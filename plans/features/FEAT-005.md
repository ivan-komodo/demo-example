# Feature: Отслеживание прогресса

> **ID**: FEAT-005
> **Status**: validated
> **Created**: 2026-04-14
> **Updated**: 2026-04-14
> **Depends on**: FEAT-001, FEAT-003, FEAT-004

---

## 📋 Описание

Система отслеживания прогресса пользователей по модулям курсов. Автоматическое обновление статуса при прохождении модулей и тестов. Расчёт общего прогресса по курсу.

---

## 🎯 Цель

Дать пользователю и администратору видимость прогресса обучения. Мотивировать завершением курсов.

---

## 📦 Компоненты

### Новые компоненты

| Компонент | Тип | Путь | Описание |
|-----------|-----|------|----------|
| UserProgress | model | `backend/apps/progress/models.py` | Прогресс по модулю |
| ProgressViewSet | viewset | `backend/apps/progress/views.py` | API прогресса |
| ProgressService | service | `backend/apps/progress/services.py` | Бизнес-логика прогресса |
| progress.js | module | `frontend/js/progress.js` | Отображение прогресса |
| progress.html | page | `frontend/progress.html` | Страница моего прогресса |

### Изменяемые компоненты

| Компонент | Изменение |
|-----------|-----------|
| `backend/config/urls.py` | Добавление маршрутов progress |
| `backend/apps/quizzes/services.py` | Обновление UserProgress при test completion |

---

## 🔗 Связи

### Зависимости

- Зависит от: FEAT-001 (User), FEAT-003 (Module, CourseEnrollment), FEAT-004 (QuizAttempt)
- Зависимые: FEAT-007 (Notifications)

### Semantic Graph Updates

```xml
<component id="backend.apps.progress.services" kind="service" path="lms-system/backend/apps/progress/services.py">
  <role>Бизнес-логика отслеживания прогресса</role>
  <depends-on ref="backend.apps.progress"/>
  <depends-on ref="backend.apps.courses"/>
  <exposes>
    <api name="get_user_progress" type="function" anchor="PROGRESS_GET">Получение прогресса</api>
    <api name="update_module_progress" type="function" anchor="PROGRESS_UPDATE">Обновление прогресса модуля</api>
    <api name="calculate_course_progress" type="function" anchor="PROGRESS_CALC">Расчёт прогресса курса</api>
    <api name="mark_module_completed" type="function" anchor="PROGRESS_COMPLETE">Завершение модуля</api>
  </exposes>
</component>
```

---

## 📝 Контракты

### PROGRESS_GET

**Функция**: `get_user_progress`
**Файл**: `backend/apps/progress/services.py`

```
ANCHOR: PROGRESS_GET
PURPOSE: Получить прогресс пользователя по курсу или модулю.

@PreConditions:
- пользователь авторизован
- course_id или module_id указан
- пользователь записан на курс

@PostConditions:
- для курса: { modules: [...], total_progress: X%, completed_modules: Y, total_modules: Z }
- для модуля: { status, completed_at, score }
- при ошибке (не записан на курс): { error: "NOT_ENROLLED" }

@Invariants:
- total_progress = (completed_modules / total_modules) * 100
- статус: not_started / in_progress / completed

@SideEffects:
- нет побочных эффектов

@ForbiddenChanges:
- нельзя получить прогресс чужого пользователя (без admin прав)
```

### PROGRESS_UPDATE

**Функция**: `update_module_progress`
**Файл**: `backend/apps/progress/services.py`

```
ANCHOR: PROGRESS_UPDATE
PURPOSE: Обновить прогресс пользователя по модулю.

@PreConditions:
- user_id: существующий пользователь
- module_id: существующий модуль
- пользователь записан на курс модуля

@PostConditions:
- если status = 'in_progress': UserProgress.status = 'in_progress'
- если status = 'completed': UserProgress.status = 'completed', completed_at = now()
- score обновляется при наличии

@Invariants:
- статус не может вернуться назад (completed → in_progress запрещён)
- score = max(score из всех попыток теста)

@SideEffects:
- обновляет UserProgress
- проверяет и обновляет CourseEnrollment (если курс завершён)
- пишет лог обновления (DEBUG)

@ForbiddenChanges:
- нельзя понизить статус (completed → in_progress)
- нельзя понизить score
```

### PROGRESS_COMPLETE

**Функция**: `mark_module_completed`
**Файл**: `backend/apps/progress/services.py`

```
ANCHOR: PROGRESS_COMPLETE
PURPOSE: Отметить модуль как завершённый (после успешного теста).

@PreConditions:
- user_id: существующий пользователь
- module_id: модуль с тестом
- тест пройден (score >= passing_score или любой балл)

@PostConditions:
- UserProgress.status = 'completed'
- UserProgress.completed_at = now()
- UserProgress.score = max(quiz_score, existing_score)
- если все модули завершены → CourseEnrollment.completed_at = now()

@Invariants:
- модуль считается завершённым после прохождения теста
- score = лучший результат из всех попыток

@SideEffects:
- обновляет UserProgress
- может обновить CourseEnrollment
- создаёт Notification (курс завершён)
- пишет лог завершения (INFO)

@ForbiddenChanges:
- нельзя отметить модуль завершённым без теста (если тест есть)
```

---

## ✅ Критерии приёма

### User Story 16: Просмотр прогресса

**Как** Слушатель
**Я хочу** просмотреть свой прогресс по курсу
**Чтобы** понимать, сколько осталось

**Acceptance Criteria**:
- [ ] Отображение статуса каждого модуля
- [ ] Общий прогресс в процентах
- [ ] Количество завершённых / всего модулей
- [ ] Score по каждому модулю

### User Story 17: Сохранение прогресса

**Как** Система
**Я хочу** сохранять прогресс пользователя по каждому модулю
**Чтобы** отслеживать обучение

**Acceptance Criteria**:
- [ ] Статус: not_started / in_progress / completed
- [ ] Автоматическое обновление при просмотре модуля
- [ ] Автоматическое обновление при прохождении теста

---

## 🧪 Тест-план

### Детерминированные тесты

- [ ] `test_progress_model_create` — создание прогресса
- [ ] `test_progress_service_get` — получение прогресса
- [ ] `test_progress_service_update_start` — начало модуля
- [ ] `test_progress_service_update_complete` — завершение модуля
- [ ] `test_progress_service_course_complete` — завершение курса
- [ ] `test_progress_service_score_max` — максимальный score

### Тесты траектории

- [ ] `test_progress_get_trajectory` — маркеры PROGRESS_GET
- [ ] `test_progress_update_trajectory` — маркеры PROGRESS_UPDATE
- [ ] `test_progress_complete_trajectory` — маркеры PROGRESS_COMPLETE

---

## 📊 Статус реализации

| Этап | Статус | Дата | Комментарий |
|------|--------|------|-------------|
| Planning | ✅ | 2026-04-14 | Feature Spec создан |
| Validation | ✅ | 2026-04-14 | Validation Report: pass |
| Implementation | ⏳ | | |
| Verification | ⏳ | | |
