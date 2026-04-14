---
name: grace-init
description: Инициализация проекта по методологии GRACE с семантической разметкой
---

# GRACE Init

Инициализирует проект для работы по методологии GRACE (Generic Rule-based Architecture for Contracted Execution).

## Что делает этот скилл

1. Создаёт структуру директорий
2. Генерирует `.kilocode/semantic-graph.xml`
3. Создаёт правила методологии
4. Инициализирует примеры разметки
5. Настраивает `.kilo/` структуру для скиллов и агентов
6. Создаёт базовый `AGENTS.md`

## Параметры

```bash
/kilo skill grace-init [--project-name NAME] [--stack STACK] [--minimal]
```

- `--project-name` — имя проекта (по умолчанию: текущая директория)
- `--stack` — стек технологий: `django`, `node`, `go`, `python`, `typescript` (по умолчанию: `django`)
- `--minimal` — минимальная инициализация (только правила, без структуры проекта)

## Процесс инициализации

### Шаг 1: Проверка существующей структуры

Проверь:
- [ ] Существует ли `.kilocode/`?
- [ ] Существует ли `.kilo/`?
- [ ] Есть ли `AGENTS.md`?

### Шаг 2: Создание директорий

Если `--minimal` не указан:

```
.kilocode/
├── rules/
│   ├── semantic-code-markup.md
│   ├── ai-logging.md
│   ├── semantic-graph-xml.md
│   └── semantic-markup-examples/
│       ├── example-python.py
│       ├── example-typescript.ts
│       ├── example-javascript.js
│       └── example-go.go
├── semantic-graph.xml
└── rules/README.md

.kilo/
├── agent/
├── skill/
├── templates/
└── artifacts/

plans/
└── features/

reports/
```

### Шаг 3: Генерация semantic-graph.xml

Используй шаблон:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<semantic-graph version="1.0" last-updated="{DATE}">
  <meta>
    <product>{PROJECT_NAME}</product>
    <description>{DESCRIPTION}</description>
    <tech-stack>
      <backend>{STACK}</backend>
    </tech-stack>
    <constraints>
      <constraint>Semantic code markup with ANCHOR</constraint>
      <constraint>AI-friendly logging</constraint>
    </constraints>
  </meta>
  
  <components>
    <!-- Components will be added by grace-plan -->
  </components>
  
  <relationships>
    <!-- Relationships will be added by grace-plan -->
  </relationships>
  
  <decisions>
    <decision id="ADR-001" status="accepted">
      <title>GRACE Methodology</title>
      <rationale>
        Semantic code markup with contracts and AI-friendly logging.
        See .kilocode/rules/ for details.
      </rationale>
    </decision>
  </decisions>
</semantic-graph>
```

### Шаг 4: Создание правил

Скопируй правила из существующего проекта или сгенерируй базовые:

- `.kilocode/rules/semantic-code-markup.md` — правила контрактной разметки
- `.kilocode/rules/ai-logging.md` — правила AI-friendly логирования
- `.kilocode/rules/semantic-graph-xml.md` — формат семантического графа
- `.kilocode/rules/README.md` — обзор правил

### Шаг 5: Примеры разметки

Создай каталог `.kilocode/rules/semantic-markup-examples/` с примерами для выбранного стека.

### Шаг 6: AGENTS.md

Создай или обнови `AGENTS.md`:

```markdown
# Project Instructions for AI Agents

## GRACE Methodology

This project follows GRACE (Generic Rule-based Architecture for Contracted Execution) methodology.

### Key Principles

1. **Semantic Code Markup**: Every critical function has ANCHOR and contract
2. **AI-Friendly Logging**: ENTRY/EXIT/BRANCH/DECISION/ERROR points
3. **Contract-First**: Code must match the contract, not vice versa

### Workflow

1. `grace-plan` — Plan feature → Feature Spec
2. `grace-validate-plan` — Validate → Validation Report
3. `grace-execute` — Implement → Code + Tests
4. `grace-verification` — Verify → Verification Report
5. `grace-fix` — Fix issues if needed

### Key Files

- `.kilocode/rules/` — Methodology rules
- `.kilocode/semantic-graph.xml` — Architecture graph
- `plans/features/` — Feature specifications
- `plans/validation/` — Validation reports

See `.kilocode/rules/README.md` for details.
```

## Пример использования

```bash
# Полная инициализация Django проекта
/kilo skill grace-init --project-name lms-system --stack django

# Минимальная инициализация (только правила)
/kilo skill grace-init --minimal

# Инициализация Node.js проекта
/kilo skill grace-init --stack node
```

## Результат

После выполнения:

- [ ] `.kilocode/` создан с правилами
- [ ] `.kilocode/semantic-graph.xml` создан
- [ ] `.kilo/` структура создана
- [ ] `AGENTS.md` создан/обновлён
- [ ] Примеры разметки для стека созданы
- [ ] `plans/features/` директория создана

## Что делать после

1. Отредактируй `.kilocode/semantic-graph.xml` под свой проект
2. Добавь специфичные правила в `.kilocode/rules/`
3. Запусти `grace-plan` для первой фичи
