import hashlib
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['first_name', 'last_name',
                  'username', 'bio', 'email', 'role']
        model = User


class YamdbTokenObtainSerializer(TokenObtainSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField(required=False)
        self.fields['conformation_code'] = serializers.CharField()

    def validate(self, attrs):
        email = attrs[self.username_field]
        try:
            validate_email(email)
        except Exception:
            raise serializers.ValidationError("Not valid email")

        if not User.objects.filter(email=email).first():
            hash_email = hashlib.sha256(email.encode('utf-8')).hexdigest()
            print(hash_email)
            if hash_email != attrs['conformation_code']:
                raise serializers.ValidationError("credential dosen't match")
            User.objects.create_user(email=email, username='',
                                     password=attrs['conformation_code'])

        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['conformation_code'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        # Prior to Django 1.10, inactive users could be authenticated with the
        # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
        # prevents inactive users from authenticating.  App designers can still
        # allow inactive users to authenticate by opting for the new
        # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
        # users from authenticating to enforce a reasonable policy and provide
        # sensible backwards compatibility with older Django versions.
        if self.user is None or not self.user.is_active:
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        return {}


class YamdbTokenObtainPairSerializer(YamdbTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data
