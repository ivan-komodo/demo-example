---
name: grace-verification
description: Прогон тестов и проверка работоспособности реализованной фичи
agent: verification-reviewer
---

# GRACE Verification

Запускает тесты, проверяет log-маркеры и формирует Verification Report.

## Что делает этот скилл

1. Запускает все тесты (unit, integration, e2e)
2. Парсит логи на наличие обязательных маркеров
3. Проверяет покрытие тестами
4. Формирует отчёт верификации
5. Обновляет статус фичи

## Параметры

```bash
/kilo skill grace-verification FEAT-XXX

/kilo skill grace-verification --all
```

- `$1` — ID фичи (например, FEAT-001)
- `--all` — проверить все фичи со статусом `implemented`

## Процесс верификации

### Шаг 1: Загрузка данных

Прочитай:
- `plans/features/FEAT-XXX.md` — Feature Spec
- `plans/validation/V-FEAT-XXX.xml` — Validation Report
- `.kilocode/semantic-graph.xml` — Архитектура

### Шаг 2: Определение тестов

Из Validation Report определи:

1. **Unit тесты** (Level 1: deterministic):
   - `tests/unit/test_{module}.py`
   - Запускаются для каждой функции

2. **Marker тесты** (Level 2: trajectory):
   - `tests/unit/test_{module}_markers.py`
   - Проверяют наличие лог-маркеров

3. **Integration тесты** (Level 3: E2E):
   - `tests/integration/test_{module}_flow.py`
   - Запускают end-to-end сценарии

### Шаг 3: Запуск тестов

#### 3.1. Unit тесты

```bash
pytest tests/unit/test_{feature}.py -v --tb=short
```

Парсинг результатов:
```
================ test session starts ================
collected 15 items

tests/unit/test_auth_login.py::test_auth_login_success PASSED
tests/unit/test_auth_login.py::test_auth_login_invalid_credentials PASSED
tests/unit/test_auth_login.py::test_auth_login_rate_limited FAILED

================= 2 passed, 1 failed =================
```

Извлеки:
- `passed`: количество прошедших
- `failed`: количество упавших
- `errors`: детали упавших тестов

#### 3.2. Integration тесты

```bash
pytest tests/integration/test_{feature}_flow.py -v
```

#### 3.3. E2E тесты

```bash
pytest tests/e2e/test_{feature}_e2e.py -v
```

### Шаг 4: Проверка log-маркеров

Для каждого ANCHOR из Validation Report:

1. Запусти тест с перехватом логов
2. Проверь наличие обязательных маркеров:

| Point | Проверка |
|-------|----------|
| ENTRY | `[MODULE][FUNCTION][ANCHOR_ID][ENTRY]` |
| EXIT | `[MODULE][FUNCTION][ANCHOR_ID][EXIT]` |
| CHECK | Опционально |
| DECISION | Опционально |
| ERROR | Если ожидается ошибка |

Пример проверки:

```python
def verify_log_markers(logs, anchor_id, required_markers):
    found = {}
    missing = []
    
    for marker in required_markers:
        pattern = f"\\[{anchor_id}\\]\\[{marker}\\]"
        if re.search(pattern, logs):
            found[marker] = True
        elif marker in ["ENTRY", "EXIT"]:  # Required
            missing.append(marker)
    
    return found, missing
```

**Результат**:

| ANCHOR | Required | Found | Missing | Status |
|--------|----------|-------|---------|--------|
| AUTH_LOGIN | ENTRY, EXIT, CHECK | ENTRY, EXIT | CHECK | ❌ |
| AUTH_GENERATE_TOKENS | ENTRY, EXIT | ENTRY, EXIT | - | ✅ |

### Шаг 5: Анализ покрытия

```bash
pytest --cov=backend/apps/{module} --cov-report=term-missing --cov-report=json
```

Парсинг:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Statements | 70% | - | - |
| Branches | 60% | - | - |
| Functions | 80% | - | - |

Минимальные требования:
- Statements: ≥ 70%
- Branches: ≥ 60%
- Functions: ≥ 80%

### Шаг 6: Формирование Verification Report

Создай `reports/verification-{TIMESTAMP}-FEAT-XXX.md`:

```markdown
# Verification Report

**Feature**: FEAT-XXX
**Name**: {Feature Name}
**Date**: 2026-04-14T16:22:00
**Status**: {passed|failed}

---

## 📊 Test Results Summary

| Level | Total | Passed | Failed | Status |
|-------|-------|--------|--------|--------|
| Unit (Deterministic) | 15 | 14 | 1 | ❌ |
| Integration (E2E) | 5 | 5 | 0 | ✅ |

---

## 🧪 Detailed Test Results

### Unit Tests

**Total**: 15
**Passed**: 14
**Failed**: 1

#### Failed Tests

1. **test_auth_login_rate_limited**
   - File: `tests/unit/test_auth_login.py:45`
   - Error: `AssertionError: Expected 429, got 200`
   - ANCHOR: `AUTH_LOGIN`
   - Issue: Rate limiting не работает

### Integration Tests

**Total**: 5
**Passed**: 5
**Failed**: 0

All integration tests passed successfully.

---

## 🔍 Log Markers Check

### AUTH_LOGIN

| Point | Required | Found | Status |
|-------|----------|-------|--------|
| ENTRY | ✅ | ✅ | ✅ |
| EXIT | ✅ | ✅ | ✅ |
| CHECK | ⚠️ | ✅ | ✅ |
| DECISION | ⚠️ | ❌ | ❌ |

**Issue**: Missing DECISION marker in AUTH_LOGIN

### AUTH_GENERATE_TOKENS

| Point | Required | Found | Status |
|-------|----------|-------|--------|
| ENTRY | ✅ | ✅ | ✅ |
| EXIT | ✅ | ✅ | ✅ |

**Status**: ✅ All required markers present

---

## 📈 Coverage Report

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Statements | 70% | 82% | ✅ |
| Branches | 60% | 78% | ✅ |
| Functions | 80% | 85% | ✅ |

**Missing Coverage**:
- `backend/apps/users/services.py:145` — rate limiting logic

---

## 🐛 Issues Found

### Issue 1: Test Failure

**ID**: TEST-001
**Severity**: Critical
**Test**: `test_auth_login_rate_limited`
**ANCHOR**: `AUTH_LOGIN`
**Description**: Rate limiting не работает корректно
**Expected**: HTTP 429 при превышении лимита
**Actual**: HTTP 200, запрос проходит

**Recommendation**: Проверить `@PreConditions` контракта AUTH_LOGIN — rate limit check должен быть в начале функции.

### Issue 2: Missing Log Marker

**ID**: LOG-001
**Severity**: Major
**ANCHOR**: `AUTH_LOGIN`
**Description**: Отсутствует DECISION marker при rate limiting

**Recommendation**: Добавить `log_line(..., "DECISION", {...})` перед return при rate limit блокировке.

---

## ✅ Sign-off Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All required log markers present
- [ ] Coverage meets minimum requirements
- [ ] No critical issues open

---

## 📋 Next Steps

1. Исправить Issue TEST-001 через `grace-fix`
2. Добавить недостающие log-маркеры
3. Перезапустить `grace-verification`
```

### Шаг 7: Обновление статуса

Обнови `plans/features/FEAT-XXX.md`:

```markdown
## 📊 Статус реализации

| Этап | Статус | Дата | Комментарий |
|------|--------|------|-------------|
| Planning | ✅ | 2026-04-14 | |
| Validation | ✅ | 2026-04-14 | |
| Implementation | ✅ | 2026-04-14 | |
| Verification | ❌ | 2026-04-14 | 1 test failed, 1 marker missing |
```

Установи статус:
- Если все тесты PASS: `verified`
- Если есть FAIL: `failed-verification`

## Пример использования

```bash
# Верификация конкретной фичи
/kilo skill grace-verification FEAT-001

# Верификация всех реализованных фич
/kilo skill grace-verification --all
```

## Результат

После выполнения:

- [ ] Все тесты запущены
- [ ] Log-маркеры проверены
- [ ] Покрытие определено
- [ ] Verification Report создан
- [ ] Статус фичи обновлён

## Критерии успеха

Верификация считается успешной если:

- ✅ **100% Unit тестов** проходят
- ✅ **100% Integration тестов** проходят
- ✅ **Все обязательные log-маркеры** присутствуют
- ✅ **Покрытие кода** соответствует требованиям

## Что делать после

1. Если `passed`:
   - Фича готова к релизу
   - Можно работать над следующей фичей

2. Если `failed`:
   - Проанализируй Issues в Verification Report
   - Запусти `grace-fix BUG-XXX` для каждой проблемы

## Типичные проблемы

| Проблема | Диагностика | Решение |
|----------|-------------|---------|
| Unit тест падает | Stack trace → ANCHOR → Контракт | grace-fix |
| Нет log-маркера | Parse logs → Найти ANCHOR в коде | Добавить log_line |
| Низкое покрытие | Coverage report → Найти пропуски | Добавить тесты |
| Integration тест падает | E2E scenario steps → Найти где ломается | grace-fix |
