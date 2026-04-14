---
name: grace-fix
description: Исправление багов с сохранением семантики контрактов
agent: fixer
---

# GRACE Fix

Исправляет баги, анализируя нарушения контрактов и сохраняя семантику кода.

## Что делает этот скилл

1. Анализирует Verification Report или принимает описание бага
2. Локализует проблему через ANCHOR и log-маркеры
3. Проверяет контракт функции на нарушения
4. Исправляет код, сохраняя семантику контракта
5. Обновляет тестовые сценарии
6. Добавляет regression tests
7. Обновляет артефакты

## Параметры

```bash
/kilo skill grace-fix BUG-XXX

/kilo skill grace-fix --from-report reports/verification-TIMESTAMP-FEAT-XXX.md

/kilo skill grace-fix "описание бага"
```

- `$1` — ID бага (например, BUG-001)
- `--from-report` — путь к Verification Report
- `$ARGUMENTS` — описание бага (если нет отчёта)

## Процесс исправления

### Шаг 1: Загрузка данных

Если указан BUG-XXX:
1. Найди баг в Verification Report
2. Загрузи связанный Feature Spec

Если указан `--from-report`:
1. Парсинг Verification Report
2. Извлечение issues

Если указано описание:
1. Создай временную запись бага
2. Определи связанную фичу

### Шаг 2: Локализация проблемы

**Ключевой принцип**: Каждый баг локализуется через ANCHOR.

#### 2.1. Найти ANCHOR

Из стека вызовов или логов найди ANCHOR:

```
Traceback (most recent call last):
  File "tests/unit/test_auth.py", line 45, in test_rate_limited
    result = login(email, password)
  File "backend/apps/users/services.py", line 67, in login
    # [START_AUTH_LOGIN] ← ANCHOR найден
```

Или из логов:

```
[2026-04-14 16:22:00] [auth][login][AUTH_LOGIN][ENTRY] {...}
[2026-04-14 16:22:00] [auth][login][AUTH_LOGIN][CHECK] {"check": "rate_limit", "result": false}
[2026-04-14 16:22:00] [auth][login][AUTH_LOGIN][EXIT] {"result": "success"} ← BUG: должно быть rejected
```

#### 2.2. Прочитать контракт

Прочитай контракт ANCHOR из:
1. Кода (комментарий)
2. Feature Spec

```python
"""
ANCHOR: AUTH_LOGIN
PURPOSE: Аутентификация пользователя по email и паролю.

@PreConditions:
- email: валидный email
- password: непустой
- НЕ превышен rate limit ← ЭТО ПРОВЕРИТЬ!

@PostConditions:
- при успехе: { access_token, refresh_token }
- при rate limit: { error: "RATE_LIMITED" } ← ЭТО НЕ РАБОТАЕТ!

@Invariants:
- пароль не возвращается

@SideEffects:
- создаёт session
- логирует попытку

@ForbiddenChanges:
- нельзя убрать rate limiting
"""
```

#### 2.3. Анализ контракта

Проверь:

| Секция | Вопрос | Результат |
|--------|--------|-----------|
| @PreConditions | Выполнены ли все предусловия? | ❌ rate limit не проверяется |
| @PostConditions | Обеспечены ли все постусловия? | ❌ при rate limit возвращается success |
| @Invariants | Нарушены ли инварианты? | ✅ не нарушены |
| @ForbiddenChanges | Затронуты ли запреты? | ✅ не затронуты |

**Вывод**: Нарушено предусловие и постусловие.

### Шаг 3: Определение категории исправления

#### Категория A: Исправление реализации

**Когда**: Контракт корректен, код не соответствует контракту.

**Пример**:
- Контракт: "при rate limit: return { error: RATE_LIMITED }"
- Код: "пропускает запрос дальше"

**Решение**: Исправить код под контракт.

#### Категория B: Исправление контракта

**Когда**: Контракт неполон, случай не учтён.

**Пример**:
- Контракт: не учитывает случай "пользователь заблокирован"
- Код: возвращает непонятную ошибку

**Решение**: 
1. Дополни контракт новым кейсом
2. Согласуй с бизнесом
3. Исправь код

**Требуется**: Обновить Feature Spec + Validation Report.

#### Категория C: Исправление теста

**Когда**: Тест ожидает поведение не из контракта.

**Пример**:
- Контракт: "при ошибке: { error: string }"
- Тест: "expect(result).toBeNull()"

**Решение**: Исправить тест под контракт.

**Проверь**: Что контракт верен.

### Шаг 4: Исправление кода

#### 4.1. Категория A (исправление реализации)

```python
# [START_AUTH_LOGIN]

def login(email: str, password: str) -> dict:
    log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "ENTRY", {
        "email": email,
    })
    
    # ДОБАВИТЬ: Проверка rate limit
    if is_rate_limited(email):
        log_line("auth", "WARN", "login", "AUTH_LOGIN", "DECISION", {
            "decision": "reject_rate_limited",
            "branch": "rate_limit_exceeded",
        })
        log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "EXIT", {
            "result": "rejected",
            "error": "RATE_LIMITED",
        })
        return {"error": "RATE_LIMITED"}
    
    # Существующий код...
    user = User.objects.filter(email=email).first()
    # ...
    
# [END_AUTH_LOGIN]
```

**Важно**: Проверь что не нарушены `@ForbiddenChanges`.

#### 4.2. Категория B (исправление контракта)

```python
# [START_AUTH_LOGIN]
"""
ANCHOR: AUTH_LOGIN
PURPOSE: Аутентификация пользователя по email и паролю.

@PreConditions:
- email: валидный email
- password: непустой
- НЕ превышен rate limit
- ПОЛЬЗОВАТЕЛЬ НЕ ЗАБЛОКИРОВАН ← ДОБАВЛЕНО

@PostConditions:
- при успехе: { access_token, refresh_token }
- при rate limit: { error: "RATE_LIMITED" }
- при blocked user: { error: "USER_BLOCKED" } ← ДОБАВЛЕНО
"""
```

**Обязательно**: Обнови Feature Spec + Validation Report.

### Шаг 5: Добавление regression test

```python
# tests/unit/test_auth_login.py

def test_auth_login_rate_limited_regression():
    """
    Regression test for BUG-001: Rate limiting должен возвращать RATE_LIMITED
    
    Issue: При превышении rate limit функция возвращала success
    Fix: Добавлена проверка rate limit в начале функции
    """
    # Given: Превышен rate limit для email
    email = "test@example.com"
    set_rate_limit(email, exceeded=True)
    
    # When
    result = login(email=email, password="password123")
    
    # Then
    assert result == {"error": "RATE_LIMITED"}
    
    # Verify log markers
    with capture_logs() as logs:
        result = login(email=email, password="password123")
    
    assert has_log_marker(logs, anchor="AUTH_LOGIN", point="DECISION")
    assert has_log_marker(logs, anchor="AUTH_LOGIN", point="EXIT")
```

### Шаг 6: Обновление тестов

Если категория B или C:

1. Обнови `plans/validation/V-FEAT-XXX.xml`:
   - Добавь новый тест-сценарий для нового кейса
   - Обнови существующие сценарии если нужно

2. Перезапусти `grace-validate-plan`

### Шаг 7: Формирование Fix Report

Создай `reports/fix-{TIMESTAMP}-BUG-XXX.md`:

```markdown
# Fix Report

**Bug ID**: BUG-001
**Feature**: FEAT-001
**Date**: 2026-04-14T16:22:00

---

## 🐛 Problem

При превышении rate limit функция `login` не блокировала запрос, а продолжала аутентификацию.

**Verification Report**: `reports/verification-20260414162200-FEAT-001.md`
**Failed Test**: `test_auth_login_rate_limited`

---

## 🔍 Root Cause Analysis

### Localisation

**ANCHOR**: AUTH_LOGIN
**File**: `backend/apps/users/services.py:42`
**Function**: `login(email, password)`

### Contract Analysis

```python
@PreConditions:
- НЕ превышен rate limit ← НЕ ПРОВЕРЯЕТСЯ В КОДЕ

@PostConditions:
- при rate limit: { error: "RATE_LIMITED" } ← НЕ ОБЕСПЕЧЕНО
```

**Диагноз**: Нарушено предусловие (rate limit не проверяется) → Постусловие не обеспечено (rate limited не возвращается).

---

## 🔧 Fix

**Category**: A (Fix Implementation)

Contract is correct, code doesn't match it.

### Code Changes

```diff
# backend/apps/users/services.py

def login(email: str, password: str) -> dict:
    log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "ENTRY", {...})
    
+   # Check rate limit FIRST
+   if is_rate_limited(email):
+       log_line("auth", "WARN", "login", "AUTH_LOGIN", "DECISION", {
+           "decision": "reject_rate_limited",
+       })
+       log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "EXIT", {
+           "result": "rejected",
+           "error": "RATE_LIMITED",
+       })
+       return {"error": "RATE_LIMITED"}
+   
    # Existing code...
    user = User.objects.filter(email=email).first()
```

### Forbidden Changes Check

✅ Rate limiting НЕ убран — добавлена проверка
✅ Безопасность сохранена
✅ Контракт не нарушен

---

## 🧪 Tests Added

### 1. Regression Test

**File**: `tests/unit/test_auth_login.py::test_auth_login_rate_limited_regression`

```python
def test_auth_login_rate_limited_regression():
    """Bug-001: Rate limiting должен работать"""
    set_rate_limit("test@example.com", exceeded=True)
    result = login(email="test@example.com", password="...")
    assert result == {"error": "RATE_LIMITED"}
```

### 2. Contract Invariant Test

**File**: `tests/unit/test_auth_login.py::test_auth_login_contract_invariant`

```python
def test_auth_login_contract_invariant():
    """Contract: @ForbiddenChanges - rate limiting never removed"""
    # Verify that rate limit check exists
    source = inspect.getsource(login)
    assert "rate_limit" in source.lower() or "is_rate_limited" in source
```

---

## 📋 Updated Markers

### Added

- `[auth][login][AUTH_LOGIN][DECISION]` — логирование решения о блокировке rate limit

### Modified

- `[auth][login][AUTH_LOGIN][EXIT]` — теперь включает `error: "RATE_LIMITED"` при блокировке

---

## ✅ Verification

- [x] All tests pass
- [x] Regression test added
- [x] Log markers updated
- [x] Contract preserved
- [x] No forbidden changes violated

**Test Run**: `pytest tests/unit/test_auth_login.py` → 15/15 passed

---

## 📎 Related Artifacts

- Feature Spec: `plans/features/FEAT-001.md`
- Validation Report: `plans/validation/V-FEAT-001.xml`
- Verification Report: `reports/verification-20260414162200-FEAT-001.md`
```

## Пример использования

```bash
# Исправление конкретного бага
/kilo skill grace-fix BUG-001

# Исправление из Verification Report
/kilo skill grace-fix --from-report reports/verification-20260414-FEAT-001.md

# Исправление по описанию
/kilo skill grace-fix "Rate limiting не работает в функции login"
```

## Результат

После выполнения:

- [ ] Проблема локализована через ANCHOR
- [ ] Контракт проанализирован
- [ ] Категория исправления определена
- [ ] Код исправлен без нарушения `@ForbiddenChanges`
- [ ] Regression tests добавлены
- [ ] Log-маркеры обновлены если нужно
- [ ] Fix Report создан

## Чеклист исправления

### Перед исправлением

- [ ] ANCHOR определён
- [ ] Контракт прочитан
- [ ] Нарушение идентифицировано (Pre/Post/Invariant)
- [ ] Категория определена (A/B/C)

### После исправления

- [ ] `@ForbiddenChanges` не нарушены
- [ ] Regression test добавлен
- [ ] Все существующие тесты проходят
- [ ] Log-маркеры корректны
- [ ] Fix Report создан

## Что делать после

1. Запусти `grace-verification FEAT-XXX` для повторной проверки
2. Если все тесты PASS — фича готова
3. Если есть другие issues — исправь их через `grace-fix`

## КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО

1. **Менять поведение под видом исправления бага**
   - Если поведение не в контракте → это новая фича → `grace-plan`

2. **Нарушать `@ForbiddenChanges`**
   - Если исправление требует нарушения → согласовать с бизнесом сначала

3. **Удалять проверки "для упрощения"**
   - За каждой проверкой может стоять бизнес-ограничение

4. **Менять контракт под реализацию**
   - Только наоборот: реализация под контракт
   - Исключение: Категория B с согласования
