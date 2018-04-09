from django.test import TestCase
from oauth2_provider.models import Application, AccessToken
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.test import APIRequestFactory
from oauth2_provider.views import TokenView
import urllib
import datetime

class OauthApplicationTestCase(TestCase):
    "should create an application for oauth authentication."
    def setUp(self):
        js_frontend = Application(
            name = "vue.js frontend",client_type = "public",
            authorization_grant_type = "Resource owner password-based").save()

    def test_oauth_application_creation(self):
        all_applications = Application.objects.all()
        self.assertEqual(len(all_applications), 1)
        self.assertEqual(all_applications[0].client_type, "public")
        self.assertEqual(all_applications[0].authorization_grant_type, "Resource owner password-based")
        self.assertEqual(all_applications[0].name, "vue.js frontend")

    def test_that_client_id_exists(self):
        all_applications = Application.objects.all()
        self.assertEqual(isinstance(all_applications[0].client_id, str), True)


class AuthTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='spencercooley', email='contact@spencercooley.com',
            password='top_secret')
        self.js_frontend = Application(
            name = "vue.js frontend",client_type = "public",
            authorization_grant_type = "Resource owner password-based").save()


    def test_should_create_auth_token(self):
        """User should create token at auth endpoint"""
        all_applications = Application.objects.all()
        app_client_id = all_applications[0].client_id
        app_client_secret = all_applications[0].client_secret
        #how do we do a request ?

        all_users = User.objects.all()

        self.assertEqual(len(all_users), 1)
        self.assertEqual(all_users[0].username, "spencercooley")
        self.assertEqual(len(all_applications), 1)

        access_token = AccessToken(
            user=all_users[0],
            application=all_applications[0],
            expires=datetime.date.today() + datetime.timedelta(days=1),
            token="testtoken1",
        ).save()
        all_tokens = AccessToken.objects.all()
        self.assertEqual(len(all_tokens), 1)
        self.assertEqual(all_tokens[0].token, "testtoken1" )
        self.assertEqual(all_tokens[0].is_expired(), False )
