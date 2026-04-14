# GRACE Artifacts Documentation

Документация по всем артефактам методологии GRACE (Generic Rule-based Architecture for Contracted Execution).

---

## 📁 Структура артефактов

```
plans/
├── features/           # Feature Specifications (ТЗ фич)
│   ├── FEAT-001.md
│   ├── FEAT-002.md
│   └── ...
├── validation/         # Validation Reports (Отчёты валидации)
│   ├── V-FEAT-001.xml
│   ├── V-FEAT-002.xml
│   └── ...

reports/
├── verification-{TIMESTAMP}-FEAT-XXX.md  # Verification Reports
├── fix-{TIMESTAMP}-BUG-XXX.md            # Fix Reports
└── ...

.kilo/
├── agent/              # Агенты GRACE
├── skill/              # Скиллы GRACE
└── templates/          # Шаблоны артефактов
```

---

## 📝 Типы артефактов

### 1. Feature Specification

**Файл**: `plans/features/FEAT-XXX.md`

**Назначение**: Исчерпывающее ТЗ фичи с компонентами, контрактами и критериями приёма.

**Создаётся**: Скиллом `grace-plan`

**Шаблон**: `.kilo/templates/feature-spec-template.md`

**Обязательные секции**:

| Секция | Описание | Критичность |
|--------|----------|-------------|
| Описание | Краткое описание фичи | ✅ Обязательно |
| Цель | Бизнес-цель | ✅ Обязательно |
| Компоненты | Новые и изменяемые компоненты | ✅ Обязательно |
| Контракты | ANCHOR + контракты для каждой функции | ✅ Обязательно |
| User Stories | Критерии приёма | ✅ Обязательно |
| Тест-план | Ссылка на Validation Report | ⚠️ Рекомендуется |

**Статусы**:

| Статус | Описание | Следующий шаг |
|--------|----------|---------------|
| `draft` | Начальный черновик | Завершить планирование |
| `planning` | В процессе планирования | Завершить `grace-plan` |
| `validated` | Прошёл валидацию | Запустить `grace-execute` |
| `implemented` | Реализован | Запустить `grace-verification` |
| `verified` | Верифицирован (тесты PASS) | Готов к релизу |
| `failed-verification` | Тесты FAIL | Запустить `grace-fix` |

---

### 2. Validation Report

**Файл**: `plans/validation/V-FEAT-XXX.xml`

**Назначение**: Результат валидации Feature Spec + тест-сценарии 3 уровней.

**Создаётся**: Скиллом `grace-validate-plan`

**Шаблон**: `.kilo/templates/validation-report-template.xml`

**Обязательные секции**:

| Секция | Описание |
|--------|----------|
| `<status>` | pass / fail / incomplete |
| `<completeness>` | Проверки полноты всех секций |
| `<contracts>` | Проверки контрактов |
| `<consistency>` | Проверки консистентности |
| `<test-scenarios>` | Тест-сценарии 3 уровней |
| `<recommendations>` | Рекомендации по улучшению |

**Тест-сценарии**:

| Level | Тип | Назначение |
|-------|-----|------------|
| 1 | deterministic | Проверка постусловий (assert expectations) |
| 2 | trajectory | Проверка log-маркеров |
| 3 | integration | E2E сценарии |

**Статус**:

| Статус | Условие |
|--------|---------|
| `pass` | Все секции заполнены, контракты корректны, нет противоречий |
| `fail` | Есть критичные проблемы |
| `incomplete` | Не все секции заполнены |

---

### 3. Verification Report

**Файл**: `reports/verification-{TIMESTAMP}-FEAT-XXX.md`

**Назначение**: Результат прогона тестов + проверка log-маркеров + покрытие.

**Создаётся**: Скиллом `grace-verification`

**Обязательные секции**:

| Секция | Описание |
|--------|----------|
| Test Results | Результаты unit/integration тестов |
| Log Markers Check | Проверка наличия обязательных маркеров |
| Coverage Report | Покрытие кода тестами |
| Issues | Найденные проблемы |

**Критерии успеха**:

- ✅ 100% unit тестов проходят
- ✅ 100% integration тестов проходят
- ✅ Все обязательные log-маркеры присутствуют
- ✅ Покрытие: Statements ≥ 70%, Functions ≥ 80%

---

### 4. Fix Report

**Файл**: `reports/fix-{TIMESTAMP}-BUG-XXX.md`

**Назначение**: Документация исправления бага.

**Создаётся**: Скиллом `grace-fix`

**Обязательные секции**:

| Секция | Описание |
|--------|----------|
| Problem | Описание проблемы |
| Root Cause | Анализ через ANCHOR и контракт |
| Fix | Категория и описание исправления |
| Tests Added | Regression tests |
| Updated Markers | Изменения в log-маркерах |

**Категории исправлений**:

| Категория | Описание | Действие |
|-----------|----------|----------|
| A | Исправление реализации | Код правится под контракт |
| B | Исправление контракта | Контракт дополняется + согласование |
| C | Исправление теста | Тест правится под контракт |

---

## 🔄 Workflow с артефактами

```
┌────────────────────┐
│  grace-plan        │ → plans/features/FEAT-XXX.md
└─────────┬──────────┘
          │
          v
┌────────────────────┐
│  grace-validate    │ → plans/validation/V-FEAT-XXX.xml
└─────────┬──────────┘
          │
          v
┌────────────────────┐
│  grace-execute     │ → Code + Tests
└─────────┬──────────┘
          │
          v
┌────────────────────┐
│  grace-verification│ → reports/verification-TIMESTAMP-FEAT-XXX.md
└─────────┬──────────┘
          │
          v
     ┌────┴────┐
   PASS      FAIL
     │         │
     v         v
   DONE   ┌────────────┐
          │ grace-fix  │ → reports/fix-TIMESTAMP-BUG-XXX.md
          └─────┬──────┘
                │
                v
          ┌──────────────┐
          │ verification │ (повторный)
          └──────────────┘
```

---

## 📖 Naming Conventions

### Feature ID

**Формат**: `FEAT-{NUMBER}`

**Примеры**:
- FEAT-001
- FEAT-002
- FEAT-003

**Правило**: Инкрементальный номер, нумерация ведётся в `plans/features/`.

### Bug ID

**Формат**: `BUG-{NUMBER}`

**Примеры**:
- BUG-001
- BUG-002

**Правило**: Инкрементальный номер, нумерация ведётся в Verification Reports.

### Test Scenario ID

**Формат**: `SC-{NUMBER}`

**Примеры**:
- SC-001, SC-002 — детерминированные тесты
- SC-010, SC-011 — траекторные тесты
- SC-020, SC-021 — интеграционные тесты

**Правило**:
- SC-001...SC-009 — Level 1 (deterministic)
- SC-010...SC-019 — Level 2 (trajectory)
- SC-020...SC-029 — Level 3 (integration)

### ANCHOR ID

**Формат**: `UPPER_SNAKE_CASE`

**Примеры**:
- AUTH_LOGIN
- AUTH_REGISTER
- COURSE_CREATE
- QUIZ_SUBMIT

**Правило**: Уникальный в рамках проекта, осмысленное имя.

---

## 🔍 Поиск артефактов

### По фиче

```bash
# Feature Spec
ls plans/features/FEAT-001.md

# Validation Report
ls plans/validation/V-FEAT-001.xml

# Verification Reports
ls reports/verification-*-FEAT-001.md

# Fix Reports (если были баги)
ls reports/fix-*-BUG-*.md
```

### По ANCHOR

```bash
# Найти все упоминания ANCHOR
grep -r "AUTH_LOGIN" plans/
grep -r "AUTH_LOGIN" reports/

# Найти в коде
grep -r "ANCHOR: AUTH_LOGIN" backend/
```

### По статусу

```bash
# Все фичи со статусом implemented
grep -l "status: implemented" plans/features/*.md

# Все фичи со статусом failed-verification
grep -l "status: failed-verification" plans/features/*.md
```

---

## 📊 Метрики и отчётность

### Дашборд по фичам

Собери статистику по всем фичам:

```python
features = glob("plans/features/*.md")

stats = {
    "total": len(features),
    "draft": count_status(features, "draft"),
    "planning": count_status(features, "planning"),
    "validated": count_status(features, "validated"),
    "implemented": count_status(features, "implemented"),
    "verified": count_status(features, "verified"),
    "failed": count_status(features, "failed-verification"),
}
```

### Покрытие тестами

Из Verification Reports:

```python
coverage = []
for report in glob("reports/verification-*.md"):
    data = parse_verification_report(report)
    coverage.append({
        "feature": data.feature_id,
        "statements": data.statements_coverage,
        "branches": data.branches_coverage,
        "functions": data.functions_coverage,
    })
```

### Общие баги

Из Fix Reports:

```python
bugs = []
for report in glob("reports/fix-*.md"):
    data = parse_fix_report(report)
    bugs.append({
        "bug_id": data.bug_id,
        "feature": data.feature_id,
        "category": data.category,
        "anchor": data.anchor_id,
    })
```

---

## 🛠 Инструменты работы

### Создание

| Артефакт | Скилл | Команда |
|----------|-------|---------|
| Feature Spec | grace-plan | `/kilo skill grace-plan "описание"` |
| Validation Report | grace-validate | `/kilo skill grace-validate FEAT-XXX` |
| Verification Report | grace-verification | `/kilo skill grace-verification FEAT-XXX` |
| Fix Report | grace-fix | `/kilo skill grace-fix BUG-XXX` |

### Обновление

| Артефакт | Когда обновлять |
|----------|-----------------|
| Feature Spec | При доработке фичи |
| Validation Report | При изменении требований |
| Verification Report | При каждом прогоне тестов |
| Fix Report | При исправлении бага |

### Архивация

Артефакты не удаляются, а архивируются:

```bash
# Архивация выполненной фичи
mkdir -p archive/FEAT-001/
mv plans/features/FEAT-001.md archive/FEAT-001/
mv plans/validation/V-FEAT-001.xml archive/FEAT-001/
mv reports/*-FEAT-001.md archive/FEAT-001/
```

---

## 📚 Связанные материалы

- [Semantics Rules](.kilocode/rules/README.md) — правила методологии
- [Semantic Graph](.kilocode/semantic-graph.xml) — архитектура компонентов
- [Templates](.kilo/templates/) — шаблоны артефактов

---

*Документация актуализирована: 2026-04-14*
