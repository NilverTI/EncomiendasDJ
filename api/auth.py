from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from api.throttles import LoginRateThrottle
from envios.models import Empleado


class EncomiendaTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        try:
            emp = Empleado.objects.get(email=user.email)
            token["empleado_id"] = emp.id
            token["empleado_cod"] = emp.codigo
            token["cargo"] = emp.cargo
        except Empleado.DoesNotExist:
            pass
        return token


class EncomiendaTokenView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]
    serializer_class = EncomiendaTokenSerializer
