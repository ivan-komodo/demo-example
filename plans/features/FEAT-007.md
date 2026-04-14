# Feature: Система уведомлений

> **ID**: FEAT-007
> **Status**: validated
> **Created**: 2026-04-14
> **Updated**: 2026-04-14
> **Depends on**: FEAT-001

---

## 📋 Описание

Система уведомлений пользователей о событиях: запись на курс, бронирование, завершение курса. Mark as read. Счётчик непрочитанных.

---

## 🎯 Цель

Информировать пользователей о важных событиях в системе.

---

## 📦 Компоненты

### Новые компоненты

| Компонент | Тип | Путь | Описание |
|-----------|-----|------|----------|
| Notification | model | `backend/apps/notifications/models.py` | Уведомление |
| NotificationViewSet | viewset | `backend/apps/notifications/views.py` | API уведомлений |
| NotificationService | service | `backend/apps/notifications/services.py` | Создание уведомлений |
| notifications.js | module | `frontend/js/notifications.js` | UI уведомлений |

---

## 📝 Контракты

### NOTIFICATION_CREATE

**Функция**: `create_notification`
**Файл**: `backend/apps/notifications/services.py`

```
ANCHOR: NOTIFICATION_CREATE
PURPOSE: Создать уведомление для пользователя.

@PreConditions:
- user_id: существующий пользователь
- type: тип уведомления (enrollment, booking, completion, etc.)
- title: непустая строка
- message: непустая строка

@PostConditions:
- Notification создан, is_read=False
- возвращается { id, user_id, type, title, message, is_read, created_at }

@Invariants:
- createdAt = now() автоматически
- is_read = False по умолчанию

@SideEffects:
- создаёт Notification в БД
- (опционально) отправка push/email

@ForbiddenChanges:
- нельзя создать уведомление для несуществующего пользователя
```

### NOTIFICATION_MARK_READ

**Функция**: `mark_as_read`
**Файл**: `backend/apps/notifications/services.py`

```
ANCHOR: NOTIFICATION_MARK_READ
PURPOSE: Отметить уведомление как прочитанное.

@PreConditions:
- notification_id: существующее уведомление пользователя

@PostConditions:
- notification.is_read = True
- возвращается { success: true }

@Invariants:
- mark_as_read идемпотентен

@SideEffects:
- обновляет is_read
- нет логирования (DEBUG только)

@ForbiddenChanges:
- нельзя отметить чужое уведомление
```

---

## ✅ Критерии приёма

### User Story 21: Просмотр уведомлений

**Как** Пользователь
**Я хочу** просмотреть уведомления
**Чтобы** быть в курсе событий

**Acceptance Criteria**:
- [ ] Список уведомлений
- [ ] Возможность отметки прочитанными
- [ ] Счётчик непрочитанных в header
- [ ] Сортировка по дате (новые сверху)

---

## 🧪 Тест-план

- [ ] `test_notification_model_create` — создание уведомления
- [ ] `test_notification_service_create` — сервис создания
- [ ] `test_notification_service_mark_read` — отметка прочитанным
- [ ] `test_notification_api_list` — список через API
- [ ] `test_notification_trajectory` — маркеры NOTIFICATION_CREATE

---

## 📊 Статус реализации

| Этап | Статус | Дата | Комментарий |
|------|--------|------|-------------|
| Planning | ✅ | 2026-04-14 | Feature Spec создан |
| Validation | ✅ | 2026-04-14 | Validation Report: pass |
