# Feature: {FEATURE_NAME}

> **ID**: {FEATURE_ID}
> **Status**: {draft|planning|validated|implemented|verified|failed}
> **Created**: {DATE}
> **Updated**: {DATE}

---

## 📋 Описание

{Краткое описание фичи в 1-3 предложениях}

---

## 🎯 Цель

{Зачем нужна эта фича. Какую проблему решает.}

---

## 📦 Компоненты

### Новые компоненты

| Компонент | Тип | Путь | Описание |
|-----------|-----|------|----------|
| {NAME} | {model/view/service/etc} | {path} | {description} |

### Изменяемые компоненты

| Компонент | Изменение |
|-----------|-----------|
| {NAME} | {что меняется} |

---

## 🔗 Связи

### Зависимости

- Зависит от: {список компонентов}
- Зависимые: {кто зависит от этого компонента}

### Semantic Graph Updates

```xml
<component id="{COMPONENT_ID}" kind="{kind}" path="{path}">
  <role>{описание роли}</role>
  <depends-on ref="{DEPENDENCY_ID}"/>
  <exposes>
    <api name="{API_NAME}" type="{type}">{description}</api>
  </exposes>
</component>

<edge id="{EDGE_ID}" from="{FROM}" to="{TO}" kind="{kind}">
  <description>{описание связи}</description>
</edge>
```

---

## 📝 Контракты

### {ANCHOR_ID_1}

**Функция**: `{function_name}`
**Файл**: `{path}`

```
ANCHOR: {ANCHOR_ID_1}
PURPOSE: {зачем функция существует}

@PreConditions:
- {условие 1}
- {условие 2}

@PostConditions:
- {гарантия при успехе}
- {гарантия при ошибке}

@Invariants:
- {инвариант 1}

@SideEffects:
- {побочный эффект или "нет"}

@ForbiddenChanges:
- {что нельзя менять}
```

### {ANCHOR_ID_2}

{...аналогично для каждого ANCHOR}

---

## ✅ Критерии приёма

### User Story 1

**Как** {роль}
**Я хочу** {действие}
**Чтобы** {цель}

**Acceptance Criteria**:
- [ ] {критерий 1}
- [ ] {критерий 2}

### User Story 2

{...аналогично}

---

## 🧪 Тест-план

**Validation Report**: `plans/validation/V-{FEATURE_ID}.xml`

### Детерминированные тесты
- [ ] {название теста} — {описание проверки}

### Тесты траектории (log markers)
- [ ] {название теста} — проверка маркеров {ANCHOR_ID}

### Интеграционные тесты
- [ ] {название E2E сценария}

---

## 📊 Статус реализации

| Этап | Статус | Дата | Комментарий |
|------|--------|------|-------------|
| Planning | ✅ | {date} | |
| Validation | ⏳ | | |
| Implementation | ⏳ | | |
| Verification | ⏳ | | |

---

## 📎 Связанные артефакты

- Validation Report: `plans/validation/V-{FEATURE_ID}.xml`
- Verification Report: `reports/verification-{TIMESTAMP}.md`
- Code: `{paths to generated code}`
- Tests: `{paths to tests}`
