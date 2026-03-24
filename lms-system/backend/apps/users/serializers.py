"""
User serializers for LMS System.

This module contains serializers for user registration,
authentication, and profile management.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import PasswordResetToken, RefreshToken

User = get_user_model()


# === CHUNK: USER_SERIALIZERS_V1 [USER_MANAGEMENT] ===
# Описание: Сериализаторы для пользователей, аутентификации и смены пароля.
# Dependencies: USER_MODEL_V1


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# [START_USER_CREATE_SERIALIZER]
# ANCHOR: USER_CREATE_SERIALIZER
# @PreConditions:
# - data содержит email, password, password_confirm, full_name, role
# @PostConditions:
# - при валидных данных создаёт нового пользователя
# - пароль хешируется автоматически
# PURPOSE: Сериализатор для создания новых пользователей с валидацией пароля.
class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'full_name', 'role'
        ]
    
    # [START_VALIDATE_PASSWORDS]
    # ANCHOR: VALIDATE_PASSWORDS
    # @PreConditions:
    # - attrs содержит password и password_confirm
    # @PostConditions:
    # - при несовпадении паролей выбрасывает ValidationError
    # - при совпадении возвращает attrs
    # PURPOSE: Валидация совпадения паролей при регистрации.
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _('Пароли не совпадают.')
            })
        return attrs
    # [END_VALIDATE_PASSWORDS]
    
    # [START_CREATE_USER]
    # ANCHOR: CREATE_USER
    # @PreConditions:
    # - validated_data содержит email, password, full_name, role
    # @PostConditions:
    # - создаёт нового пользователя с хешированным паролем
    # - возвращает созданный экземпляр User
    # PURPOSE: Создание пользователя через UserManager.
    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
    # [END_CREATE_USER]


# [END_USER_CREATE_SERIALIZER]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ['full_name', 'role', 'is_active']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True,
    )


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh."""
    
    refresh = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)


# [START_PASSWORD_RESET_CONFIRM_SERIALIZER]
# ANCHOR: PASSWORD_RESET_CONFIRM_SERIALIZER
# @PreConditions:
# - data содержит token, new_password, new_password_confirm
# @PostConditions:
# - при валидных данных возвращает attrs для смены пароля
# PURPOSE: Сериализатор для подтверждения сброса пароля.
class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password],
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
    )
    
    # [START_VALIDATE_NEW_PASSWORDS]
    # ANCHOR: VALIDATE_NEW_PASSWORDS
    # @PreConditions:
    # - attrs содержит new_password и new_password_confirm
    # @PostConditions:
    # - при несовпадении паролей выбрасывает ValidationError
    # - при совпадении возвращает attrs
    # PURPOSE: Валидация совпадения новых паролей при сбросе.
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('Пароли не совпадают.')
            })
        return attrs
    # [END_VALIDATE_NEW_PASSWORDS]


# [END_PASSWORD_RESET_CONFIRM_SERIALIZER]


# [START_CHANGE_PASSWORD_SERIALIZER]
# ANCHOR: CHANGE_PASSWORD_SERIALIZER
# @PreConditions:
# - data содержит old_password, new_password, new_password_confirm
# - request.user аутентифицирован
# @PostConditions:
# - при верном old_password и совпадении новых паролей возвращает attrs
# PURPOSE: Сериализатор для смены пароля аутентифицированным пользователем.
class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True,
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password],
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
    )
    
    # [START_VALIDATE_OLD_PASSWORD]
    # ANCHOR: VALIDATE_OLD_PASSWORD
    # @PreConditions:
    # - value содержит старый пароль
    # - request.user аутентифицирован
    # @PostConditions:
    # - при неверном пароле выбрасывает ValidationError
    # - при верном пароле возвращает value
    # PURPOSE: Проверка текущего пароля пользователя.
    def validate_old_password(self, value):
        """Validate that old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Неверный текущий пароль.'))
        return value
    # [END_VALIDATE_OLD_PASSWORD]
    
    # [START_VALIDATE_CHANGE_PASSWORDS]
    # ANCHOR: VALIDATE_CHANGE_PASSWORDS
    # @PreConditions:
    # - attrs содержит new_password и new_password_confirm
    # @PostConditions:
    # - при несовпадении паролей выбрасывает ValidationError
    # - при совпадении возвращает attrs
    # PURPOSE: Валидация совпадения новых паролей при смене.
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('Пароли не совпадают.')
            })
        return attrs
    # [END_VALIDATE_CHANGE_PASSWORDS]


# [END_CHANGE_PASSWORD_SERIALIZER]


# === END_CHUNK: USER_SERIALIZERS_V1 ===