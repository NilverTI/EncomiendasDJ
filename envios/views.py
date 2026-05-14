import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.core.exceptions import PermissionDenied

from .forms import EncomiendaForm
from .models import Encomienda, Empleado
from config.choices import EstadoEnvio, EstadoGeneral


@login_required
def dashboard(request):
    hoy = timezone.now().date()
    context = {
        'encomiendas_activas': Encomienda.objects.activas().count(),
        'en_transito': Encomienda.objects.en_transito().count(),
        'con_retraso': Encomienda.objects.con_retraso().count(),
        'entregadas_hoy': Encomienda.objects.filter(
            estado=EstadoEnvio.ENTREGADO,
            fecha_entrega_real=hoy,
        ).count(),
        'ultimas_encomiendas': Encomienda.objects.con_relaciones()[:5],
    }
    return render(request, 'envios/dashboard.html', context)


@login_required
def encomienda_lista(request):
    qs = Encomienda.objects.con_relaciones()

    estado = request.GET.get('estado', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(
            Q(codigo__icontains=q)
            | Q(remitente__apellidos__icontains=q)
            | Q(remitente__nro_doc__icontains=q)
            | Q(destinatario__apellidos__icontains=q)
            | Q(destinatario__nro_doc__icontains=q)
        )

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page', 1)
    encomiendas_page = paginator.get_page(page_number)

    return render(request, 'envios/lista.html', {
        'encomiendas': encomiendas_page,
        'estados': EstadoEnvio.choices,
        'estado_filtro': estado,
        'query': q,
    })


@login_required
def encomienda_detalle(request, pk):
    encomienda = get_object_or_404(
        Encomienda.objects.select_related(
            'remitente', 'destinatario', 'ruta', 'empleado_registro'
        ).prefetch_related('historial'),
        pk=pk
    )
    context = {
        'encomienda': encomienda,
        'EstadoEnvio': EstadoEnvio,
    }
    return render(request, 'envios/detalle.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def encomienda_crear(request):
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            encomienda = form.save(commit=False)
            empleado = Empleado.objects.filter(estado=EstadoGeneral.ACTIVO).first()
            if not empleado:
                messages.error(request, 'No hay empleados activos registrados. Contacte al administrador.')
                return redirect('envios:crear')
            encomienda.empleado_registro = empleado
            if not encomienda.codigo:
                encomienda.codigo = f"ENC-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
            encomienda.costo_envio = encomienda.calcular_costo()
            encomienda.save()
            messages.success(request, f'Encomienda {encomienda.codigo} creada exitosamente.')
            return redirect('envios:detalle', pk=encomienda.pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = EncomiendaForm()

    context = {'form': form, 'titulo': 'Nueva Encomienda'}
    return render(request, 'envios/form.html', context)


@login_required
@require_POST
def encomienda_cambiar_estado(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)

    nuevo_estado = request.POST.get('nuevo_estado')
    if not nuevo_estado or nuevo_estado not in EstadoEnvio.values:
        messages.error(request, 'Estado no válido.')
        return redirect('envios:detalle', pk=pk)

    empleado = Empleado.objects.filter(estado=EstadoGeneral.ACTIVO).first()
    if not empleado:
        messages.error(request, 'No hay empleados activos para registrar el cambio.')
        return redirect('envios:detalle', pk=pk)

    try:
        encomienda.cambiar_estado(nuevo_estado, empleado, observacion=request.POST.get('observacion', ''))
        messages.success(request, f'Estado cambiado a "{encomienda.get_estado_display()}".')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('envios:detalle', pk=pk)


@login_required
@require_GET
def encomienda_estado_json(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)
    return JsonResponse({
        'codigo': encomienda.codigo,
        'estado': encomienda.estado,
        'display': encomienda.get_estado_display(),
        'retraso': encomienda.tiene_retraso,
        'dias': encomienda.dias_en_transito,
    })


@login_required
@require_POST
def eliminar_encomienda(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)
    if encomienda.estado not in (EstadoEnvio.PENDIENTE,):
        raise PermissionDenied('Solo se pueden eliminar encomiendas pendientes.')
    encomienda.delete()
    messages.success(request, f'Encomienda {encomienda.codigo} eliminada.')
    return redirect('envios:lista')
