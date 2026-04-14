# GRACE: Generic Rule-based Architecture for Contracted Execution

Методология и набор инструментов для AI-assisted разработки с семантической разметкой кода.

---

## 🎯 Что такое GRACE?

GRACE — это методология разработки, которая делает код понятным для AI-агентов через:

1. **Семантическую разметку** — каждый важный блок кода имеет ANCHOR и контракт
2. **AI-friendly логирование** — ENTRY/EXIT/BRANCH/DECISION/ERROR точки
3. **Контракты** — формальное описание предусловий, постусловий, инвариантов
4. **Многоуровневое тестирование** — детерминированные, траекторные, интеграционные тесты

---

## 🚀 Быстрый старт

### 1. Инициализация проекта

```bash
/kilo skill grace-init --project-name my-project --stack django
```

### 2. Планирование фичи

```bash
/kilo skill grace-plan "Логин пользователя по email и паролю"
```

Это создаст `plans/features/FEAT-001.md` с полным ТЗ фичи.

### 3. Валидация плана

```bash
/kilo skill grace-validate-plan FEAT-001
```

Создаст `plans/validation/V-FEAT-001.xml` с тест-сценариями 3 уровней.

### 4. Генерация кода

```bash
/kilo skill grace-execute FEAT-001
```

Сгенерирует код с ANCHOR, контрактами и логированием.

### 5. Верификация

```bash
/kilo skill grace-verification FEAT-001
```

Запустит тесты, проверит log-маркеры, создаст отчёт.

### 6. Исправление багов (если нужно)

```bash
/kilo skill grace-fix BUG-001
```

---

## 📁 Структура проекта

```
.kilo/
├── agent/              # AI агенты GRACE
│   ├── implementer.md
│   ├── contract-reviewer.md
│   ├── verification-reviewer.md
│   └── fixer.md
├── skill/              # Скиллы GRACE
│   ├── grace-init/
│   ├── grace-plan/
│   ├── grace-validate-plan/
│   ├── grace-execute/
│   ├── grace-verification/
│   └── grace-fix/
├── templates/          # Шаблоны артефактов
│   ├── feature-spec-template.md
│   ├── validation-report-template.xml
│   └── test-plan-template.md
└── artifacts/          # Документация
    └── README.md

.kilocode/
├── rules/              # Правила методологии
│   ├── semantic-code-markup.md
│   ├── ai-logging.md
│   ├── semantic-graph-xml.md
│   └── semantic-markup-examples/
└── semantic-graph.xml  # Архитектурный граф

plans/
├── features/           # Feature Specifications
│   └── FEAT-001.md
└── validation/         # Validation Reports
    └── V-FEAT-001.xml

reports/
├── verification-*.md   # Verification Reports
└── fix-*.md           # Fix Reports
```

---

## 🤖 Агенты

| Агент | Режим | Назначение |
|-------|-------|------------|
| **implementer** | primary | Генерация кода по Feature Spec |
| **contract-reviewer** | subagent | Проверка соответствия контрактов |
| **verification-reviewer** | subagent | Прогон тестов и проверка маркеров |
| **fixer** | primary | Исправление багов с сохранением контрактов |

---

## 🔧 Скиллы

| Скилл | Назначение | Результат |
|-------|------------|-----------|
| **grace-init** | Инициализация проекта | Структура директорий, правила |
| **grace-plan** | Планирование фичи | Feature Spec (FEAT-XXX.md) |
| **grace-validate-plan** | Валидация плана | Validation Report (V-FEAT-XXX.xml) |
| **grace-execute** | Генерация кода | Код + тесты |
| **grace-verification** | Верификация | Verification Report |
| **grace-fix** | Исправление багов | Fix Report + исправленный код |

---

## 📝 Пример кода с разметкой

```python
# [START_AUTH_LOGIN]
"""
ANCHOR: AUTH_LOGIN
PURPOSE: Аутентификация пользователя по email и паролю.

@PreConditions:
- email: валидный email формат
- password: непустая строка

@PostConditions:
- при успехе: { access_token, refresh_token, user }
- при ошибке: { error: "INVALID_CREDENTIALS" }

@Invariants:
- пароль никогда не возвращается в ответе

@SideEffects:
- создаёт refresh_token в БД
- логирует попытку входа

@ForbiddenChanges:
- нельзя убрать rate limiting
"""
def login(email: str, password: str) -> dict:
    log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "ENTRY", {
        "email": email,
    })
    
    # Rate limit check
    if is_rate_limited(email):
        log_line("auth", "WARN", "login", "AUTH_LOGIN", "DECISION", {
            "decision": "rate_limited",
        })
        log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "EXIT", {
            "result": "rejected",
        })
        return {"error": "RATE_LIMITED"}
    
    # Validate credentials
    user = validate_credentials(email, password)
    log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "CHECK", {
        "check": "credentials_valid",
        "result": user is not None,
    })
    
    if not user:
        log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "EXIT", {
            "result": "rejected",
        })
        return {"error": "INVALID_CREDENTIALS"}
    
    # Generate tokens
    tokens = generate_tokens(user)
    
    log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "EXIT", {
        "result": "success",
    })
    
    return {
        "access_token": tokens["access"],
        "refresh_token": tokens["refresh"],
        "user": {"id": user.id, "email": user.email},
    }
# [END_AUTH_LOGIN]
```

---

## 🧪 3 уровня тестирования

### Level 1: Детерминированные тесты

Проверка постусловий:

```python
def test_login_success():
    result = login("user@example.com", "password")
    assert result["access_token"] is not None
    assert result["refresh_token"] is not None
```

### Level 2: Тесты траектории

Проверка log-маркеров:

```python
def test_auth_login_markers():
    with capture_logs() as logs:
        login("user@example.com", "password")
    
    assert has_log_marker(logs, anchor="AUTH_LOGIN", point="ENTRY")
    assert has_log_marker(logs, anchor="AUTH_LOGIN", point="EXIT")
```

### Level 3: Интеграционные тесты

E2E сценарии:

```python
def test_e2e_login():
    response = client.post("/api/auth/login/", {...})
    assert response.status_code == 200
    
    # Use token to access protected endpoint
    response = client.get("/api/users/me/", 
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

---

## 📊 Workflow

```
┌─────────────────┐
│  grace-init     │  Инициализация
└────────┬────────┘
         │
         v
┌─────────────────┐
│  grace-plan     │  → Feature Spec
└────────┬────────┘
         │
         v
┌─────────────────────────┐
│  grace-validate-plan    │  → Validation Report
└────────┬────────────────┘
         │
         v
┌─────────────────┐
│  grace-execute  │  → Код + тесты
└────────┬────────┘
         │
         v
┌──────────────────────┐
│  grace-verification  │  → Verification Report
└────────┬─────────────┘
         │
    ┌────┴────┐
   PASS       FAIL
    │          │
    v          v
  DONE    ┌─────────┐
          │ grace-fix │
          └─────┬─────┘
                │
                v
          (повторная верификация)
```

---

## 📖 Документация

- [Artifacts Documentation](.kilo/artifacts/README.md) — описание всех артефактов
- [Semantic Markup Rules](.kilocode/rules/semantic-code-markup.md) — правила разметки
- [AI Logging Rules](.kilocode/rules/ai-logging.md) — правила логирования
- [Semantic Graph](.kilocode/semantic-graph.xml) — архитектура компонентов
- [Plan File](.kilo/plans/1776172123309-curious-planet.md) — план реализации системы GRACE

---

## ✅ Ключевые принципы

1. **Контракт-первый** — код должен соответствовать контракту, не наоборот
2. **Явная семантика** — каждый блок имеет адрес (ANCHOR) и смысл (контракт)
3. **Наблюдаемость** — логи позволяют восстановить траекторию выполнения
4. **Запрет разрушения** — `@ForbiddenChanges` защищает критичную логику
5. **Без догадок** — при неопределённости — сохранить поведение, пометить `@SEMANTIC_AMBIGUITY`

---

## 🎓 Демо-пример

См. `plans/features/FEAT-001.md` — пример Feature Spec для аутентификации пользователей.

---

*Создано: 2026-04-14*
