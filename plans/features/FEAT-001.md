# Feature: Аутентификация и регистрация пользователей

> **ID**: FEAT-001
> **Status**: validated
> **Created**: 2026-04-14
> **Updated**: 2026-04-14

---

## 📋 Описание

Система аутентификации на основе JWT с поддержкой refresh токенов. Включает регистрацию пользователей администратором, логин по email/password, логаут и обновление токенов. Реализует ролевую модель (admin/trainer/learner) с защитой от перебора паролей.

---

## 🎯 Цель

Обеспечить безопасную аутентификацию и авторизацию пользователей для доступа к LMS системе. Решает проблему идентификации пользователя и разграничения прав доступа на основе ролей.

---

## 📦 Компоненты

### Новые компоненты

| Компонент | Тип | Путь | Описание |
|-----------|-----|------|----------|
| User | model | `backend/apps/users/models.py` | Модель пользователя с ролями |
| RefreshToken | model | `backend/apps/users/models.py` | JWT refresh токены |
| PasswordResetToken | model | `backend/apps/users/models.py` | Токены сброса пароля (заготовка для FEAT-002) |
| AuthViewSet | viewset | `backend/apps/users/views.py` | Регистрация, логин, логаут, refresh |
| UserViewSet | viewset | `backend/apps/users/views.py` | CRUD пользователей |
| AuthService | service | `backend/apps/users/services.py` | Бизнес-логика аутентификации |
| UserSerializer | serializer | `backend/apps/users/serializers.py` | Сериализация пользователя |
| AuthSerializer | serializer | `backend/apps/users/serializers.py` | Валидация login/register |
| RolePermission | permission | `backend/apps/users/permissions.py` | Ролевые права доступа |
| auth.js | module | `frontend/js/auth.js` | Клиентская аутентификация |
| api.js | module | `frontend/js/api.js` | API клиент с JWT |
| login.html | page | `frontend/login.html` | Страница входа |
| login.css | stylesheet | `frontend/css/login.css` | Стили страницы входа |

### Изменяемые компоненты

| Компонент | Изменение |
|-----------|-----------|
| `backend/config/urls.py` | Добавление маршрутов auth и users |
| `backend/config/settings/base.py` | Настройка JWT, bcrypt, CORS |
| `frontend/js/main.js` | Инициализация AuthManager |

---

## 🔗 Связи

### Зависимости

- Зависит от: `backend.core` (permissions, exceptions, middleware)
- Зависимые: `backend.apps.courses`, `backend.apps.quizzes`, `backend.apps.progress`, `backend.apps.bookings`, `backend.apps.notifications`

### Semantic Graph Updates

```xml
<component id="backend.apps.users.models.User" kind="model" path="lms-system/backend/apps/users/models.py">
  <role>Пользователь системы с ролями admin/trainer/learner</role>
  <exposes>
    <api name="User" type="model">Email, password_hash, full_name, role, is_active</api>
  </exposes>
</component>

<component id="backend.apps.users.services.AuthService" kind="service" path="lms-system/backend/apps/users/services.py">
  <role>Бизнес-логика аутентификации JWT</role>
  <depends-on ref="backend.apps.users.models.User"/>
  <depends-on ref="backend.apps.users.models.RefreshToken"/>
  <exposes>
    <api name="register_user" type="function">Регистрация нового пользователя</api>
    <api name="authenticate_user" type="function">Логин с генерацией JWT</api>
    <api name="refresh_tokens" type="function">Обновление access/refresh токенов</api>
    <api name="logout_user" type="function">Отзыв refresh токена</api>
  </exposes>
</component>

<component id="backend.apps.users.views.AuthViewSet" kind="viewset" path="lms-system/backend/apps/users/views.py">
  <role>API endpoints для аутентификации</role>
  <depends-on ref="backend.apps.users.services.AuthService"/>
  <exposes>
    <api name="/api/auth/register/" type="endpoint">POST - регистрация пользователя</api>
    <api name="/api/auth/login/" type="endpoint">POST - аутентификация</api>
    <api name="/api/auth/logout/" type="endpoint">POST - логаут</api>
    <api name="/api/auth/refresh/" type="endpoint">POST - обновление токенов</api>
  </exposes>
</component>

<component id="frontend.auth" kind="module" path="lms-system/frontend/js/auth.js">
  <role>Управление аутентификацией на клиенте</role>
  <depends-on ref="frontend.api"/>
  <exposes>
    <api name="AuthManager" type="class">login, logout, refresh, isAuthenticated</api>
  </exposes>
</component>

<edge id="api.auth.register" from="frontend.auth" to="backend.apps.users.views.AuthViewSet" kind="http-rest">
  <endpoint>/api/auth/register/</endpoint>
  <methods>POST</methods>
</edge>

<edge id="api.auth.login" from="frontend.auth" to="backend.apps.users.views.AuthViewSet" kind="http-rest">
  <endpoint>/api/auth/login/</endpoint>
  <methods>POST</methods>
</edge>

<edge id="api.auth.logout" from="frontend.auth" to="backend.apps.users.views.AuthViewSet" kind="http-rest">
  <endpoint>/api/auth/logout/</endpoint>
  <methods>POST</methods>
</edge>

<edge id="api.auth.refresh" from="frontend.auth" to="backend.apps.users.views.AuthViewSet" kind="http-rest">
  <endpoint>/api/auth/refresh/</endpoint>
  <methods>POST</methods>
</edge>
```

---

## 📝 Контракты

### USER_REGISTER

**Функция**: `register_user`
**Файл**: `backend/apps/users/services.py`

```
ANCHOR: USER_REGISTER
PURPOSE: Регистрация нового пользователя администратором системы.

@PreConditions:
- request.user.role == 'admin' (только админ может создавать пользователей)
- email: валидный email формат, уникальный в БД
- password: строка длиной 8-128 символов
- role: одно из значений ('admin', 'trainer', 'learner')
- full_name: непустая строка (опционально)

@PostConditions:
- при успехе: User создан в БД,.password_hash = bcrypt(password)
- при успехе: возвращается { id, email, full_name, role, is_active, created_at }
- при ошибке (email exists): { error: "EMAIL_ALREADY_EXISTS" }
- при ошибке (недостаточно прав): { error: "PERMISSION_DENIED" }
- при ошибке (валидация): { error: "VALIDATION_ERROR", fields: [...] }

@Invariants:
- пароль НИКОГДА не хранится в открытом виде
- пароль НИКОГДА не возвращается в ответе API
- email всегда приводится к lowercase

@SideEffects:
- создаёт запись в таблице users
- пишет лог регистрации (INFO уровень)

@ForbiddenChanges:
- нельзя разрешить регистрацию не-администраторам
- нельзя ослабить валидацию email
- нельзя убрать bcrypt хеширование
```

### AUTH_LOGIN

**Функция**: `authenticate_user`
**Файл**: `backend/apps/users/services.py`

```
ANCHOR: AUTH_LOGIN
PURPOSE: Аутентификация пользователя по email и паролю с выдачей JWT токенов.

@PreConditions:
- email: валидный email формат
- password: непустая строка
- user.is_active == True (пользователь активен)

@PostConditions:
- при успехе: возвращается { access_token, refresh_token, user: {...} }
- при успехе: refresh_token сохранён в БД с expires_at = now() + 30 дней
- при ошибке (неверные данные): { error: "INVALID_CREDENTIALS" }
- при ошибке (rate limit): { error: "RATE_LIMIT_EXCEEDED", retry_after: <seconds> }

@Invariants:
- пароль НИКОГДА не возвращается в ответе
- одинаковая ошибка для несуществующего email и неверного пароля (защита от перебора)
- refresh токен уникален для каждой сессии

@SideEffects:
- создаёт/обновляет refresh_token в БД
- инкрементирует счётчик failed_attempts при ошибке
- пишет лог попытки входа (DEBUG - успех, WARN - неудача)
- при успехе: сбрасывает failed_attempts

@ForbiddenChanges:
- нельзя убрать rate limiting на /login
- нельзя возвращать разные ошибки для разных сценариев (user exists vs wrong password)
- нельзя убрать bcrypt проверку пароля
```

### AUTH_REFRESH

**Функция**: `refresh_tokens`
**Файл**: `backend/apps/users/services.py`

```
ANCHOR: AUTH_REFRESH
PURPOSE: Обновление JWT токенов по валидному refresh токену.

@PreConditions:
- refresh_token: непустая строка
- refresh токен существует в БД
- refresh токен не истёк (expires_at > now())
- refresh токен не отозван (revoked_at IS NULL)

@PostConditions:
- при успехе: старый refresh токен помечен revoked_at
- при успехе: создан новый refresh_token в БД
- при успехе: возвращается { access_token, refresh_token }
- при ошибке (invalid/expired/revoked): { error: "INVALID_REFRESH_TOKEN" }

@Invariants:
- каждый refresh токен используется только один раз (rotation)
- новый refresh токен генерируется при каждом обновлении

@SideEffects:
- обновляет revoked_at старого токена
- создаёт новую запись refresh_token
- пишет лог обновления токена (DEBUG)

@ForbiddenChanges:
- нельзя переиспользовать старый refresh токен
- нельзя убрать проверку revoked_at
```

### AUTH_LOGOUT

**Функция**: `logout_user`
**Файл**: `backend/apps/users/services.py`

```
ANCHOR: AUTH_LOGOUT
PURPOSE: Отзыв refresh токена для завершения сессии.

@PreConditions:
- refresh_token: непустая строка
- токен существует в БД

@PostConditions:
- токен помечен revoked_at = now()
- возвращается { success: true }
- при ошибке (токен не найден): молча возвращаем success (idempotent)

@Invariants:
- logout идемпотентен (повторный вызов не вызывает ошибку)

@SideEffects:
- обновляет revoked_at токена
- пишет лог логаута (INFO)

@ForbiddenChanges:
- нельзя требовать валидный токен для логаута (idempotency)
```

### JWT_VERIFY

**Функция**: `verify_token`
**Файл**: `backend/apps/users/services.py`

```
ANCHOR: JWT_VERIFY
PURPOSE: Проверка валидности access токена и извлечение данных пользователя.

@PreConditions:
- access_token: непустая строка
- токен в формате JWT

@PostConditions:
- при успехе: возвращается { user_id, email, role, exp }
- при ошибке (expired): { error: "TOKEN_EXPIRED" }
- при ошибке (invalid): { error: "INVALID_TOKEN" }

@Invariants:
- access токен не проверяется по БД (stateless)
- проверка только подписи и срока действия

@SideEffects:
- нет побочных эффектов

@ForbiddenChanges:
- нельзя добавлять проверки по БД для access токена (stateless)
```

---

## ✅ Критерии приёма

### User Story 1: Регистрация пользователя

**Как** Администратор
**Я хочу** зарегистрировать нового пользователя (тренер/слушатель)
**Чтобы** предоставить ему доступ к системе

**Acceptance Criteria**:
- [ ] Форма ввода: email (с валидацией), пароль, роль, ФИО
- [ ] Пароль хешируется bcrypt
- [ ] Email уникален в системе
- [ ] При успехе: пользователь создан, возвращаются данные
- [ ] При ошибке: валидное сообщение об ошибке
- [ ] Только администратор может создавать пользователей

### User Story 2: Вход в систему

**Как** Пользователь
**Я хочу** войти в систему по email и паролю
**Чтобы** получить доступ к функциям системы

**Acceptance Criteria**:
- [ ] JWT access токен возвращается (срок 8 часов)
- [ ] Refresh токен возвращается (срок 30 дней)
- [ ] При неверных данных: одинаковая ошибка "INVALID_CREDENTIALS"
- [ ] Rate limiting: максимум 5 попыток за 15 минут с одного IP
- [ ] При превышении rate limit: ошибка с retry_after
- [ ] В ответе нет пароля и password_hash

### User Story 3: Обновление токенов

**Как** Пользователь
**Я хочу** обновить access токен без повторного ввода пароля
**Чтобы** продолжить работу без прерывания сессии

**Acceptance Criteria**:
- [ ] Refresh токен обменивается на новую пару access + refresh
- [ ] Старый refresh токен отзывается (rotation)
- [ ] Использованный refresh токен нельзя применить повторно
- [ ] При невалидном refresh: ошибка INVALID_REFRESH_TOKEN

### User Story 4: Выход из системы

**Как** Пользователь
**Я хочу** выйти из системы
**Чтобы** завершить сессию и отозвать токены

**Acceptance Criteria**:
- [ ] Refresh токен отзывается (revoked_at)
- [ ] Access токен остаётся валидным до истечения (stateless)
- [ ] Logout идемпотентен (повторный вызов успешен)
- [ ] После логаута refresh возвращает ошибку

### User Story 5: Защита от перебора

**Как** Система
**Я хочу** ограничить количество попыток входа
**Чтобы** предотвратить перебор паролей

**Acceptance Criteria**:
- [ ] Rate limiting: 5 запросов / 15 минут на IP для /login
- [ ] При превышении: HTTP 429 с заголовком Retry-After
- [ ] Логирование всех попыток входа (успешных и неудачных)
- [ ] Уведомление админа при >10 неудачных попыток с одного IP

---

## 🧪 Тест-план

**Validation Report**: `plans/validation/V-FEAT-001.xml`

### Детерминированные тесты

**Unit-тесты (pytest)**:
- [ ] `test_user_model_create` — создание пользователя с bcrypt хешем
- [ ] `test_user_model_email_unique` — уникальность email
- [ ] `test_user_model_role_validation` — валидация ролей
- [ ] `test_auth_service_register_success` — успешная регистрация
- [ ] `test_auth_service_register_email_exists` — ошибка дублирования email
- [ ] `test_auth_service_login_success` — успешный логин
- [ ] `test_auth_service_login_invalid_password` — неверный пароль
- [ ] `test_auth_service_login_user_not_found` — пользователь не найден
- [ ] `test_auth_service_login_rate_limit` — превышение rate limit
- [ ] `test_auth_service_refresh_success` — успешное обновление токенов
- [ ] `test_auth_service_refresh_invalid_token` — невалидный refresh
- [ ] `test_auth_service_refresh_expired_token` — истёкший refresh
- [ ] `test_auth_service_refresh_revoked_token` — отозванный refresh
- [ ] `test_auth_service_logout_success` — успешный логаут
- [ ] `test_auth_service_logout_idempotent` — идемпотентность логаута
- [ ] `test_jwt_verify_success` — валидация access токена
- [ ] `test_jwt_verify_expired` — истёкший access токен
- [ ] `test_jwt_verify_invalid` — невалидный access токен

**Serializers**:
- [ ] `test_user_serializer_valid` — валидные данные
- [ ] `test_user_serializer_email_invalid` — невалидный email
- [ ] `test_user_serializer_password_short` — короткий пароль
- [ ] `test_auth_login_serializer_valid` — валидные данные логина
- [ ] `test_auth_login_serializer_missing_fields` — отсутствующие поля

### Тесты траектории (log markers)

- [ ] `test_register_trajectory` — проверка маркеров USER_REGISTER: ENTRY → EXIT
- [ ] `test_login_trajectory` — проверка маркеров AUTH_LOGIN: ENTRY → BRANCH → EXIT
- [ ] `test_login_failed_trajectory` — проверка маркеров AUTH_LOGIN: ENTRY → ERROR → EXIT
- [ ] `test_refresh_trajectory` — проверка маркеров AUTH_REFRESH: ENTRY → EXIT
- [ ] `test_logout_trajectory` — проверка маркеров AUTH_LOGOUT: ENTRY → EXIT

### Интеграционные тесты

**API Endpoints (pytest + APIClient)**:
- [ ] `test_api_register_admin_only` — только админ может регистрировать
- [ ] `test_api_register_success` — успешная регистрация через API
- [ ] `test_api_login_success` — успешный логин через API
- [ ] `test_api_login_invalid_credentials` — неверные данные для логина
- [ ] `test_api_login_rate_limit` — rate limiting на логин
- [ ] `test_api_refresh_success` — обновление токенов через API
- [ ] `test_api_logout_success` — логаут через API
- [ ] `test_api_protected_endpoint_with_valid_token` — доступ с токеном
- [ ] `test_api_protected_endpoint_without_token` — доступ без токена
- [ ] `test_api_protected_endpoint_expired_token` — доступ с истёкшим токеном

**E2E (Playwright/Cypress)**:
- [ ] `test_e2e_login_flow` — полный сценарий входа в систему
- [ ] `test_e2e_register_flow` — сценарий регистрации админом
- [ ] `test_e2e_session_persistence` — сохранение сессии при перезагрузке
- [ ] `test_e2e_token_refresh_flow` — автоматическое обновление токена
- [ ] `test_e2e_logout_flow` — сценарий выхода из системы

---

## 📊 Статус реализации

| Этап | Статус | Дата | Комментарий |
|------|--------|------|-------------|
| Planning | ✅ | 2026-04-14 | Feature Spec создан |
| Validation | ✅ | 2026-04-14 | Validation Report: pass |
| Implementation | ⏳ | | |
| Verification | ⏳ | | |

---

## 📎 Связанные артефакты

- Validation Report: `plans/validation/V-FEAT-001.xml`
- Verification Report: `reports/verification-{TIMESTAMP}.md`
- Code: 
  - `lms-system/backend/apps/users/models.py`
  - `lms-system/backend/apps/users/views.py`
  - `lms-system/backend/apps/users/services.py`
  - `lms-system/backend/apps/users/serializers.py`
  - `lms-system/frontend/js/auth.js`
  - `lms-system/frontend/js/api.js`
- Tests:
  - `lms-system/backend/tests/unit/test_users_models.py`
  - `lms-system/backend/tests/unit/test_users_services.py`
  - `lms-system/backend/tests/integration/test_auth_api.py`
  - `lms-system/backend/tests/e2e/test_auth_flow.py`
