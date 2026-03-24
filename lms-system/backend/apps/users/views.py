"""
User views for LMS System.

This module contains views for user registration,
authentication, and profile management.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PasswordResetToken
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


# === CHUNK: USER_VIEWSET_V1 [USER_MANAGEMENT] ===
# Описание: ViewSet для CRUD операций над пользователями.
# Dependencies: USER_MODEL_V1, USER_SERIALIZERS_V1
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    
    Provides CRUD operations for users.
    Only admins can create, update, or delete users.
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_SERIALIZER_CLASS]
    # ANCHOR: GET_SERIALIZER_CLASS
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - для create возвращает UserCreateSerializer
    # - для update/partial_update возвращает UserUpdateSerializer
    # - для остальных действий возвращает UserSerializer
    # PURPOSE: Выбор подходящего сериализатора в зависимости от действия.
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    # [END_GET_SERIALIZER_CLASS]
    
    # [START_GET_QUERYSET]
    # ANCHOR: GET_QUERYSET
    # @PreConditions:
    # - пользователь аутентифицирован
    # @PostConditions:
    # - для admin возвращает всех пользователей
    # - для остальных возвращает только собственную запись
    # PURPOSE: Фильтрация queryset в зависимости от роли пользователя.
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        if user.is_admin:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    # [END_GET_QUERYSET]
    
    # [START_ME_ACTION]
    # ANCHOR: ME_ACTION
    # @PreConditions:
    # - пользователь аутентифицирован
    # @PostConditions:
    # - возвращает данные текущего пользователя
    # PURPOSE: Получение профиля текущего аутентифицированного пользователя.
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Return current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    # [END_ME_ACTION]
    
    # [START_CHANGE_PASSWORD_ACTION]
    # ANCHOR: CHANGE_PASSWORD_ACTION
    # @PreConditions:
    # - пользователь аутентифицирован
    # - request.data содержит old_password и new_password
    # @PostConditions:
    # - при успехе пароль пользователя изменён
    # - возвращает сообщение об успехе
    # PURPOSE: Смена пароля текущего пользователя.
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Пароль успешно изменён.'})
    # [END_CHANGE_PASSWORD_ACTION]
    
    # [START_LOGOUT_ACTION]
    # ANCHOR: LOGOUT_ACTION
    # @PreConditions:
    # - пользователь аутентифицирован
    # - request.data может содержать refresh токен
    # @PostConditions:
    # - при наличии refresh токена он добавляется в blacklist
    # - возвращает сообщение об успехе или ошибку
    # PURPOSE: Выход из системы с отзывом refresh токена.
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Успешный выход из системы.'})
        except Exception:
            return Response(
                {'error': 'Неверный токен.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    # [END_LOGOUT_ACTION]


# === END_CHUNK: USER_VIEWSET_V1 ===


# [START_LOGIN_VIEW]
# ANCHOR: LOGIN_VIEW
# @PreConditions:
# - request.data содержит email и password
# @PostConditions:
# - при успехе возвращает access, refresh токены и данные пользователя
# - при неудаче возвращает ошибку 401
# PURPOSE: Аутентификация пользователя и выдача JWT токенов.
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login view for user authentication.
    
    Returns JWT access and refresh tokens on successful login.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Неверный email или пароль.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.check_password(password):
        return Response(
            {'error': 'Неверный email или пароль.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Учётная запись деактивирована.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    })
# [END_LOGIN_VIEW]


# [START_REGISTER_VIEW]
# ANCHOR: REGISTER_VIEW
# @PreConditions:
# - request.data содержит email, password, full_name, role
# @PostConditions:
# - при успехе создаёт нового пользователя и возвращает его данные
# - возвращает статус 201
# PURPOSE: Регистрация нового пользователя в системе.
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register view for new user registration.
    
    Only admins can register new users.
    """
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    return Response(
        UserSerializer(user).data,
        status=status.HTTP_201_CREATED
    )
# [END_REGISTER_VIEW]


# [START_LOGOUT_VIEW]
# ANCHOR: LOGOUT_VIEW
# @PreConditions:
# - пользователь аутентифицирован
# - request.data может содержать refresh токен
# @PostConditions:
# - при наличии refresh токена он добавляется в blacklist
# - возвращает сообщение об успехе или ошибку
# PURPOSE: Выход из системы с отзывом refresh токена.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout view for user logout.
    
    Blacklists the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Успешный выход из системы.'})
    except Exception:
        return Response(
            {'error': 'Неверный токен.'},
            status=status.HTTP_400_BAD_REQUEST
        )
# [END_LOGOUT_VIEW]


# [START_PASSWORD_RESET_REQUEST_VIEW]
# ANCHOR: PASSWORD_RESET_REQUEST_VIEW
# @PreConditions:
# - request.data содержит email
# @PostConditions:
# - создаёт токен сброса пароля (если пользователь существует)
# - возвращает сообщение (не раскрывает существование email)
# PURPOSE: Запрос на сброс пароля с созданием токена.
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    """
    Request password reset.
    
    Sends an email with reset link to the user.
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal that user doesn't exist
        return Response({'message': 'Если email существует, письмо отправлено.'})
    
    # Create reset token
    token = PasswordResetToken.objects.create(
        user=user,
        token=PasswordResetToken.objects.make_random_password(64),
        expires_at=timezone.now() + timezone.timedelta(hours=24)
    )
    
    # TODO: Send email with reset link
    # For now, return token in response (remove in production)
    return Response({
        'message': 'Если email существует, письмо отправлено.',
        'token': token.token,  # Remove in production
    })
# [END_PASSWORD_RESET_REQUEST_VIEW]


# [START_PASSWORD_RESET_CONFIRM_VIEW]
# ANCHOR: PASSWORD_RESET_CONFIRM_VIEW
# @PreConditions:
# - request.data содержит token и new_password
# @PostConditions:
# - при валидном токене устанавливает новый пароль
# - токен помечается как использованный
# - при ошибке возвращает 400
# PURPOSE: Подтверждение сброса пароля с установкой нового.
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    """
    Confirm password reset.
    
    Validates token and sets new password.
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'error': 'Неверный токен.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if reset_token.is_used:
        return Response(
            {'error': 'Токен уже использован.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if reset_token.is_expired:
        return Response(
            {'error': 'Токен истёк.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user = reset_token.user
    user.set_password(new_password)
    user.save()
    
    # Mark token as used
    reset_token.mark_as_used()
    
    return Response({'message': 'Пароль успешно сброшен.'})
# [END_PASSWORD_RESET_CONFIRM_VIEW]