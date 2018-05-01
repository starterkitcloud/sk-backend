from rest_framework import routers, viewsets, permissions
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
import json
from rest_framework.permissions import AllowAny, IsAdminUser

class MixedPermissionModelViewSet(viewsets.ModelViewSet):
   '''
   Mixed permission base model allowing for action level
   permission control. Subclasses may define their permissions
   by creating a 'permission_classes_by_action' variable.

   Example:
   permission_classes_by_action = {'list': [AllowAny],
                                   'create': [IsAdminUser]}
   '''

   permission_classes_by_action = {'create': [AllowAny],
                                   'list': [IsAdminUser]}
   def get_permissions(self):
      try:
        # return permission_classes depending on `action`
        return [permission() for permission in self.permission_classes_by_action[self.action]]
      except KeyError:
        # action is not set return default permission_classes
        return [permission() for permission in self.permission_classes]


class UserViewSet(MixedPermissionModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer



class UserInfo(APIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    def get(self, request, format=None):
        """
        Return logged in user details.
        """
        data = {
            'id': self.request.user.id,
            'email': self.request.user.email,
            'username': self.request.user.username,
        }
        return Response(data)
