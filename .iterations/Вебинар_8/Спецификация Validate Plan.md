Спецификация GRACE Validate Plan
0,22 $
44%

90.8K
205.0K
Tokens
1.4K
408
cache 89.0K

8 задач выполнено
# GRACE Validate Plan

Валидирует Feature Specification на полноту, непротиворечивость и формирует Validation Report с тест-сценариями 3 уровней.

## Что делает этот скилл

1. Проверяет наличие всех обязательных секций в Feature Spec
2. Валидирует контракты на полноту
3. Проверяет связи в `.kilocode/semantic-graph.xml`
4. Формирует тест-сценарии 3 уровней:
   - Детерминированные (проверки результатов)
   - Траекторные (проверки log-маркеров)
   - Интеграционные (E2E сценарии)
5. Создаёт Validation Report

## Параметры

```bash
/kilo skill grace-validate-plan FEAT-XXX
```

- `все фичи провалидируй` — ID фичи (например, FEAT-001)
- Или `все фичи провалидируй` — путь к Feature Spec файлу

## Процесс валидации

### Шаг 1: Загрузка Feature Spec

Прочитай:
- `plans/features/FEAT-XXX.md`
- `.kilocode/semantic-graph.xml`

### Шаг 2: Проверка полноты секций

| Секция | Проверки | Критично |
|--------|----------|----------|
| Описание | Есть, понятно, 1-3 предложения | ✅ |
| Цель | Есть, измерима | ✅ |
| Компоненты | Пути указаны, типы определены | ✅ |
| Контракты | Все ANCHOR определены | ✅ |
| User Stories | Есть критерии приёма | ✅ |
| Тест-план | Есть черновик | ⚠️ |

### Шаг 3: Валидация контрактов

Для каждого ANCHOR проверь:

| Поле | Требование | Проверка |
|------|------------|----------|
| ANCHOR | Уникальный ID в UPPER_SNAKE_CASE | ✅ |
| PURPOSE | Одна фраза, отвечает на "зачем" | ✅ |
| @PreConditions | Список условий или "нет" | ✅ |
| @PostConditions | Гарантии успеха и ошибки | ✅ |
| @Invariants | Хотя бы один инвариант | ✅ |
| @SideEffects | "нет" или список эффектов | ✅ |
| @ForbiddenChanges | Хотя бы одно ограничение | ✅ |

**Распространённые проблемы**:

❌ "Меняет данные в БД" — слишком общее
✅ "Создаёт запись в таблице users с полями email, password_hash"

❌ "Работает правильно" — не измеримо
✅ "Возвращает 200 OK при валидных данных"

### Шаг 4: Проверка консистентности

Проверь:

1. **Нет дублирующихся ANCHOR_ID**:
   - Все ANCHOR в фиче уникальны
   - ANCHOR не конфликтует с другими фичами

2. **Ссылки в semantic-graph**:
   - Все компоненты из Feature Spec есть в semantic-graph.xml
   - Все зависимости (`depends-on`) существуют
   - Все рёбра (`edge`) указывают на существующие компоненты

3. **Нет противоречий**:
   - Предусловия не противоречат друг другу
   - Постусловия достижимы
   - Инварианты не нарушаются пред/постусловиями

### Шаг 5: Генерация тест-сценариев

#### Level 1: Детерминированные тесты

Для каждой функции из контракта:

```xml
<scenario id="SC-001" level="deterministic">
  <name>{название}</name>
  <description>{описание}</description>
  <anchor ref="{ANCHOR_ID}"/>
  <given>{предусловия из @PreConditions}</given>
  <when>{вызов функции}</when>
  <then>
    <assertion type="equal">
      <actual>result.status</actual>
      <expected>200</expected>
    </assertion>
  </then>
</scenario>
```

Генерируй:
- Успешный кейс (happy path)
- Кейсы для каждого условия ошибки из @PostConditions
- Edge cases для граничных значений

#### Level 2: Тесты траектории (log markers)

Для каждого ANCHOR:

```xml
<scenario id="SC-010" level="trajectory">
  <name>Проверка лог-маркеров для {ANCHOR_ID}</name>
  <anchor ref="{ANCHOR_ID}"/>
  <required-log-markers>
    <marker point="ENTRY" required="true">
      <pattern>[{MODULE}][{FUNCTION}][{ANCHOR_ID}][ENTRY]</pattern>
    </marker>
    <marker point="EXIT" required="true">
      <pattern>[{MODULE}][{FUNCTION}][{ANCHOR_ID}][EXIT]</pattern>
    </marker>
    <marker point="CHECK" required="false"/>
    <marker point="DECISION" required="false"/>
    <marker point="ERROR" required="false"/>
  </required-log-markers>
</scenario>
```

**Обязательные маркеры**: ENTRY, EXIT
**Опциональные**: CHECK, DECISION, ERROR, STATE_CHANGE

#### Level 3: Интеграционные тесты

Для каждой User Story:

```xml
<scenario id="SC-020" level="integration">
  <name>{User Story name}</name>
  <description>E2E сценарий</description>
  <steps>
    <step order="1">
      <action>{действие пользователя}</action>
      <expected>{ожидаемый результат}</expected>
      <verify-markers>
        <marker ref="SC-010"/> <!-- ссылка на trajectory тест -->
      </verify-markers>
    </step>
    <step order="2">
      <!-- ... -->
    </step>
  </steps>
</scenario>
```

### Шаг 6: Формирование Validation Report

Создай `plans/validation/V-FEAT-XXX.xml` по шаблону `.kilo/templates/validation-report-template.xml`.

Обязательно включи:

- [ ] Статус: `pass`, `fail` или `incomplete`
- [ ] Проверки полноты всех секций
- [ ] Проверки всех контрактов
- [ ] Все тест-сценарии 3 уровней
- [ ] Рекомендации по улучшению

### Шаг 7: Обновление статуса

Обнови `plans/features/FEAT-XXX.md`:
- Если `pass`: статус → `validated`
- Если `fail/incomplete`: статус → `planning` (требуется доработка)

## Пример использования

```bash
/kilo skill grace-validate-plan FEAT-001

/kilo skill grace-validate-plan plans/features/FEAT-002.md
```

## Результат

После выполнения:

- [ ] Файл `plans/validation/V-FEAT-XXX.xml` создан
- [ ] Все секции проверены на полноту
- [ ] Все контракты провалидированы
- [ ] Тест-сценарии 3 уровней сгенерированы
- [ ] Статус в Feature Spec обновлён

## Критерии успеха

Validation Report считается `pass`, если:

- ✅ Все обязательные секции заполнены
- ✅ Все контракты имеют обязательные поля
- ✅ Нет противоречий в пред/постусловиях
- ✅ Все ссылки в semantic-graph валидны
- ✅ Тест-сценарии покрывают все ANCHOR

## Что делать после

1. Если `pass`: запусти `grace-execute FEAT-XXX`
2. Если `fail/incomplete`:
   - Исправь проблемы в Feature Spec
   - Перезапусти `grace-validate-plan`

## Пример отчёта

```xml
<?xml version="1.0" encoding="UTF-8"?>
<validation-report feature-id="FEAT-001" date="2026-04-14">
  <status>pass</status>
  
  <completeness>
    <section name="description" status="pass"/>
    <section name="contracts" status="pass"/>
    <section name="acceptance" status="pass"/>
  </completeness>
  
  <contracts>
    <contract anchor="AUTH_LOGIN">
      <has-purpose>true</has-purpose>
      <has-preconditions>true</has-preconditions>
      <!-- ... -->
    </contract>
  </contracts>
  
  <test-scenarios>
    <!-- 3 детерминированных сценария -->
    <!-- 1 траекторный сценарий -->
    <!-- 1 интеграционный сценарий -->
  </test-scenarios>
</validation-report>
```








$ mkdir -p plans/validation








































Все 7 Feature Specification провалидированы успешно.

Результаты валидации
Feature	Статус	Контрактов	Тест-сценариев
FEAT-001: Аутентификация	✅ pass	5	15 deterministic, 5 trajectory, 4 integration
FEAT-002: Восстановление пароля	✅ pass	3	6 deterministic, 3 trajectory, 2 integration
FEAT-003: Управление курсами	✅ pass	9	9 deterministic, 4 trajectory, 1 integration
FEAT-004: Тесты и попытки	✅ pass	4	7 deterministic, 3 trajectory, 1 integration
FEAT-005: Отслеживание прогресса	✅ pass	3	6 deterministic, 3 trajectory, 1 integration
FEAT-006: Бронирование ресурсов	✅ pass	2	6 deterministic, 2 trajectory, 1 integration
FEAT-007: Уведомления	✅ pass	2	5 deterministic, 2 trajectory, 1 integration
Созданные файлы
plans/validation/V-FEAT-001.xml
plans/validation/V-FEAT-002.xml
plans/validation/V-FEAT-003.xml
plans/validation/V-FEAT-004.xml
plans/validation/V-FEAT-005.xml
plans/validation/V-FEAT-006.xml
plans/validation/V-FEAT-007.xml
Все спецификации обновлены: статус → validated. Следующий шаг: grace-execute FEAT-001 для начала реализации.


+10581
-10
Введите сообщение... (Enter для отправки, Shift+Enter для новой строки)
