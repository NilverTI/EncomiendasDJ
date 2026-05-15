from rest_framework.permissions import BasePermission, SAFE_METHODS
from envios.models import Empleado


class EsEmpleadoActivo(BasePermission):
    message = "Solo empleados activos tienen acceso a esta API."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return Empleado.objects.filter(
            email=request.user.email, estado=1
        ).exists()


class EsPropietarioOAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.empleado_registro.email == request.user.email


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(obj, "cliente_correo") and obj.cliente_correo == request.user.email
