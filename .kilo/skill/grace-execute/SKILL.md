---
name: grace-execute
description: Генерация кода по Feature Specification с семантической разметкой и тестами
agent: implementer
---

# GRACE Execute

Генерирует код по Feature Specification с семантической разметкой, контрактами и тестами.

## Что делает этот скилл

1. Читает Feature Spec и Validation Report
2. Генерирует код с семантической разметкой:
   - ANCHOR и CHUNK комментарии
   - Полные контракты для всех функций
   - AI-friendly логирование (ENTRY, EXIT, BRANCH, DECISION, ERROR)
3. Создаёт тесты по тест-сценариям
4. Обновляет статус фичи
5. Обновляет `.kilocode/semantic-graph.xml`

## Параметры

```bash
/kilo skill grace-execute FEAT-XXX
```

- `$1` — ID фичи (например, FEAT-001)
- Или `$ARGUMENTS` — путь к Feature Spec файлу

## Процесс генерации кода

### Шаг 1: Загрузка данных

Прочитай:
- `plans/features/FEAT-XXX.md` — Feature Specification
- `plans/validation/V-FEAT-XXX.xml` — Validation Report с тест-сценариями
- `.kilocode/semantic-graph.xml` — Архитектура компонентов
- `.kilocode/rules/semantic-markup-examples/` — Примеры для стека

### Шаг 2: Подготовка к генерации

Для каждого компонента из Feature Spec:

1. Определи путь к файлу
2. Проверь, существует ли файл
3. Если существует — определи, что нужно добавить/изменить
4. Если нет — создай с базовой структурой

### Шаг 3: Генерация кода

**ОБЯЗАТЕЛЬНЫЕ требования к каждой функции:**

#### 3.1. ANCHOR комментарии

```python
# [START_ANCHOR_ID]
# ... код функции ...
# [END_ANCHOR_ID]
```

#### 3.2. Контракт

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
- создаёт/обновляет refresh_token в БД

@ForbiddenChanges:
- нельзя убрать rate limiting
"""
```

#### 3.3. AI-friendly логирование

```python
def login(email: str, password: str) -> dict:
    log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "ENTRY", {
        "email": email,
        "has_password": bool(password),
    })
    
    # Валидация
    if not email or "@" not in email:
        log_line("auth", "WARN", "login", "AUTH_LOGIN", "ERROR", {
            "reason": "invalid_email_format",
        })
        log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "EXIT", {
            "result": "rejected",
            "error": "INVALID_EMAIL",
        })
        return {"error": "INVALID_EMAIL"}
    
    # Проверка пользователя
    user = User.objects.filter(email=email).first()
    log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "CHECK", {
        "check": "user_exists",
        "result": user is not None,
    })
    
    if not user:
        log_line("auth", "WARN", "login", "AUTH_LOGIN", "DECISION", {
            "decision": "reject_invalid_credentials",
            "branch": "user_not_found",
        })
        log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "EXIT", {
            "result": "rejected",
        })
        return {"error": "INVALID_CREDENTIALS"}
    
    # ... остальная логика
    
    log_line("auth", "DEBUG", "login", "AUTH_LOGIN", "EXIT", {
        "result": "success",
        "user_id": user.id,
    })
    return {"access_token": "...", "user": {...}}
# [END_AUTH_LOGIN]
```

**Точки логирования**:

| Point | Когда использовать | Обязательно |
|-------|-------------------|-------------|
| ENTRY | Вход в функцию | ✅ |
| EXIT | Успешный выход | ✅ |
| BRANCH | Ветвление | ⚠️ при наличии |
| DECISION | Принятие решения | ⚠️ при наличии |
| CHECK | Результат проверки | ⚠️ при наличии |
| ERROR | Ошибка/отказ | ⚠️ при ошибке |
| STATE_CHANGE | Изменение состояния | ⚠️ при изменении |

### Шаг 4: Генерация тестов

Для каждого тест-сценария из Validation Report:

#### 4.1. Детерминированные тесты

```python
# tests/unit/test_auth_login.py

def test_auth_login_success():
    """SC-001: Успешный логин возвращает токены"""
    # Given
    user = create_test_user(email="test@example.com", password="password123")
    
    # When
    result = login(email="test@example.com", password="password123")
    
    # Then
    assert result["access_token"] is not None
    assert result["refresh_token"] is not None
    assert result["user"]["email"] == "test@example.com"

def test_auth_login_invalid_credentials():
    """SC-002: Невалидные credentials возвращают ошибку"""
    # Given
    # нет пользователя
    
    # When
    result = login(email="wrong@example.com", password="wrong")
    
    # Then
    assert result["error"] == "INVALID_CREDENTIALS"
```

#### 4.2. Тесты траектории (log markers)

```python
# tests/unit/test_auth_login_markers.py

def test_auth_login_log_markers():
    """SC-010: Проверка лог-маркеров для AUTH_LOGIN"""
    # Given
    user = create_test_user(email="test@example.com", password="password123")
    
    # When
    with capture_logs() as logs:
        result = login(email="test@example.com", password="password123")
    
    # Then
    assert has_log_marker(logs, module="auth", function="login", 
                          anchor="AUTH_LOGIN", point="ENTRY")
    assert has_log_marker(logs, module="auth", function="login",
                          anchor="AUTH_LOGIN", point="EXIT")
    assert has_log_marker(logs, module="auth", function="login",
                          anchor="AUTH_LOGIN", point="CHECK", optional=True)
```

#### 4.3. Интеграционные тесты

```python
# tests/integration/test_auth_login_flow.py

def test_auth_login_e2e():
    """SC-020: E2E сценарий аутентификации"""
    # Step 1: Пользователь открывает страницу логина
    response = client.get("/login")
    assert response.status_code == 200
    
    # Step 2: Вводит credentials
    with capture_logs() as logs:
        response = client.post("/api/auth/login/", {
            "email": "test@example.com",
            "password": "password123"
        })
    
    # Step 3: Получает токены
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Step 4: Может обратиться к protected endpoint
    response = client.get("/api/users/me/", 
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Verify log markers
    assert has_all_required_markers(logs, ["AUTH_LOGIN", "AUTH_GENERATE_TOKENS"])
```

### Шаг 5: Обновление статуса

Обнови `plans/features/FEAT-XXX.md`:

```markdown
## 📊 Статус реализации

| Этап | Статус | Дата | Комментарий |
|------|--------|------|-------------|
| Planning | ✅ | 2026-04-14 | |
| Validation | ✅ | 2026-04-14 | |
| Implementation | ✅ | 2026-04-14 | All code generated |
| Verification | ⏳ | | Pending test run |
```

Установи статус: `implemented`

### Шаг 6: Обновление semantic-graph.xml

Если добавлены новые компоненты:

```xml
<component id="backend.apps.users.views.AuthViewSet" kind="viewset" 
           path="backend/apps/users/views.py">
  <role>Аутентификация: login, logout, refresh</role>
  <depends-on ref="backend.apps.users.services.AuthService"/>
  <exposes>
    <api name="login" type="method">POST /api/auth/login/</api>
  </exposes>
</component>
```

## Пример использования

```bash
/kilo skill grace-execute FEAT-001

/kilo skill grace-execute plans/features/FEAT-002.md
```

## Результат

После выполнения:

- [ ] Код сгенерирован в соответствующих директориях
- [ ] Все функции размечены ANCHOR
- [ ] Все функции имеют полные контракты
- [ ] Все функции имеют AI-friendly логирование
- [ ] Unit-тесты созданы для deterministic сценариев
- [ ] Marker-тесты созданы для trajectory сценариев
- [ ] Integration-тесты созданы для E2E сценариев
- [ ] Статус в Feature Spec: `implemented`
- [ ] `.kilocode/semantic-graph.xml` обновлён

## Чеклист качества кода

### Семантическая разметка

- [ ] `[START_ANCHOR]` ... `[END_ANCHOR]` для каждой функции
- [ ] ANCHOR_ID совпадает в маркерах, контракте и логах
- [ ] Нет функций без ANCHOR (кроме тривиальных getters/setters)

### Контракты

- [ ] PURPOSE отвечает на "зачем"
- [ ] @PreConditions конкретны и проверяемы
- [ ] @PostConditions описывают все случаи (успех/ошибка)
- [ ] @Invariants не нарушаются кодом
- [ ] @SideEffects перечислены явно
- [ ] @ForbiddenChanges отражают бизнес-ограничения

### Логирование

- [ ] ENTRY лог для каждой функции
- [ ] EXIT лог для каждой функции
- [ ] ERROR лог с причиной для ошибок
- [ ] DECISION лог для ветвлений
- [ ] CHECK лог для проверок
- [ ] Данные в логах достаточны для диагностики

### Тесты

- [ ] Все deterministic сценарии покрыты
- [ ] Все trajectory сценарии покрыты
- [ ] E2E сценарии реализованы
- [ ] Тесты используют fixtures/mocks корректно

## Что делать после

1. Запусти `grace-verification FEAT-XXX` для прогона тестов
2. При падении тестов — используй `grace-fix` для исправления

## Типичные проблемы и решения

| Проблема | Решение |
|----------|---------|
| ANCHOR дублируется | Проверь уникальность в Feature Spec |
| Логи не совпадают с ANCHOR | Убедись что anchor параметр в log_line правильный |
| Контракт неполон | Дополни используя информацию из Validation Report |
| Тест падает | Проверь что тест соответствует контракту |
