from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.serializers import RegisterSerializer


class UserRegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()
