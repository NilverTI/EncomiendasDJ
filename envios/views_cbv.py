from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from config.choices import EstadoEnvio
from envios.forms import EncomiendaForm
from envios.models import Encomienda, Empleado
from envios.querysets import EncomiendaQuerySet


class EncomiendaListView(LoginRequiredMixin, ListView):
    model = Encomienda
    template_name = 'envios/lista.html'
    context_object_name = 'encomiendas'
    paginate_by = 15
    ordering = ['-fecha_registro']

    def get_queryset(self):
        qs = Encomienda.objects.con_relaciones()
        estado = self.request.GET.get('estado')
        q = self.request.GET.get('q')
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
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estados'] = EstadoEnvio.choices
        ctx['estado_filtro'] = self.request.GET.get('estado', '')
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class EncomiendaDetailView(LoginRequiredMixin, DetailView):
    model = Encomienda
    template_name = 'envios/detalle.html'
    context_object_name = 'encomienda'

    def get_queryset(self):
        return Encomienda.objects.con_relaciones()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['EstadoEnvio'] = EstadoEnvio
        return ctx


class EncomiendaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Encomienda
    form_class = EncomiendaForm
    template_name = 'envios/form.html'
    success_message = 'Encomienda %(codigo)s creada correctamente.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva Encomienda'
        return ctx

    def get_success_url(self):
        return reverse_lazy('envios:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        empleado = Empleado.objects.filter(estado=1).first()
        if empleado:
            form.instance.empleado_registro = empleado
        return super().form_valid(form)


class EncomiendaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Encomienda
    form_class = EncomiendaForm
    template_name = 'envios/form.html'
    success_message = 'Encomienda %(codigo)s actualizada correctamente.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar {self.object.codigo}'
        return ctx

    def get_success_url(self):
        return reverse_lazy('envios:detalle', kwargs={'pk': self.object.pk})
