# Feature: Восстановление пароля

> **ID**: FEAT-002
> **Status**: validated
> **Created**: 2026-04-14
> **Updated**: 2026-04-14
> **Depends on**: FEAT-001

---

## 📋 Описание

Система восстановления пароля через email. Пользователь вводит email, получает ссылку с токеном для сброса пароля. Токен одноразовый, срок действия — 24 часа. Включает rate limiting для защиты от флуда.

---

## 🎯 Цель

Позволить пользователям восстановить доступ к аккаунту без обращения к администратору. Снижает нагрузку на поддержку и улучшает UX.

---

## 📦 Компоненты

### Новые компоненты

| Компонент | Тип | Путь | Описание |
|-----------|-----|------|----------|
| PasswordResetService | service | `backend/apps/users/services.py` | Бизнес-логика сброса пароля |
| EmailService | service | `backend/apps/core/email.py` | Отправка email (общий сервис) |
| PasswordResetSerializer | serializer | `backend/apps/users/serializers.py` | Валидация запроса сброса |
| reset-password.html | page | `frontend/reset-password.html` | Страница сброса пароля |
| forgot-password.html | page | `frontend/forgot-password.html` | Страница запроса сброса |

### Изменяемые компоненты

| Компонент | Изменение |
|-----------|-----------|
| `backend/apps/users/models.py` | Модель PasswordResetToken (создана в FEAT-001) |
| `backend/apps/users/views.py` | Добавить endpoints reset_password, confirm_reset |
| `backend/config/settings/base.py` | Настройка email backend |
| `frontend/js/auth.js` | Методы resetPassword, confirmPasswordReset |

---

## 🔗 Связи

### Зависимости

- Зависит от: FEAT-001 (User, PasswordResetToken model)
- Зависит от: `backend.core.email.EmailService` (новый сервис)

### Semantic Graph Updates

```xml
<component id="backend.core.email" kind="service" path="lms-system/backend/apps/core/email.py">
  <role>Сервис отправки email (smtp/sendgrid/etc)</role>
  <exposes>
    <api name="send_email" type="function">Отправка email через настроенный backend</api>
    <api name="send_password_reset_email" type="function">Отправка письма со ссылкой сброса пароля</api>
  </exposes>
</component>

<component id="backend.apps.users.services.PasswordResetService" kind="service" path="lms-system/backend/apps/users/services.py">
  <role>Бизнес-логика восстановления пароля</role>
  <depends-on ref="backend.apps.users"/>
  <depends-on ref="backend.core.email"/>
  <exposes>
    <api name="request_password_reset" type="function" anchor="PASSWORD_RESET_REQUEST">Запрос на сброс пароля</api>
    <api name="confirm_password_reset" type="function" anchor="PASSWORD_RESET_CONFIRM">Подтверждение сброса</api>
  </exposes>
</component>

<edge id="api.auth.reset-request" from="frontend.auth" to="backend.apps.users.views.AuthViewSet" kind="http-rest">
  <endpoint>POST /api/auth/password-reset/</endpoint>
  <description>Запрос на сброс пароля</description>
</edge>

<edge id="api.auth.reset-confirm" from="frontend.auth" to="backend.apps.users.views.AuthViewSet" kind="http-rest">
  <endpoint>POST /api/auth/password-reset/confirm/</endpoint>
  <description>Подтверждение сброса пароля с токеном</description>
</edge>
```

---

## 📝 Контракты

### PASSWORD_RESET_REQUEST

**Функция**: `request_password_reset`
**Файл**: `backend/apps/users/services.py`

```
ANCHOR: PASSWORD_RESET_REQUEST
PURPOSE: Инициировать процесс восстановления пароля через email.

@PreConditions:
- email: валидный email формат

@PostConditions:
- если пользователь существует: создан PasswordResetToken, отправлено email
- если пользователь НЕ существует: молча возвращаем success (защита от перебора)
- всегда возвращается { success: true } (информационная безопасность)
- токен имеет expires_at = now() + 24 часа

@Invariants:
- один активный токен на пользователя (старые токены отзываются)
- email отправляется только на реальный адрес пользователя
- ответ всегда одинаковый (существует пользователь или нет)

@SideEffects:
- создаёт/обновляет PasswordResetToken в БД
- отправляет email через EmailService
- пишет лог запроса сброса (INFO)
- отзывает старые токены пользователя (used_at = now())

@ForbiddenChanges:
- нельзя возвращать разные ответы для существующих/несуществующих email
- нельзя отправлять несколько писем за короткий промежуток (rate limit)
- нельзя убрать проверку rate limiting
```

### PASSWORD_RESET_CONFIRM

**Функция**: `confirm_password_reset`
**Файл**: `backend/apps/users/services.py`

```
ANCHOR: PASSWORD_RESET_CONFIRM
PURPOSE: Завершить процесс сброса пароля по токену из email.

@PreConditions:
- token: непустая строка (UUID)
- new_password: строка 8-128 символов
- токен существует в БД
- токен не истёк (expires_at > now())
- токен не использован (used_at IS NULL)

@PostConditions:
- при успехе: user.password_hash = bcrypt(new_password)
- при успехе: token.used_at = now()
- при успехе: все refresh_tokens пользователя отозваны (revoked_at)
- при успехе: возвращается { success: true }
- при ошибке (токен не найден/истёк/использован): { error: "INVALID_OR_EXPIRED_TOKEN" }
- при ошибке (валидация пароля): { error: "VALIDATION_ERROR", fields: [...] }

@Invariants:
- токен одноразовый (used_at устанавливается при использовании)
- после сброса все сессии завершаются

@SideEffects:
- обновляет user.password_hash
- обновляет token.used_at
- обновляет all refresh_tokens.revoked_at для пользователя
- отправляет уведомление о смене пароля (email)
- пишет лог сброса пароля (INFO)

@ForbiddenChanges:
- нельзя разрешить повторное использование токена
- нельзя убрать отзыв всех сессий при смене пароля
- нельзя убрать уведомление о смене пароля
```

### EMAIL_SEND

**Функция**: `send_password_reset_email`
**Файл**: `backend/apps/core/email.py`

```
ANCHOR: EMAIL_SEND
PURPOSE: Отправить email со ссылкой для сброса пароля.

@PreConditions:
- to_email: валидный email формат
- reset_token: UUID токен
- user: пользователь существует

@PostConditions:
- при успехе: email отправлен через настроенный backend
- при ошибке (SMTP): логируется ошибка, возвращается success=False

@Invariants:
- ссылка содержит токен как query parameter: ?token={UUID}
- ссылка ведёт на frontend reset-password страницу

@SideEffects:
- отправляет email через SMTP/SendGrid/и т.д.
- пишет лог отправки (DEBUG)

@ForbiddenChanges:
- нельзя логировать токен в открытом виде
- нельзя отправлять пароль в email
```

---

## ✅ Критерии приёма

### User Story 3: Восстановление пароля

**Как** Пользователь
**Я хочу** восстановить забытый пароль через email
**Чтобы** получить доступ к аккаунту без обращения к администратору

**Acceptance Criteria**:
- [ ] Форма ввода email для запроса сброса
- [ ] Если email существует в системе — отправляется письмо со ссылкой
- [ ] Ссылка ведёт на страницу установки нового пароля
- [ ] Токен в ссылке имеет срок действия 24 часа
- [ ] После перехода по ссылке можно задать новый пароль
- [ ] После сброса пароля все активные сессии завершаются
- [ ] Если email НЕ существует — форма показывает "проверьте email" (без раскрытия информации)
- [ ] Rate limiting: не более 3 запросов сброса в час на email

### User Story: Безопасность сброса пароля

**Как** Система
**Я хочу** обеспечить безопасность процесса сброса пароля
**Чтобы** предотвратить несанкционированный доступ к аккаунтам

**Acceptance Criteria**:
- [ ] Токен одноразовый (после использования — недействителен)
- [ ] При создании нового токена старые отзываются
- [ ] При смене пароля отзываются все refresh токены
- [ ] Email уведомление при смене пароля
- [ ] Логирование всех запросов и подтверждений сброса
- [ ] Защита от перебора email (одинаковый ответ для любого email)

---

## 🧪 Тест-план

**Validation Report**: `plans/validation/V-FEAT-002.xml`

### Детерминированные тесты

**Unit-тесты (pytest)**:
- [ ] `test_password_reset_token_create` — создание токена сброса
- [ ] `test_password_reset_token_expiry` — проверка истечения срока
- [ ] `test_password_reset_token_used` — пометка токена как использованного
- [ ] `test_request_password_reset_existing_user` — запрос для существующего пользователя
- [ ] `test_request_password_reset_non_existing_user` — запрос для несуществующего пользователя
- [ ] `test_request_password_reset_rate_limit` — превышение rate limit
- [ ] `test_request_password_reset_revokes_old_tokens` — отзыв старых токенов
- [ ] `test_confirm_password_reset_success` — успешное подтверждение
- [ ] `test_confirm_password_reset_invalid_token` — невалидный токен
- [ ] `test_confirm_password_reset_expired_token` — истёкший токен
- [ ] `test_confirm_password_reset_used_token` — использованный токен
- [ ] `test_confirm_password_reset_revokes_sessions` — отзыв сессий при сбросе
- [ ] `test_email_service_send_success` — успешная отправка email
- [ ] `test_email_service_send_failure` — ошибка отправки email

### Тесты траектории (log markers)

- [ ] `test_reset_request_trajectory` — проверка маркеров PASSWORD_RESET_REQUEST: ENTRY → EXIT
- [ ] `test_reset_confirm_trajectory` — проверка маркеров PASSWORD_RESET_CONFIRM: ENTRY → EXIT
- [ ] `test_email_send_trajectory` — проверка маркеров EMAIL_SEND: ENTRY → EXIT

### Интеграционные тесты

**API Endpoints**:
- [ ] `test_api_password_reset_request` — запрос сброса через API
- [ ] `test_api_password_reset_confirm` — подтверждение сброса через API
- [ ] `test_api_password_reset_rate_limit` — rate limiting
- [ ] `test_api_password_reset_invalid_token` — невалидный токен
- [ ] `test_api_password_reset_expired_token` — истёкший токен

**E2E**:
- [ ] `test_e2e_password_reset_flow` — полный сценарий сброса пароля
- [ ] `test_e2e_password_reset_expired_link` — переход по истёкшей ссылке

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

- Depends on: `plans/features/FEAT-001.md`
- Validation Report: `plans/validation/V-FEAT-002.xml`
- Verification Report: `reports/verification-{TIMESTAMP}.md`
- Code:
  - `lms-system/backend/apps/users/services.py` (PasswordResetService)
  - `lms-system/backend/apps/core/email.py` (EmailService)
  - `lms-system/frontend/js/auth.js` (resetPassword, confirmPasswordReset)
  - `lms-system/frontend/forgot-password.html`
  - `lms-system/frontend/reset-password.html`
- Tests:
  - `lms-system/backend/tests/unit/test_password_reset.py`
  - `lms-system/backend/tests/integration/test_password_reset_api.py`
