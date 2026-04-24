import re

from django.core.exceptions import ValidationError


CODIGO_ENCOMIENDA_RE = re.compile(r"^ENC-[A-Z0-9-]+$")


def validar_peso_positivo(value):
    if value <= 0:
        raise ValidationError(f"El peso debe ser mayor a 0. Recibio: {value} kg")


def validar_codigo_encomienda(value):
    if not CODIGO_ENCOMIENDA_RE.match((value or "").strip().upper()):
        raise ValidationError(
            "El codigo de encomienda debe comenzar con ENC- y usar solo letras, numeros o guiones."
        )


def validar_nro_doc_dni(value):
    documento = (value or "").strip()
    if not documento.isdigit() or len(documento) != 8:
        raise ValidationError(
            "El DNI debe contener exactamente 8 digitos numericos."
        )
