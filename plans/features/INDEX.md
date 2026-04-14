# LMS System MVP — Feature Index

> **Last Updated**: 2026-04-14
> **Total Features**: 7

---

## 📊 Статус по фичам

| ID | Название | Статус | Sprint | Зависимости |
|----|----------|--------|--------|-------------|
| FEAT-001 | Аутентификация и регистрация | planning | 1 | — |
| FEAT-002 | Восстановление пароля | planning | 1 | FEAT-001 |
| FEAT-003 | Управление курсами и модулями | planning | 2 | FEAT-001 |
| FEAT-004 | Тесты и попытки прохождения | planning | 3 | FEAT-001, FEAT-003 |
| FEAT-005 | Отслеживание прогресса | planning | 3 | FEAT-001, FEAT-003, FEAT-004 |
| FEAT-006 | Бронирование ресурсов | planning | 4 | FEAT-001, FEAT-003 |
| FEAT-007 | Система уведомлений | planning | 4 | FEAT-001 |

---

## 📋 Детали по фичам

### Sprint 1: Базовая инфраструктура + Аутентификация

#### FEAT-001: Аутентификация и регистрация
- **Файл**: [FEAT-001.md](./FEAT-001.md)
- **ANCHORs**: `USER_REGISTER`, `AUTH_LOGIN`, `AUTH_REFRESH`, `AUTH_LOGOUT`, `JWT_VERIFY`
- **User Stories**: US1, US2, US3, US4, US5
- **Компоненты**: User, RefreshToken, AuthViewSet, AuthService
- **Ключевые точки**:
  - JWT access token (8h) + refresh token (30d)
  - Rate limiting на login (5/15min)
  - bcrypt хеширование паролей
  - Только admin может создавать пользователей

#### FEAT-002: Восстановление пароля
- **Файл**: [FEAT-002.md](./FEAT-002.md)
- **ANCHORs**: `PASSWORD_RESET_REQUEST`, `PASSWORD_RESET_CONFIRM`, `EMAIL_SEND`
- **User Stories**: US3
- **Компоненты**: PasswordResetToken, EmailService, PasswordResetService
- **Ключевые точки**:
  - Токен сброса 24ч
  - Rate limiting (3/час)
  - Отзыв всех сессий при смене пароля
  - Защита от перебора email

---

### Sprint 2: Курсы + Модули + Назначения

#### FEAT-003: Управление курсами и модулями
- **Файл**: [FEAT-003.md](./FEAT-003.md)
- **ANCHORs**: `COURSE_CREATE`, `COURSE_UPDATE`, `COURSE_DELETE`, `COURSE_PUBLISH`, `COURSE_ARCHIVE`, `MODULE_CREATE`, `MODULE_UPDATE`, `MODULE_DELETE`, `MODULE_REORDER`, `COURSE_ENROLL`
- **User Stories**: US4, US5, US6, US7, US8, US9, US13, US14, US23
- **Компоненты**: Course, Module, CourseEnrollment, CourseService
- **Ключевые точки**:
  - Статусы курса: draft → published → archived
  - Автоматический order_num для модулей
  - Нельзя опубликовать пустой курс
  - CASCADE удаление модулей при удалении курса

---

### Sprint 3: Тесты + Прогресс

#### FEAT-004: Тесты и попытки прохождения
- **Файл**: [FEAT-004.md](./FEAT-004.md)
- **ANCHORs**: `QUIZ_CREATE`, `QUIZ_UPDATE`, `QUIZ_DELETE`, `QUIZ_ATTEMPT_START`, `QUIZ_ATTEMPT_SUBMIT`, `QUIZ_SCORE_CALC`
- **User Stories**: US10, US11, US12, US15, US18
- **Компоненты**: Quiz, QuizOption, QuizAttempt, QuizAnswer, QuizService
- **Ключевые точки**:
  - 3 типа вопросов: single, multiple, open
  - Максимум 3 попытки на тест
  - Score = (correct / total) * 100
  - CASCADE удаление попыток при удалении теста

#### FEAT-005: Отслеживание прогресса
- **Файл**: [FEAT-005.md](./FEAT-005.md)
- **ANCHORs**: `PROGRESS_GET`, `PROGRESS_UPDATE`, `PROGRESS_COMPLETE`, `PROGRESS_CALC`
- **User Stories**: US16, US17
- **Компоненты**: UserProgress, ProgressService
- **Ключевые точки**:
  - Статусы: not_started → in_progress → completed
  - Score = max из всех попыток
  - Автоматическое завершение курса
  - Статус можно только повышать (не понижать)

---

### Sprint 4: Бронирование + Уведомления

#### FEAT-006: Бронирование ресурсов
- **Файл**: [FEAT-006.md](./FEAT-006.md)
- **ANCHORs**: `BOOKING_CREATE`, `BOOKING_CANCEL`
- **User Stories**: US19, US20
- **Компоненты**: Resource, Booking, BookingService
- **Ключевые точки**:
  - Типы ресурсов: classroom, trainer, equipment
  - Проверка конфликтов через PostgreSQL EXCLUDE constraint
  - Нельзя бронировать в прошлом
  - Уведомление тренеру при бронировании

#### FEAT-007: Система уведомлений
- **Файл**: [FEAT-007.md](./FEAT-007.md)
- **ANCHORs**: `NOTIFICATION_CREATE`, `NOTIFICATION_MARK_READ`
- **User Stories**: US21
- **Компоненты**: Notification, NotificationService
- **Ключевые точки**:
  - Типы: enrollment, booking, completion
  - Счётчик непрочитанных
  - Mark as read (идемпотентно)

---

## 🔗 Граф зависимостей

```
FEAT-001 (Auth)
    │
    ├──→ FEAT-002 (Password Reset)
    │
    ├──→ FEAT-003 (Courses)
    │       │
    │       ├──→ FEAT-004 (Quizzes)
    │       │       │
    │       │       └──→ FEAT-005 (Progress)
    │       │
    │       └──→ FEAT-006 (Bookings)
    │
    └──→ FEAT-007 (Notifications)
```

---

## 📊 Статистика

| Метрика | Значение |
|---------|----------|
| Всего фич | 7 |
| ANCHORs | 27 |
| User Stories | 21 |
| Sprint-ов | 4 |
| Компонентов backend | 18 |
| Компонентов frontend | 8 |

---

## 🚀 Порядок реализации

1. **Sprint 1**: FEAT-001 → FEAT-002 (3 недели)
2. **Sprint 2**: FEAT-003 (3 недели)
3. **Sprint 3**: FEAT-004 → FEAT-005 (3 недели)
4. **Sprint 4**: FEAT-006 → FEAT-007 (2 недели)
5. **Sprint 5**: Отчёты + аналитика (2 недели)
6. **Sprint 6**: Тестирование + CI/CD (2 недели)

---

## 📝 Следующие шаги

1. Запустить `grace-validate-plan` для каждой фичи
2. Исправить замечания валидации
3. Начать реализацию с FEAT-001
