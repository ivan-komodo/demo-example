# Feature: Управление курсами и модулями

> **ID**: FEAT-003
> **Status**: validated
> **Created**: 2026-04-14
> **Updated**: 2026-04-14
> **Depends on**: FEAT-001

---

## 📋 Описание

CRUD операции для курсов и модулей. Включает создание, редактирование, удаление, публикацию курсов. Модули поддерживают три типа контента: текст, PDF, видео. Автоматический порядок модулей через order_num.

---

## 🎯 Цель

Позволить администраторам создавать и управлять образовательным контентом. Курсы — основная единица обучения, модули — структурные части курса.

---

## 📦 Компоненты

### Новые компоненты

| Компонент | Тип | Путь | Описание |
|-----------|-----|------|----------|
| Course | model | `backend/apps/courses/models.py` | Курс (title, description, status) |
| Module | model | `backend/apps/courses/models.py` | Модуль курса (text/pdf/video) |
| CourseEnrollment | model | `backend/apps/courses/models.py` | Запись пользователя на курс |
| CourseViewSet | viewset | `backend/apps/courses/views.py` | CRUD курсов |
| ModuleViewSet | viewset | `backend/apps/courses/views.py` | CRUD модулей |
| EnrollmentViewSet | viewset | `backend/apps/courses/views.py` | Управление записями |
| CourseService | service | `backend/apps/courses/services.py` | Бизнес-логика курсов |
| CourseSerializer | serializer | `backend/apps/courses/serializers.py` | Сериализация курса |
| ModuleSerializer | serializer | `backend/apps/courses/serializers.py` | Сериализация модуля |
| courses.js | module | `frontend/js/courses.js` | Работа с курсами на клиенте |
| courses.html | page | `frontend/courses.html` | Страница списка курсов |
| course-detail.html | page | `frontend/course-detail.html` | Страница курса |
| course-form.html | page | `frontend/course-form.html` | Форма создания/редактирования курса |

### Изменяемые компоненты

| Компонент | Изменение |
|-----------|-----------|
| `backend/config/urls.py` | Добавление маршрутов courses |
| `frontend/js/main.js` | Инициализация CoursesManager |

---

## 🔗 Связи

### Зависимости

- Зависит от: FEAT-001 (User, permissions)
- Зависимые: FEAT-004 (Quizzes), FEAT-005 (Progress), FEAT-006 (Bookings)

### Semantic Graph Updates

```xml
<component id="backend.apps.courses.services" kind="service" path="lms-system/backend/apps/courses/services.py">
  <role>Бизнес-логика управления курсами и модулями</role>
  <depends-on ref="backend.apps.courses"/>
  <depends-on ref="backend.apps.users"/>
  <exposes>
    <api name="create_course" type="function" anchor="COURSE_CREATE">Создание курса</api>
    <api name="update_course" type="function" anchor="COURSE_UPDATE">Обновление курса</api>
    <api name="delete_course" type="function" anchor="COURSE_DELETE">Удаление курса</api>
    <api name="publish_course" type="function" anchor="COURSE_PUBLISH">Публикация курса</api>
    <api name="archive_course" type="function" anchor="COURSE_ARCHIVE">Архивация курса</api>
    <api name="create_module" type="function" anchor="MODULE_CREATE">Создание модуля</api>
    <api name="update_module" type="function" anchor="MODULE_UPDATE">Обновление модуля</api>
    <api name="delete_module" type="function" anchor="MODULE_DELETE">Удаление модуля</api>
    <api name="reorder_modules" type="function" anchor="MODULE_REORDER">Изменение порядка модулей</api>
    <api name="enroll_user" type="function" anchor="COURSE_ENROLL">Запись пользователя на курс</api>
  </exposes>
</component>

<edge id="api.courses.list" from="frontend.courses" to="backend.apps.courses.views.CourseViewSet" kind="http-rest">
  <endpoint>GET /api/courses/</endpoint>
</edge>

<edge id="api.courses.create" from="frontend.courses" to="backend.apps.courses.views.CourseViewSet" kind="http-rest">
  <endpoint>POST /api/courses/</endpoint>
</edge>

<edge id="api.courses.update" from="frontend.courses" to="backend.apps.courses.views.CourseViewSet" kind="http-rest">
  <endpoint>PUT/PATCH /api/courses/{id}/</endpoint>
</edge>

<edge id="api.courses.delete" from="frontend.courses" to="backend.apps.courses.views.CourseViewSet" kind="http-rest">
  <endpoint>DELETE /api/courses/{id}/</endpoint>
</edge>

<edge id="api.modules.create" from="frontend.courses" to="backend.apps.courses.views.ModuleViewSet" kind="http-rest">
  <endpoint>POST /api/modules/</endpoint>
</edge>
```

---

## 📝 Контракты

### COURSE_CREATE

**Функция**: `create_course`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: COURSE_CREATE
PURPOSE: Создать новый курс в системе.

@PreConditions:
- request.user.role == 'admin'
- title: непустая строка 1-255 символов
- description: строка (опционально)
- status: 'draft' (по умолчанию)

@PostConditions:
- при успехе: Course создан в БД, status='draft'
- при успехе: возвращается { id, title, description, status, created_at, updated_at }
- при ошибке (валидация): { error: "VALIDATION_ERROR", fields: [...] }
- при ошибке (недостаточно прав): { error: "PERMISSION_DENIED" }

@Invariants:
- новые курсы всегда в статусе 'draft'
- created_at и updated_at устанавливаются автоматически

@SideEffects:
- создаёт запись в таблице courses
- пишет лог создания курса (INFO)

@ForbiddenChanges:
- нельзя создать курс в статусе 'published' напрямую
- нельзя создать курс без title
```

### COURSE_UPDATE

**Функция**: `update_course`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: COURSE_UPDATE
PURPOSE: Обновить данные курса.

@PreConditions:
- request.user.role == 'admin'
- course_id: существующий курс
- доступны для обновления: title, description

@PostConditions:
- при успехе: курс обновлён, updated_at = now()
- при успехе: возвращается обновлённый курс
- при ошибке (курс не найден): { error: "COURSE_NOT_FOUND" }

@Invariants:
- updated_at обновляется при любом изменении
- статус не меняется через этот метод (используй publish/archive)

@SideEffects:
- обновляет запись в БД
- пишет лог обновления (INFO)

@ForbiddenChanges:
- нельзя менять статус через update (только через publish/archive)
- нельзя изменить id курса
```

### COURSE_DELETE

**Функция**: `delete_course`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: COURSE_DELETE
PURPOSE: Удалить курс из системы.

@PreConditions:
- request.user.role == 'admin'
- course_id: существующий курс

@PostConditions:
- при успехе: курс и все модули удалены (CASCADE)
- при успехе: возвращается { success: true }
- при ошибке (курс не найден): { error: "COURSE_NOT_FOUND" }

@Invariants:
- удаление курса каскадно удаляет все модули
- удаление курса каскадно удаляет записи на курс

@SideEffects:
- удаляет курс и связанные модули из БД
- удаляет course_enrollments
- пишет лог удаления (WARN)

@ForbiddenChanges:
- нельзя удалить курс с активными записями (или Confirm dialog?)
- защита от случайного удаления
```

### COURSE_PUBLISH

**Функция**: `publish_course`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: COURSE_PUBLISH
PURPOSE: Опубликовать курс для слушателей.

@PreConditions:
- request.user.role == 'admin'
- course_id: существующий курс со status='draft'
- курс имеет минимум 1 модуль

@PostConditions:
- при успехе: course.status = 'published'
- при ошибке (нет модулей): { error: "COURSE_MUST_HAVE_MODULES" }
- при ошибке (уже опубликован): молча success

@Invariants:
- можно публиковать только из status='draft' или 'archived'
- нельзя опубликовать пустой курс

@SideEffects:
- обновляет status курса
- пишет лог публикации (INFO)

@ForbiddenChanges:
- нельзя опубликовать курс без модулей
```

### COURSE_ARCHIVE

**Функция**: `archive_course`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: COURSE_ARCHIVE
PURPOSE: Архивировать курс (скрыть от слушателей).

@PreConditions:
- request.user.role == 'admin'
- course_id: существующий курс

@PostConditions:
- при успехе: course.status = 'archived'
- курс не виден слушателям
- существующие записи сохраняются

@Invariants:
- архивация не удаляет данные
- архивированный курс можно восстановить (publish)

@SideEffects:
- обновляет status курса
- пишет лог архивации (INFO)

@ForbiddenChanges:
- нельзя удалить данные при архивации
```

### MODULE_CREATE

**Функция**: `create_module`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: MODULE_CREATE
PURPOSE: Создать модуль в курсе.

@PreConditions:
- request.user.role == 'admin'
- course_id: существующий курс
- title: непустая строка 1-255 символов
- content_type: 'text' | 'pdf' | 'video'
- content_text: текст модуля (если content_type='text')
- content_url: URL файла/видео (если content_type='pdf' или 'video')

@PostConditions:
- при успехе: Module создан, order_num = max(order_num) + 1 для курса
- при успехе: возвращается { id, course_id, title, content_type, order_num, ... }
- при ошибке (валидация): { error: "VALIDATION_ERROR", fields: [...] }

@Invariants:
- order_num автоматически вычисляется для модулей курса
- модуль привязан к одному курсу

@SideEffects:
- создаёт запись в таблице modules
- пишет лог создания модуля (INFO)

@ForbiddenChanges:
- нельзя создать модуль без привязки к курсу
- нельзя вручную указать order_num (автоматический)
```

### MODULE_UPDATE

**Функция**: `update_module`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: MODULE_UPDATE
PURPOSE: Обновить содержимое модуля.

@PreConditions:
- request.user.role == 'admin'
- module_id: существующий модуль

@PostConditions:
- при успехе: модуль обновлён, updated_at = now()
- при ошибке (модуль не найден): { error: "MODULE_NOT_FOUND" }

@Invariants:
- order_n обновляется только через reorder_modules
- course_id не меняется

@SideEffects:
- обновляет запись в БД
- пишет лог обновления (INFO)

@ForbiddenChanges:
- нельзя изменить course_id модуля
- нельзя изменить order_num напрямую
```

### MODULE_DELETE

**Функция**: `delete_module`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: MODULE_DELETE
PURPOSE: Удалить модуль из курса.

@PreConditions:
- request.user.role == 'admin'
- module_id: существующий модуль

@PostConditions:
- при успехе: модуль удалён, связанные тесты удалены (CASCADE)
- при успехе: order_num оставшихся модулей пересчитан
- возвращается { success: true }

@Invariants:
- удаление модуля каскадно удаляет тесты
- порядок модулей пересчитывается после удаления

@SideEffects:
- удаляет модуль и связанные тесты
- пересчитывает order_num для оставшихся модулей
- пишет лог удаления (WARN)

@ForbiddenChanges:
- нельзя удалить модуль без пересчёта order_num
```

### MODULE_REORDER

**Функция**: `reorder_modules`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: MODULE_REORDER
PURPOSE: Изменить порядок модулей в курсе.

@PreConditions:
- request.user.role == 'admin'
- course_id: существующий курс
- module_ids: список id модулей в новом порядке

@PostConditions:
- при успехе: order_num модулей обновлены согласно новому порядку
- module_ids содержит все модули курса (ни одного пропущенного)

@Invariants:
- order_num уникален в рамках курса
- порядок модулей всегда непрерывный (1, 2, 3...)

@SideEffects:
- обновляет order_num для всех модулей курса
- пишет лог изменения порядка (INFO)

@ForbiddenChanges:
- нельзя пропустить модули курса
- нельзя указать модули другого курса
```

### COURSE_ENROLL

**Функция**: `enroll_user`
**Файл**: `backend/apps/courses/services.py`

```
ANCHOR: COURSE_ENROLL
PURPOSE: Записать пользователя на курс.

@PreConditions:
- request.user.role == 'admin'
- user_id: существующий активный пользователь
- course_id: существующий опубликованный курс (status='published')
- пользователь ещё не записан на курс

@PostConditions:
- при успехе: CourseEnrollment создан, status='active'
- при успехе: созданы UserProgress записи для всех модулей (status='not_started')
- при ошибке (уже записан): { error: "ALREADY_ENROLLED" }
- при ошибке (курс не опубликован): { error: "COURSE_NOT_PUBLISHED" }

@Invariants:
- один пользователь может быть записан на курс только один раз
- запись возможна только на опубликованный курс

@SideEffects:
- создаёт CourseEnrollment
- создаёт UserProgress для каждого модуля
- создаёт Notification для пользователя
- пишет лог записи на курс (INFO)

@ForbiddenChanges:
- нельзя записать на курс в статусе draft/archived
- нельзя создать дубликат записи
```

---

## ✅ Критерии приёма

### User Story 4: Создание курса

**Как** Администратор
**Я хочу** создать курс с названием и описанием
**Чтобы** начать формировать образовательную программу

**Acceptance Criteria**:
- [ ] Форма создания курса: title (обязательно), description (опционально)
- [ ] Курс создаётся в статусе 'draft'
- [ ] Автоматические поля: created_at, updated_at
- [ ] Валидация: title от 1 до 255 символов

### User Story 5: Редактирование курса

**Как** Администратор
**Я хочу** редактировать название и описание курса
**Чтобы** актуализировать информацию

**Acceptance Criteria**:
- [ ] Можно изменить title и description
- [ ] updated_at обновляется при сохранении
- [ ] Статус курса не меняется при редактировании

### User Story 6: Удаление курса

**Как** Администратор
**Я хочу** удалить курс
**Чтобы** убрать неактуальный контент

**Acceptance Criteria**:
- [ ] Курс удаляется из БД
- [ ] Все модули курса удаляются (CASCADE)
- [ ] Записи на курс удаляются (CASCADE)
- [ ] Confirm dialog перед удалением

### User Story 7: Добавление модуля

**Как** Администратор
**Я хочу** добавить модуль к курсу (текст, PDF-файл или видео-ссылка)
**Чтобы** наполнить курс контентом

**Acceptance Criteria**:
- [ ] Три типа контента: text (textarea), pdf (url), video (url)
- [ ] Модули автоматически получают order_num
- [ ] Модули отображаются в порядке добавления
- [ ] Title модуля обязателен

### User Story 8: Редактирование модуля

**Как** Администратор
**Я хочу** редактировать содержимое модуля
**Чтобы** актуализировать контент

**Acceptance Criteria**:
- [ ] Можно изменить title, content_text, content_url
- [ ] Нельзя изменить course_id модуля
- [ ] Нельзя изменить order_num напрямую

### User Story 9: Удаление модуля

**Как** Администратор
**Я хочу** удалить модуль из курса
**Чтобы** убрать неактуальный контент

**Acceptance Criteria**:
- [ ] Модуль удаляется с каскадным удалением тестов
- [ ] order_num оставшихся модулей пересчитывается
- [ ] Confirm dialog перед удалением

### User Story 13: Назначение слушателя на курс

**Как** Администратор
**Я хочу** назначить слушателя на курс
**Чтобы** предоставить доступ к обучению

**Acceptance Criteria**:
- [ ] Интерфейс выбора курса и пользователя
- [ ] Запись создаётся в CourseEnrollment
- [ ] Создаются UserProgress записи для всех модулей
- [ ] Пользователь получает уведомление о назначении

### User Story 14: Просмотр списка назначенных курсов

**Как** Слушатель
**Я хочу** просмотреть список назначенных мне курсов
**Чтобы** видеть доступные курсы

**Acceptance Criteria**:
- [ ] Список курсов со статусом записи
- [ ] Отображение прогресса по курсу
- [ ] Только опубликованные курсы

### User Story 23: Управление статусом курса

**Как** Администратор
**Я хочу** публиковать и архивировать курсы
**Чтобы** управлять доступностью курсов

**Acceptance Criteria**:
- [ ] Публикация: курс виден слушателям
- [ ] Архивация: курс скрыт от слушателей
- [ ] Нельзя опубликовать пустой курс (без модулей)

---

## 🧪 Тест-план

**Validation Report**: `plans/validation/V-FEAT-003.xml`

### Детерминированные тесты

**Unit-тесты**:
- [ ] `test_course_model_create` — создание курса
- [ ] `test_course_model_status_validation` — валидация статусов
- [ ] `test_module_model_create` — создание модуля
- [ ] `test_module_model_order_auto` — автоматический order_num
- [ ] `test_course_service_create_course` — сервис создания курса
- [ ] `test_course_service_update_course` — сервис обновления курса
- [ ] `test_course_service_delete_course` — сервис удаления курса
- [ ] `test_course_service_publish_course` — сервис публикации
- [ ] `test_course_service_archive_course` — сервис архивации
- [ ] `test_module_service_create_module` — сервис создания модуля
- [ ] `test_module_service_update_module` — сервис обновления модуля
- [ ] `test_module_service_delete_module` — сервис удаления модуля
- [ ] `test_module_service_reorder_modules` — сервис изменения порядка
- [ ] `test_enroll_service_success` — успешная запись на курс
- [ ] `test_enroll_service_already_enrolled` — повторная запись
- [ ] `test_enroll_service_course_not_published` — запись на неопубликованный курс

### Тесты траектории (log markers)

- [ ] `test_course_create_trajectory` — маркеры COURSE_CREATE
- [ ] `test_course_publish_trajectory` — маркеры COURSE_PUBLISH
- [ ] `test_module_create_trajectory` — маркеры MODULE_CREATE
- [ ] `test_module_reorder_trajectory` — маркеры MODULE_REORDER
- [ ] `test_enroll_trajectory` — маркеры COURSE_ENROLL

### Интеграционные тесты

**API Endpoints**:
- [ ] `test_api_course_crud` — CRUD курсов через API
- [ ] `test_api_module_crud` — CRUD модулей через API
- [ ] `test_api_course_publish` — публикация через API
- [ ] `test_api_module_reorder` — изменение порядка через API
- [ ] `test_api_enroll_user` — запись на курс через API
- [ ] `test_api_enrolled_courses_list` — список курсов слушателя

**E2E**:
- [ ] `test_e2e_course_create_flow` — сценарий создания курса
- [ ] `test_e2e_module_create_flow` — сценарий создания модуля
- [ ] `test_e2e_course_publish_flow` — сценарий публикации курса

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
- Validation Report: `plans/validation/V-FEAT-003.xml`
- Code:
  - `lms-system/backend/apps/courses/models.py`
  - `lms-system/backend/apps/courses/views.py`
  - `lms-system/backend/apps/courses/services.py`
  - `lms-system/frontend/js/courses.js`
  - `lms-system/frontend/courses.html`
- Tests:
  - `lms-system/backend/tests/unit/test_courses.py`
  - `lms-system/backend/tests/integration/test_courses_api.py`
