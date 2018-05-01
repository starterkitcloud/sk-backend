from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


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
        return user

    class Meta:
        model = User
        write_only_fields = 'password'
        fields = ('first_name','last_name','username', 'email', 'password')
