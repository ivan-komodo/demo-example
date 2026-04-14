# Feature: Бронирование ресурсов

> **ID**: FEAT-006
> **Status**: validated
> **Created**: 2026-04-14
> **Updated**: 2026-04-14
> **Depends on**: FEAT-001, FEAT-003

---

## 📋 Описание

Система бронирования ресурсов: аудитории, тренеры, оборудование. Проверка конфликтов по времени. Календарь бронирований. Уведомления при бронировании.

---

## 🎯 Цель

Организовать очное обучение и события. Оптимизировать использование ресурсов.

---

## 📦 Компоненты

### Новые компоненты

| Компонент | Тип | Путь | Описание |
|-----------|-----|------|----------|
| Resource | model | `backend/apps/bookings/models.py` | Ресурс (classroom/trainer/equipment) |
| Booking | model | `backend/apps/bookings/models.py` | Бронирование |
| ResourceViewSet | viewset | `backend/apps/bookings/views.py` | CRUD ресурсов |
| BookingViewSet | viewset | `backend/apps/bookings/views.py` | CRUD бронирований |
| BookingService | service | `backend/apps/bookings/services.py` | Бизнес-логика |
| bookings.js | module | `frontend/js/bookings.js` | Календарь на клиенте |
| bookings.html | page | `frontend/bookings.html` | Страница бронирования |

---

## 📝 Контракты

### BOOKING_CREATE

**Функция**: `create_booking`
**Файл**: `backend/apps/bookings/services.py`

```
ANCHOR: BOOKING_CREATE
PURPOSE: Забронировать ресурс на указанный период.

@PreConditions:
- request.user.role == 'admin' или 'trainer'
- resource_id: существующий активный ресурс
- start_time < end_time
- start_time > now() (нельзя забронировать в прошлом)
- нет пересечений с существующими бронированиями ресурса

@PostConditions:
- при успехе: Booking создан, status='confirmed'
- при успехе: уведомление отправлено тренеру
- при ошибке (конфликт): { error: "BOOKING_CONFLICT", conflicting_bookings: [...] }
- при ошибке (валидация): { error: "VALIDATION_ERROR", fields: [...] }

@Invariants:
- один ресурс не может быть забронирован на пересекающиеся периоды
- PostgreSQL EXCLUDE constraint гарантирует отсутствие пересечений

@SideEffects:
- создаёт Booking в БД
- создаёт Notification для тренера (если ресурс = trainer)
- пишет лог бронирования (INFO)

@ForbiddenChanges:
- нельзя убрать проверку конфликтов
- нельзя бронировать в прошлом
```

### BOOKING_CANCEL

**Функция**: `cancel_booking`
**Файл**: `backend/apps/bookings/services.py`

```
ANCHOR: BOOKING_CANCEL
PURPOSE: Отменить бронирование.

@PreConditions:
- booking_id: существующее бронирование
- request.user == booking.user или request.user.role == 'admin'
- start_time > now() (нельзя отменить прошедшее)

@PostConditions:
- booking.status = 'cancelled'
- уведомление отправлено участникам

@Invariants:
- отменить можно только будущие бронирования

@SideEffects:
- обновляет booking.status
- создаёт Notification
- пишет лог отмены (INFO)

@ForbiddenChanges:
- нельзя отменить прошедшее бронирование
```

---

## ✅ Критерии приёма

### User Story 19: Бронирование ресурса

**Как** Администратор
**Я хочу** забронировать ресурс (аудитория, тренер, дата/время)
**Чтобы** организовать очное обучение

**Acceptance Criteria**:
- [ ] Выбор ресурса из списка
- [ ] Проверка на конфликт по времени
- [ ] Уведомление тренеру при бронировании
- [ ] Валидация: start < end, start > now

### User Story 20: Просмотр бронирований

**Как** Тренер
**Я хочу** просмотреть список назначенных сессий
**Чтобы** планировать время

**Acceptance Criteria**:
- [ ] Календарь или список бронирований
- [ ] Фильтрация по датам
- [ ] Фильтрация по статусу

---

## 🧪 Тест-план

- [ ] `test_booking_model_create` — создание бронирования
- [ ] `test_booking_service_create_success` — успешное бронирование
- [ ] `test_booking_service_conflict` — конфликт бронирований
- [ ] `test_booking_service_past_time` — бронирование в прошлом
- [ ] `test_booking_service_cancel` — отмена бронирования
- [ ] `test_booking_trajectory` — маркеры BOOKING_CREATE

---

## 📊 Статус реализации

| Этап | Статус | Дата | Комментарий |
|------|--------|------|-------------|
| Planning | ✅ | 2026-04-14 | Feature Spec создан |
| Validation | ✅ | 2026-04-14 | Validation Report: pass |
