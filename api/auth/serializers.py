from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework import exceptions as drf_exceptions

from djoser import utils
from djoser.conf import settings
from config import exceptions

from . import mailer

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            'id',
            'email',
            'password',
            'token',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            messages = [_(message) for message in e.messages]

            raise serializers.ValidationError({'password': messages})

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            raise exceptions.AlreadyExists(
                _('The provided email address already has an account.'))

        return user

    @staticmethod
    def perform_create(validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=['is_active'])

        return user

    def get_token(self, token):
        return default_token_generator.make_token(token)


class EmailAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        users = self.context['view'].get_users(value)
        if not users:
            raise drf_exceptions.NotFound(
                _('User account with given email does not exist.'))


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.IntegerField()
    token = serializers.CharField()

    default_error_messages = {
        'invalid_token': _('The provided token for the user is not valid.'),
        'invalid_uid': _('Invalid user id, the user does not exist.'),
    }

    def __init__(self, *args, **kwargs):
        super(UidAndTokenSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate_uid(self, value):
        try:
            uid = value
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            self.fail('invalid_uid')

        return value

    def validate(self, attrs):
        attrs = super(UidAndTokenSerializer, self).validate(attrs)
        is_token_valid = self.context['view'].token_generator.check_token(
            self.user, attrs['token'])
        if not is_token_valid:
            self.fail('invalid_token')

        return attrs


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ('auth_token', )


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        user_account = self._get_user_by_username(username)
        if not user_account:
            raise drf_exceptions.AuthenticationFailed(
                _('Unable to login with the provided credentials.'))

        self.user = authenticate(username=username, password=password)
        if not self.user:
            if user_account.is_active:
                raise drf_exceptions.AuthenticationFailed(
                    _('Unable to login with the provided credentials.'))
            else:
                raise drf_exceptions.PermissionDenied(
                    _('The account is inactive, please activate your account.'
                      ), 'notActivated')

        return attrs

    @staticmethod
    def _get_user_by_username(username):
        user = User.objects.filter(**{
            User.USERNAME_FIELD + '__iexact': username
        }).first()

        return user


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})

    def __init__(self, *args, **kwargs):
        super(PasswordSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        user = self.context['request'].user or self.user
        assert user is not None

        try:
            validate_password(attrs['new_password'], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        return super(PasswordSerializer, self).validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    re_new_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'password_mismatch': _('The two password fields did not match.'),
    }

    def validate(self, attrs):
        attrs = super(PasswordRetypeSerializer, self).validate(attrs)
        if attrs['new_password'] != attrs['re_new_password']:
            self.fail('password_mismatch')

        return attrs


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'incorrect_password':
        _('Incorrect password. Please provide your current password.'),
    }

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if not is_password_valid:
            self.fail('incorrect_password')

        return value


class ChangePasswordSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass


class ChangePasswordRetypeSerializer(PasswordRetypeSerializer,
                                     CurrentPasswordSerializer):
    pass


class ChangeEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta(object):
        model = User
        fields = ('email', )


class PasswordResetConfirmSerializer(UidAndTokenSerializer,
                                     PasswordSerializer):
    pass


class PasswordResetConfirmRetypeSerializer(UidAndTokenSerializer,
                                           PasswordRetypeSerializer):
    pass
