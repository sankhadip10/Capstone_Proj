from rest_framework import generics

from DjangoProject.models import User
from DjangoProject.serializer import UserSerializer


class UserListCreateApiView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer