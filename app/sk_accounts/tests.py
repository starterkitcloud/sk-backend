from django.test import TestCase
from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from .views import UserInfo, ConfirmUserAccount, RequestResetPassword, ResetPassword
from rest_framework.test import APIRequestFactory, force_authenticate
from oauth2_provider.models import Application, AccessToken
import datetime
import json
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .helpers import TokenGenerator



# Create your tests here.
class UserSerializerTests(TestCase):
    def setUp(self):
        self.new_user = {
            'username':'hello world',
            'password': 'password114455',
            'email':'test@testing.com'
        }
        self.user_serializer = UserSerializer()

    def test_user_should_not_be_active_on_creation(self):
        new_user = self.user_serializer.create(self.new_user)
        self.assertEqual(new_user.is_active, False)

    def test_should_not_create_duplicate_email_or_username(self):
        new_user = UserSerializer().create(self.new_user)
        repeat_user = UserSerializer().create(self.new_user)
        self.assertEqual(type(new_user), type(User()))
        self.assertEqual(type(repeat_user), IntegrityError)

    def test_correct_fields_exist(self):
        new_user = UserSerializer().create(self.new_user)
        serializer_data = UserSerializer(instance=new_user).data.keys()
        self.assertEqual(set(serializer_data), set(['username', 'password','email', 'first_name', 'last_name']))

# test user summary endpoint
class NeedsAuthTestCase(TestCase):
    #has a setup that creates a single user, an oauth app, and a auth token.
    def setUp(self):
        self.user = User.objects.create_user(
            username='spencercooley', email='contact@spencercooley.com',
            password='top_secret')

        the_application = Application(
            name = "javascript",client_type = "public",
            authorization_grant_type = "Resource owner password-based", user=self.user).save()
        self.oauth_app = Application.objects.get(name="javascript")
        access_token = AccessToken.objects.create(
            user=self.user,
            scope="read write",
            expires=datetime.date.today() + datetime.timedelta(days=1),
            token="secret-access-token-key",
            application=self.oauth_app
        )
        self.access_token = AccessToken.objects.get(user=self.user)
        self.factory = APIRequestFactory()
        self.auth_header = 'Bearer {}'.format(self.access_token)

class TestUserInfoEndpoint(NeedsAuthTestCase):
    def test_user_info_requires_auth(self):
        request_with_auth = self.factory.get('v1/user_summary', HTTP_AUTHORIZATION=self.auth_header)
        request_without_auth = self.factory.get('v1/user_summary')
        view = UserInfo.as_view()
        response_with_auth = view(request_with_auth)
        response_without_auth = view(request_without_auth)
        self.assertEqual(response_with_auth.status_code, 200)
        self.assertEqual(response_without_auth.status_code, 401)

    def test_user_info_returns_the_correct_data(self):
        request_with_auth = self.factory.get('v1/user_summary', HTTP_AUTHORIZATION=self.auth_header)
        view = UserInfo.as_view()
        response_with_auth = view(request_with_auth)
        response_as_dict = json.loads(response_with_auth.render().content)
        self.assertEqual(response_as_dict['email'], 'contact@spencercooley.com')
        self.assertEqual(response_as_dict['username'], 'spencercooley')



class TestUserConfirmationEndpoint(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='spencercooley', email='contact@spencercooley.com',
            password='top_secret', is_active=False)

    def test_that_user_is_inactive_on_creation(self):
        self.assertEqual(self.user.is_active, False)

    def test_that_the_confirmation_view_switches_user_to_active(self):
        self.assertEqual(self.user.is_active, False)
        account_activation_token = TokenGenerator()
        confirmation_token = account_activation_token.make_token(self.user)
        request = self.factory.get('v1/confirm_account?token={}&email={}'.format(confirmation_token, self.user.email))
        view = ConfirmUserAccount.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200 )
        #user should be updated now
        updated_user = User.objects.get(username='spencercooley')
        self.assertEqual(updated_user.is_active, True)


# class TestResetPasswordEndpoint(TestCase):
#     def setUp(self):
#         self.factory = APIRequestFactory()
#         self.view = ResetPassword.as_view()
#         self.user = self.user_inactive = User.objects.create_user(
#             username='spencercooley1', email='contact@spencercooley1.com',
#             password='top_secret', is_active=True)
#
#         self.token = TokenGenerator().make_token(self.user)
#
#     def test_password_is_reset_when_token_and_email_present_and_valid(self):
#         data = {
#             'email': self.user.email,
#             'token': self.token,
#             'new_password': 'new_top_secret'
#         }
#         request = self.factory.post('v1/reset-password', data=data)
#         response = self.view(request)
#
#         self.assertEqual(response.status_code, 200)


class TestResetPasswordRequestEndpoint(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user_inactive = User.objects.create_user(
            username='spencercooley1', email='contact@spencercooley1.com',
            password='top_secret', is_active=False)

        self.user_active = User.objects.create_user(
            username='spencercooley2', email='contact@spencercooley2.com',
            password='top_secret', is_active=True)
        self.view = RequestResetPassword.as_view()

    def test_endpoint_returns_200_as_active_or_inactive(self):
        request_active = self.factory.get('v1/request-password-reset?email={}'
                                                .format(self.user_active.email))
        request_inactive = self.factory.get('v1/request-password-reset?email={}'
                                                .format(self.user_inactive.email))

        response_active = self.view(request_active)
        response_inactive = self.view(request_inactive)

        self.assertEqual(response_active.status_code, 200)
        self.assertEqual(response_inactive.status_code, 200)

    def test_should_require_an_email_parameter(self):
        #email in request.GET is required
        request_with_no_email = self.factory.get('v1/request-password-reset')
        response = self.view(request_with_no_email)

        self.assertEqual(response.status_code, 400)

    def test_should_still_return_200_even_if_user_does_not_exist(self):
        request_false_email = self.factory.get('v1/request-password-reset?email={}'
                                            .format('email@doesnotexist.com'))
        response = self.view(request_false_email)
        self.assertEqual(response.status_code, 200)
