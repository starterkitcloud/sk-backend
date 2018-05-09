from django.test import TestCase
from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from .views import UserInfo
from rest_framework.test import APIRequestFactory, force_authenticate
from oauth2_provider.models import Application, AccessToken
import datetime
import json

# Create your tests here.
class UserSerializerTests(TestCase):
    def setUp(self):
        self.new_user = {
            'username':'hello world',
            'password': 'password114455',
            'email':'test@testing.com'
        }
        self.user_serializer = UserSerializer()

    def test_successful_information_returns_user_instance(self):
        new_user = self.user_serializer.create(self.new_user)
        self.assertEqual(type(new_user), type(User()))

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
