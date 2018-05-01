from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    #unique email and unique username

    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), message="There is already an account associated with that email address.")])

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=False,
        )
        user.set_password(validated_data['password'])
        user.save()

        #make the token for the user confirmation
        confirmation_token = account_activation_token.make_token(user)
        #send this token in an email
        #blah blah blah send email using mailgun



        print(confirmation_token)
        return user

    class Meta:
        model = User
        write_only_fields = 'password'
        fields = ('first_name','last_name','username', 'email', 'password')




#make another endpoint for confirming the user clicked through the link
#checks if token is valid.... then you can do whatever you want

# if user is not None and account_activation_token.check_token(user, token):
    #make the user active in the system

    
#have a periodic task that deletes all users that are inactive for more than 6 hours
#this ensures that anyone that is doing some bullshit will have their fake attempts deleted from the system everyday
