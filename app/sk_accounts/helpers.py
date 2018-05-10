
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )

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
