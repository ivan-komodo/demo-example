# Feature: Тесты и попытки прохождения

> **ID**: FEAT-004
> **Status**: validated
> **Created**: 2026-04-14
> **Updated**: 2026-04-14
> **Depends on**: FEAT-001, FEAT-003

---

## 📋 Описание

CRUD операции для тестов (вопросы с вариантами ответов). Поддержка трёх типов вопросов: один правильный ответ, несколько правильных, открытый ответ. Система попыток с ограничением (максимум 3 попытки). Проверка ответов и расчёт score.

---

## 🎯 Цель

Позволить создавать тесты для модулей и проходить их пользователям. Тесты проверяют усвоение материала и влияют на прогресс.

---

## 📦 Компоненты

### Новые компоненты

| Компонент | Тип | Путь | Описание |
|-----------|-----|------|----------|
| Quiz | model | `backend/apps/quizzes/models.py` | Вопрос теста |
| QuizOption | model | `backend/apps/quizzes/models.py` | Вариант ответа |
| QuizAttempt | model | `backend/apps/quizzes/models.py` | Попытка прохождения |
| QuizAnswer | model | `backend/apps/quizzes/models.py` | Ответ пользователя |
| QuizViewSet | viewset | `backend/apps/quizzes/views.py` | CRUD тестов |
| QuizAttemptViewSet | viewset | `backend/apps/quizzes/views.py` | Попытки прохождения |
| QuizService | service | `backend/apps/quizzes/services.py` | Бизнес-логика тестов |
| quizzes.js | module | `frontend/js/quizzes.js` | Работа с тестами на клиенте |
| quiz.html | page | `frontend/quiz.html` | Страница прохождения теста |

### Изменяемые компоненты

| Компонент | Изменение |
|-----------|-----------|
| `backend/config/urls.py` | Добавление маршрутов quizzes |
| `frontend/js/main.js` | Инициализация QuizManager |

---

## 🔗 Связи

### Зависимости

- Зависит от: FEAT-001 (User), FEAT-003 (Module)
- Зависимые: FEAT-005 (Progress)

### Semantic Graph Updates

```xml
<component id="backend.apps.quizzes.services" kind="service" path="lms-system/backend/apps/quizzes/services.py">
  <role>Бизнес-логика тестов и попыток</role>
  <depends-on ref="backend.apps.quizzes"/>
  <depends-on ref="backend.apps.courses"/>
  <depends-on ref="backend.apps.users"/>
  <exposes>
    <api name="create_quiz" type="function" anchor="QUIZ_CREATE">Создание вопроса</api>
    <api name="update_quiz" type="function" anchor="QUIZ_UPDATE">Обновление вопроса</api>
    <api name="delete_quiz" type="function" anchor="QUIZ_DELETE">Удаление вопроса</api>
    <api name="start_attempt" type="function" anchor="QUIZ_ATTEMPT_START">Начало попытки</api>
    <api name="submit_attempt" type="function" anchor="QUIZ_ATTEMPT_SUBMIT">Отправка ответов</api>
    <api name="calculate_score" type="function" anchor="QUIZ_SCORE_CALC">Расчёт баллов</api>
  </exposes>
</component>
```

---

## 📝 Контракты

### QUIZ_CREATE

**Функция**: `create_quiz`
**Файл**: `backend/apps/quizzes/services.py`

```
ANCHOR: QUIZ_CREATE
PURPOSE: Создать вопрос теста для модуля.

@PreConditions:
- request.user.role == 'admin'
- module_id: существующий модуль
- question: непустая строка
- question_type: 'single' | 'multiple' | 'open'
- options: список вариантов (для single/multiple), минимум 2 варианта
- for single/multiple: минимум 1 вариант с is_correct=True
- order_num: автоматически (max + 1)

@PostConditions:
- при успехе: Quiz создан, QuizOptions созданы
- возвращается { id, module_id, question, question_type, options: [...], order_num }
- при ошибке (валидация): { error: "VALIDATION_ERROR", fields: [...] }

@Invariants:
- для open типа options не требуются
- для single/multiple: минимум 2 варианта, минимум 1 правильный

@SideEffects:
- создаёт Quiz и QuizOptions
- пишет лог создания (INFO)

@ForbiddenChanges:
- нельзя создать вопрос без правильного ответа (кроме open)
- нельзя создать вопрос с одним вариантом (для single/multiple)
```

### QUIZ_ATTEMPT_START

**Функция**: `start_attempt`
**Файл**: `backend/apps/quizzes/services.py`

```
ANCHOR: QUIZ_ATTEMPT_START
PURPOSE: Начать попытку прохождения теста.

@PreConditions:
- пользователь авторизован
- quiz_id: существующий вопрос
- пользователь записан на курс, к которому относится модуль
- attempt_number <= 3 (максимум 3 попытки)
- предыдущие попытки завершены (completed_at IS NOT NULL)

@PostConditions:
- при успехе: QuizAttempt создан, attempt_number = max + 1
- возвращается { attempt_id, quiz, attempt_number, max_attempts: 3 }
- при ошибке (превышен лимит): { error: "MAX_ATTEMPTS_EXCEEDED" }
- при ошибке (не записан на курс): { error: "NOT_ENROLLED" }

@Invariants:
- максимум 3 попытки на тест
- нельзя начать новую попытку, пока предыдущая не завершена

@SideEffects:
- создаёт QuizAttempt
- пишет лог начала попытки (DEBUG)

@ForbiddenChanges:
- нельзя превысить лимит в 3 попытки
- нельзя начать 4-ю попытку
```

### QUIZ_ATTEMPT_SUBMIT

**Функция**: `submit_attempt`
**Файл**: `backend/apps/quizzes/services.py`

```
ANCHOR: QUIZ_ATTEMPT_SUBMIT
PURPOSE: Отправить ответы и завершить попытку.

@PreConditions:
- attempt_id: существующая попытка пользователя
- attempt.completed_at IS NULL (попытка активна)
- answers: список ответов
  - для single: { quiz_option_id }
  - для multiple: { quiz_option_ids: [...] }
  - для open: { text: "..." }

@PostConditions:
- при успехе: QuizAnswer созданы, score рассчитан
- attempt.completed_at = now()
- attempt.score = calculated_score
- возвращается { attempt_id, score, correct_count, total_count, answers: [...] }
- обновлён UserProgress для модуля

@Invariants:
- score = (correct_answers / total_questions) * 100
- для multiple: вопрос считается правильным, если выбраны все правильные и ни одного неправильного

@SideEffects:
- создаёт QuizAnswers
- обновляет QuizAttempt (score, completed_at)
- обновляет UserProgress
- пишет лог завершения попытки (INFO)

@ForbiddenChanges:
- нельзя изменить отправленные ответы после завершения
- нельзя пересчитать score после завершения
```

### QUIZ_SCORE_CALC

**Функция**: `calculate_score`
**Файл**: `backend/apps/quizzes/services.py`

```
ANCHOR: QUIZ_SCORE_CALC
PURPOSE: Рассчитать баллы за попытку.

@PreConditions:
- attempt_id: существующая завершённая попытка

@PostConditions:
- возвращается score от 0.00 до 100.00
- single: правильный = 1, неправильный = 0
- multiple: все правильные + нет неправильных = 1, иначе = 0
- open: сравнение с эталоном (или ручная проверка)

@Invariants:
- score = (correct_questions / total_questions) * 100
- округление до 2 знаков

@SideEffects:
- нет побочных эффектов

@ForbiddenChanges:
- нельзя изменить формулу расчёта score
- нельзя дать больше 100 баллов
```

---

## ✅ Критерии приёма

### User Story 10: Добавление теста

**Как** Администратор
**Я хочу** добавить тест к модулю с вопросами и вариантами ответов
**Чтобы** проверять усвоение материала

**Acceptance Criteria**:
- [ ] Три типа вопросов: single (один правильный), multiple (несколько), open (открытый)
- [ ] Для single/multiple: минимум 2 варианта ответа, минимум 1 правильный
- [ ] Автоматический order_num для вопросов
- [ ] Валидация: вопрос обязателен

### User Story 11: Редактирование теста

**Как** Администратор
**Я хочу** редактировать вопрос и варианты ответов
**Чтобы** актуализировать тест

**Acceptance Criteria**:
- [ ] Можно изменить вопрос, тип, варианты ответов
- [ ] При изменении типа вопроса валидация обновляется

### User Story 12: Удаление теста

**Как** Администратор
**Я хочу** удалить тест
**Чтобы** убрать неактуальный вопрос

**Acceptance Criteria**:
- [ ] Тест удаляется с каскадным удалением попыток
- [ ] Confirm dialog перед удалением

### User Story 15: Прохождение теста

**Как** Слушатель
**Я хочу** пройти тест и ответить на вопросы
**Чтобы** проверить свои знания

**Acceptance Criteria**:
- [ ] Максимум 3 попытки на тест
- [ ] Для single: radio buttons (один ответ)
- [ ] Для multiple: checkboxes (несколько ответов)
- [ ] Для open: textarea
- [ ] После отправки: показ результата (score)

### User Story 18: Сохранение ответов

**Как** Система
**Я хочу** сохранить ответы пользователя на тест
**Чтобы** зафиксировать результат

**Acceptance Criteria**:
- [ ] Ответы сохраняются в QuizAnswer
- [ ] Score сохраняется в QuizAttempt
- [ ] UserProgress обновляется

---

## 🧪 Тест-план

**Validation Report**: `plans/validation/V-FEAT-004.xml`

### Детерминированные тесты

- [ ] `test_quiz_model_create` — создание вопроса
- [ ] `test_quiz_option_model` — варианты ответа
- [ ] `test_quiz_attempt_model` — попытка прохождения
- [ ] `test_quiz_service_create_single` — single тип
- [ ] `test_quiz_service_create_multiple` — multiple тип
- [ ] `test_quiz_service_create_open` — open тип
- [ ] `test_quiz_service_start_attempt` — начало попытки
- [ ] `test_quiz_service_max_attempts` — лимит попыток
- [ ] `test_quiz_service_submit_single` — отправка single
- [ ] `test_quiz_service_submit_multiple` — отправка multiple
- [ ] `test_quiz_service_submit_open` — отправка open
- [ ] `test_quiz_service_score_calc` — расчёт score

### Тесты траектории

- [ ] `test_quiz_create_trajectory` — маркеры QUIZ_CREATE
- [ ] `test_attempt_start_trajectory` — маркеры QUIZ_ATTEMPT_START
- [ ] `test_attempt_submit_trajectory` — маркеры QUIZ_ATTEMPT_SUBMIT

### Интеграционные тесты

- [ ] `test_api_quiz_crud` — CRUD тестов
- [ ] `test_api_attempt_flow` — полный цикл попытки
- [ ] `test_api_max_attempts` — лимит попыток через API

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

- Depends on: `plans/features/FEAT-001.md`, `plans/features/FEAT-003.md`
- Validation Report: `plans/validation/V-FEAT-004.xml`
- Code:
  - `lms-system/backend/apps/quizzes/models.py`
  - `lms-system/backend/apps/quizzes/views.py`
  - `lms-system/backend/apps/quizzes/services.py`
  - `lms-system/frontend/js/quizzes.js`
