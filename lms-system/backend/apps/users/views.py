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

from core.utils import log_line
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
# [START_USER_VIEWSET]
"""
ANCHOR: USER_VIEWSET
PURPOSE: ViewSet для CRUD операций над пользователями.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет CRUD операции для пользователей
- только admin может создавать, обновлять, удалять пользователей

@Invariants:
- пользователь видит только свою запись (кроме admin)

@SideEffects:
- операции с БД через ORM

@ForbiddenChanges:
- permission_classes = [IsAuthenticated]
"""
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
    """
    ANCHOR: GET_SERIALIZER_CLASS
    PURPOSE: Выбор подходящего сериализатора в зависимости от действия.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - для create возвращает UserCreateSerializer
    - для update/partial_update возвращает UserUpdateSerializer
    - для остальных действий возвращает UserSerializer
    
    @Invariants:
    - всегда возвращает валидный serializer class
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - логика выбора сериализатора по action
    """
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        log_line("users", "DEBUG", "get_serializer_class", "GET_SERIALIZER_CLASS", "ENTRY", {
            "action": self.action,
        })
        
        if self.action == 'create':
            serializer = UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            serializer = UserUpdateSerializer
        else:
            serializer = UserSerializer
        
        log_line("users", "DEBUG", "get_serializer_class", "GET_SERIALIZER_CLASS", "EXIT", {
            "serializer": serializer.__name__,
        })
        
        return serializer
    # [END_GET_SERIALIZER_CLASS]
    
    # [START_GET_QUERYSET]
    """
    ANCHOR: GET_QUERYSET
    PURPOSE: Фильтрация queryset в зависимости от роли пользователя.
    
    @PreConditions:
    - пользователь аутентифицирован
    
    @PostConditions:
    - для admin возвращает всех пользователей
    - для остальных возвращает только собственную запись
    
    @Invariants:
    - всегда возвращает QuerySet
    
    @SideEffects:
    - чтение из БД
    
    @ForbiddenChanges:
    - проверка user.is_admin
    """
    def get_queryset(self):
        """Filter queryset based on user role."""
        log_line("users", "DEBUG", "get_queryset", "GET_QUERYSET", "ENTRY", {})
        
        user = self.request.user
        if user.is_admin:
            queryset = User.objects.all()
            log_line("users", "DEBUG", "get_queryset", "GET_QUERYSET", "BRANCH", {
                "branch": "admin_all_users",
            })
        else:
            queryset = User.objects.filter(id=user.id)
            log_line("users", "DEBUG", "get_queryset", "GET_QUERYSET", "BRANCH", {
                "branch": "own_record_only",
            })
        
        log_line("users", "DEBUG", "get_queryset", "GET_QUERYSET", "EXIT", {
            "count": queryset.count(),
        })
        
        return queryset
    # [END_GET_QUERYSET]
    
    # [START_ME_ACTION]
    """
    ANCHOR: ME_ACTION
    PURPOSE: Получение профиля текущего аутентифицированного пользователя.
    
    @PreConditions:
    - пользователь аутентифицирован
    
    @PostConditions:
    - возвращает данные текущего пользователя
    
    @Invariants:
    - всегда возвращает Response с UserSerializer data
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - возвращает request.user
    """
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Return current user profile."""
        log_line("users", "DEBUG", "me", "ME_ACTION", "ENTRY", {
            "user_id": request.user.id,
        })
        
        serializer = self.get_serializer(request.user)
        
        log_line("users", "DEBUG", "me", "ME_ACTION", "EXIT", {
            "user_id": request.user.id,
        })
        
        return Response(serializer.data)
    # [END_ME_ACTION]
    
    # [START_CHANGE_PASSWORD_ACTION]
    """
    ANCHOR: CHANGE_PASSWORD_ACTION
    PURPOSE: Смена пароля текущего пользователя.
    
    @PreConditions:
    - пользователь аутентифицирован
    - request.data содержит old_password и new_password
    
    @PostConditions:
    - при успехе пароль пользователя изменён
    - возвращает сообщение об успехе
    
    @Invariants:
    - старый пароль проверяется через serializer validation
    - новый пароль хешируется
    
    @SideEffects:
    - обновление password в БД
    - логирование операции
    
    @ForbiddenChanges:
    - использование set_password для хеширования
    """
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user password."""
        log_line("users", "DEBUG", "change_password", "CHANGE_PASSWORD_ACTION", "ENTRY", {
            "user_id": request.user.id,
        })
        
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        log_line("users", "INFO", "change_password", "CHANGE_PASSWORD_ACTION", "STATE_CHANGE", {
            "action": "password_changed",
            "user_id": user.id,
        })
        log_line("users", "DEBUG", "change_password", "CHANGE_PASSWORD_ACTION", "EXIT", {
            "result": "success",
        })
        
        return Response({'message': 'Пароль успешно изменён.'})
    # [END_CHANGE_PASSWORD_ACTION]
    
    # [START_LOGOUT_ACTION]
    """
    ANCHOR: LOGOUT_ACTION
    PURPOSE: Выход из системы с отзывом refresh токена.
    
    @PreConditions:
    - пользователь аутентифицирован
    - request.data может содержать refresh токен
    
    @PostConditions:
    - при наличии refresh токена он добавляется в blacklist
    - возвращает сообщение об успехе или ошибку
    
    @Invariants:
    - ошибки не раскрывают детали токена
    
    @SideEffects:
    - добавление токена в blacklist
    - логирование операции
    
    @ForbiddenChanges:
    - обработка исключений с возвратом общей ошибки
    """
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user by blacklisting refresh token."""
        log_line("users", "DEBUG", "logout", "LOGOUT_ACTION", "ENTRY", {
            "user_id": request.user.id,
        })
        
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                log_line("users", "INFO", "logout", "LOGOUT_ACTION", "STATE_CHANGE", {
                    "action": "token_blacklisted",
                    "user_id": request.user.id,
                })
            
            log_line("users", "DEBUG", "logout", "LOGOUT_ACTION", "EXIT", {
                "result": "success",
            })
            return Response({'message': 'Успешный выход из системы.'})
        except Exception as e:
            log_line("users", "WARN", "logout", "LOGOUT_ACTION", "ERROR", {
                "reason": "invalid_token",
            })
            log_line("users", "DEBUG", "logout", "LOGOUT_ACTION", "EXIT", {
                "result": "error",
            })
            return Response(
                {'error': 'Неверный токен.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    # [END_LOGOUT_ACTION]
# [END_USER_VIEWSET]


# === END_CHUNK: USER_VIEWSET_V1 ===


# [START_LOGIN_VIEW]
"""
ANCHOR: LOGIN_VIEW
PURPOSE: Аутентификация пользователя и выдача JWT токенов.

@PreConditions:
- request.data содержит email и password

@PostConditions:
- при успехе возвращает access, refresh токены и данные пользователя
- при неудаче возвращает ошибку 401

@Invariants:
- сообщение об ошибке не раскрывает существование email
- неправильный пароль и несуществующий email дают одинаковую ошибку

@SideEffects:
- генерация JWT токенов
- логирование операции

@ForbiddenChanges:
- одинаковое сообщение для неверного email и пароля (безопасность)
"""
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login view for user authentication.
    
    Returns JWT access and refresh tokens on successful login.
    """
    log_line("users", "DEBUG", "login_view", "LOGIN_VIEW", "ENTRY", {})
    
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    log_line("users", "DEBUG", "login_view", "LOGIN_VIEW", "CHECK", {
        "check": "credentials",
        "email": email,
    })
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        log_line("users", "WARN", "login_view", "LOGIN_VIEW", "DECISION", {
            "decision": "user_not_found",
            "email": email,
        })
        log_line("users", "DEBUG", "login_view", "LOGIN_VIEW", "EXIT", {
            "result": "unauthorized",
        })
        return Response(
            {'error': 'Неверный email или пароль.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.check_password(password):
        log_line("users", "WARN", "login_view", "LOGIN_VIEW", "DECISION", {
            "decision": "invalid_password",
            "email": email,
        })
        log_line("users", "DEBUG", "login_view", "LOGIN_VIEW", "EXIT", {
            "result": "unauthorized",
        })
        return Response(
            {'error': 'Неверный email или пароль.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        log_line("users", "WARN", "login_view", "LOGIN_VIEW", "DECISION", {
            "decision": "account_deactivated",
            "email": email,
        })
        log_line("users", "DEBUG", "login_view", "LOGIN_VIEW", "EXIT", {
            "result": "unauthorized",
        })
        return Response(
            {'error': 'Учётная запись деактивирована.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    
    log_line("users", "INFO", "login_view", "LOGIN_VIEW", "STATE_CHANGE", {
        "action": "user_logged_in",
        "user_id": user.id,
        "email": email,
    })
    log_line("users", "DEBUG", "login_view", "LOGIN_VIEW", "EXIT", {
        "result": "success",
        "user_id": user.id,
    })
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    })
# [END_LOGIN_VIEW]


# [START_REGISTER_VIEW]
"""
ANCHOR: REGISTER_VIEW
PURPOSE: Регистрация нового пользователя в системе.

@PreConditions:
- request.data содержит email, password, full_name, role

@PostConditions:
- при успехе создаёт нового пользователя и возвращает его данные
- возвращает статус 201

@Invariants:
- пароль хешируется через serializer.save()

@SideEffects:
- создание записи User в БД
- логирование операции

@ForbiddenChanges:
- статус 201 CREATED
"""
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register view for new user registration.
    
    Only admins can register new users.
    """
    log_line("users", "DEBUG", "register_view", "REGISTER_VIEW", "ENTRY", {})
    
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    log_line("users", "INFO", "register_view", "REGISTER_VIEW", "STATE_CHANGE", {
        "action": "user_registered",
        "user_id": user.id,
        "email": user.email,
    })
    log_line("users", "DEBUG", "register_view", "REGISTER_VIEW", "EXIT", {
        "result": "success",
        "user_id": user.id,
    })
    
    return Response(
        UserSerializer(user).data,
        status=status.HTTP_201_CREATED
    )
# [END_REGISTER_VIEW]


# [START_LOGOUT_VIEW]
"""
ANCHOR: LOGOUT_VIEW
PURPOSE: Выход из системы с отзывом refresh токена.

@PreConditions:
- пользователь аутентифицирован
- request.data может содержать refresh токен

@PostConditions:
- при наличии refresh токена он добавляется в blacklist
- возвращает сообщение об успехе или ошибку

@Invariants:
- ошибки не раскрывают детали токена

@SideEffects:
- добавление токена в blacklist
- логирование операции

@ForbiddenChanges:
- обработка исключений с возвратом общей ошибки
"""
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout view for user logout.
    
    Blacklists the refresh token.
    """
    log_line("users", "DEBUG", "logout_view", "LOGOUT_VIEW", "ENTRY", {
        "user_id": request.user.id,
    })
    
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            log_line("users", "INFO", "logout_view", "LOGOUT_VIEW", "STATE_CHANGE", {
                "action": "token_blacklisted",
                "user_id": request.user.id,
            })
        
        log_line("users", "DEBUG", "logout_view", "LOGOUT_VIEW", "EXIT", {
            "result": "success",
        })
        return Response({'message': 'Успешный выход из системы.'})
    except Exception:
        log_line("users", "WARN", "logout_view", "LOGOUT_VIEW", "ERROR", {
            "reason": "invalid_token",
        })
        log_line("users", "DEBUG", "logout_view", "LOGOUT_VIEW", "EXIT", {
            "result": "error",
        })
        return Response(
            {'error': 'Неверный токен.'},
            status=status.HTTP_400_BAD_REQUEST
        )
# [END_LOGOUT_VIEW]


# [START_PASSWORD_RESET_REQUEST_VIEW]
"""
ANCHOR: PASSWORD_RESET_REQUEST_VIEW
PURPOSE: Запрос на сброс пароля с созданием токена.

@PreConditions:
- request.data содержит email

@PostConditions:
- создаёт токен сброса пароля (если пользователь существует)
- возвращает сообщение (не раскрывает существование email)

@Invariants:
- сообщение всегда одинаковое (защита от перебора email)

@SideEffects:
- создание PasswordResetToken в БД (если пользователь существует)
- логирование операции

@ForbiddenChanges:
- сообщение "Если email существует, письмо отправлено." всегда одинаковое
"""
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    """
    Request password reset.
    
    Sends an email with reset link to the user.
    """
    log_line("users", "DEBUG", "password_reset_request_view", "PASSWORD_RESET_REQUEST_VIEW", "ENTRY", {})
    
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email)
        
        token = PasswordResetToken.objects.create(
            user=user,
            token=PasswordResetToken.objects.make_random_password(64),
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        log_line("users", "INFO", "password_reset_request_view", "PASSWORD_RESET_REQUEST_VIEW", "STATE_CHANGE", {
            "action": "reset_token_created",
            "user_id": user.id,
        })
        
        log_line("users", "DEBUG", "password_reset_request_view", "PASSWORD_RESET_REQUEST_VIEW", "EXIT", {
            "result": "token_created",
        })
        
        return Response({
            'message': 'Если email существует, письмо отправлено.',
            'token': token.token,
        })
    except User.DoesNotExist:
        log_line("users", "DEBUG", "password_reset_request_view", "PASSWORD_RESET_REQUEST_VIEW", "BRANCH", {
            "branch": "user_not_found",
        })
        log_line("users", "DEBUG", "password_reset_request_view", "PASSWORD_RESET_REQUEST_VIEW", "EXIT", {
            "result": "not_found",
        })
        
        return Response({'message': 'Если email существует, письмо отправлено.'})
# [END_PASSWORD_RESET_REQUEST_VIEW]


# [START_PASSWORD_RESET_CONFIRM_VIEW]
"""
ANCHOR: PASSWORD_RESET_CONFIRM_VIEW
PURPOSE: Подтверждение сброса пароля с установкой нового.

@PreConditions:
- request.data содержит token и new_password

@PostConditions:
- при валидном токене устанавливает новый пароль
- токен помечается как использованный
- при ошибке возвращает 400

@Invariants:
- токен используется только один раз

@SideEffects:
- обновление password пользователя в БД
- пометка токена как использованного
- логирование операции

@ForbiddenChanges:
- проверка is_used, is_expired перед сбросом пароля
"""
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    """
    Confirm password reset.
    
    Validates token and sets new password.
    """
    log_line("users", "DEBUG", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "ENTRY", {})
    
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        log_line("users", "WARN", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "ERROR", {
            "reason": "invalid_token",
        })
        log_line("users", "DEBUG", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "EXIT", {
            "result": "invalid_token",
        })
        return Response(
            {'error': 'Неверный токен.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if reset_token.is_used:
        log_line("users", "WARN", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "ERROR", {
            "reason": "token_used",
        })
        log_line("users", "DEBUG", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "EXIT", {
            "result": "token_used",
        })
        return Response(
            {'error': 'Токен уже использован.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if reset_token.is_expired:
        log_line("users", "WARN", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "ERROR", {
            "reason": "token_expired",
        })
        log_line("users", "DEBUG", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "EXIT", {
            "result": "token_expired",
        })
        return Response(
            {'error': 'Токен истёк.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = reset_token.user
    user.set_password(new_password)
    user.save()
    
    reset_token.mark_as_used()
    
    log_line("users", "INFO", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "STATE_CHANGE", {
        "action": "password_reset",
        "user_id": user.id,
    })
    log_line("users", "DEBUG", "password_reset_confirm_view", "PASSWORD_RESET_CONFIRM_VIEW", "EXIT", {
        "result": "success",
        "user_id": user.id,
    })
    
    return Response({'message': 'Пароль успешно сброшен.'})
# [END_PASSWORD_RESET_CONFIRM_VIEW]