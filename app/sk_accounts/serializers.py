from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail
from .helpers import TokenGenerator

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    #unique email and unique username
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), message="There is already an account associated with that email address.")])
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(), message="That username is taken")])
    def create(self, validated_data):
        try:
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                is_active=False,
            )
            user.set_password(validated_data['password'])
            user.save()

            account_activation_token = TokenGenerator()
            #make the token for the user confirmation
            confirmation_token = account_activation_token.make_token(user)
            send_mail('subject', 'http://localhost:8080/#/confirm-account?token='+confirmation_token+'&email='+user.email, 'noreply@ethspeak.com', ['contact@spencercooley.com'])
            #send this token in an email
            #blah blah blah send email using mailgun
            return user
        except Exception as e:
            return e

    class Meta:
        model = User
        write_only_fields = 'password'
        fields = ('first_name','last_name','username', 'email', 'password')


#have a periodic task that deletes all users that are inactive for more than 6 hours
#this ensures that anyone that is doing some bullshit will have their fake attempts deleted from the system everyday
