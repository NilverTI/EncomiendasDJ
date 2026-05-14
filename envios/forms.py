from django import forms
from django.core.exceptions import ValidationError

from clientes.models import Cliente
from config.choices import EstadoGeneral
from envios.models import Encomienda
from rutas.models import Ruta


class EncomiendaForm(forms.ModelForm):
    class Meta:
        model = Encomienda
        fields = [
            'codigo',
            'descripcion',
            'peso_kg',
            'volumen_cm3',
            'remitente',
            'destinatario',
            'ruta',
            'costo_envio',
            'fecha_entrega_est',
            'observaciones',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ENC-2026001'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'peso_kg': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
            'volumen_cm3': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control', 'placeholder': 'Opcional'}),
            'remitente': forms.Select(attrs={'class': 'form-select'}),
            'destinatario': forms.Select(attrs={'class': 'form-select'}),
            'ruta': forms.Select(attrs={'class': 'form-select'}),
            'costo_envio': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control', 'placeholder': 'Se calculará automáticamente'}),
            'fecha_entrega_est': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Opcional'}),
        }
        labels = {
            'codigo': 'Código de encomienda',
            'descripcion': 'Descripción',
            'peso_kg': 'Peso (kg)',
            'volumen_cm3': 'Volumen (cm³)',
            'remitente': 'Remitente',
            'destinatario': 'Destinatario',
            'ruta': 'Ruta',
            'costo_envio': 'Costo de envío (S/)',
            'fecha_entrega_est': 'Fecha estimada de entrega',
            'observaciones': 'Observaciones',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['remitente'].queryset = Cliente.objects.filter(estado=EstadoGeneral.ACTIVO).order_by('apellidos', 'nombres')
        self.fields['destinatario'].queryset = Cliente.objects.filter(estado=EstadoGeneral.ACTIVO).order_by('apellidos', 'nombres')
        self.fields['ruta'].queryset = Ruta.objects.filter(estado=EstadoGeneral.ACTIVO).order_by('origen', 'destino')
        self.fields['codigo'].required = False
        self.fields['costo_envio'].required = False

    def clean(self):
        cleaned_data = super().clean()
        remitente = cleaned_data.get('remitente')
        destinatario = cleaned_data.get('destinatario')
        if remitente and destinatario and remitente == destinatario:
            raise ValidationError({
                'destinatario': 'El destinatario no puede ser el mismo que el remitente.'
            })
        return cleaned_data
