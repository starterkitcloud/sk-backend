from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
import json
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.test import APIRequestFactory
from .helpers import MixedPermissionModelViewSet, TokenGenerator
from rest_framework import permissions
from django.utils.datastructures import MultiValueDictKeyError
from django.core.mail import send_mail


class UserViewSet(MixedPermissionModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ConfirmUserAccount(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        """
        Return true if valid token is in parameter data
        Return error with message if invalid token is in the parameter data
        """
        user = User.objects.get(email=request.GET['email'])
        token = request.GET['token']
        account_activation_token = TokenGenerator()
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            data = {'message':'user is now active'}
            return Response(data)
        else:
            data = {'message': 'This url is not valid.'}
            return Response(data)

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

class ResetPassword(APIView):
    """
    resets the passsword
    """
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        print(request.POST)


class RequestResetPassword(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        try:
            try:
                user = User.objects.get(email=request.GET['email'])
            except User.DoesNotExist:
                user = None
            if user is not None:
                account_activation_token = TokenGenerator()
                reset_token = account_activation_token.make_token(user)
                #send email with url to reset password screen.
                send_mail('subject',
                'http://localhost:8080/#/reset-password?token={}&email={}'
                                        .format(reset_token, user.email),
                                        'noreply@ethspeak.com',
                                        ['contact@spencercooley.com'])

            data = {'message':'You should receive an email with reset instructions if this email is associated with an account in our system.'}
            return Response(data)
        except MultiValueDictKeyError:
            data = {'message':'You must provide an email address to reset your password.'}
            return Response(data=data, status=400)
