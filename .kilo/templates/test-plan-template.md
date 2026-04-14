# Test Plan: {FEATURE_ID}

> **Feature**: {FEATURE_NAME}
> **Created**: {DATE}
> **Status**: {draft|ready|executed}

---

## 📋 Overview

{Краткое описание того, что тестируется}

---

## 🎯 Test Strategy

### Levels of Testing

| Level | Type | Coverage Target |
|-------|------|-----------------|
| 1 | Deterministic (Unit) | 100% of functions |
| 2 | Trajectory (Log Markers) | All ANCHORs |
| 3 | Integration (E2E) | Critical paths |

---

## Level 1: Deterministic Tests

### SC-001: {Test Name}

**Anchor**: `{ANCHOR_ID}`
**Function**: `{function_name}`
**File**: `{path}`

**Given**:
- {предусловие 1}
- {предусловие 2}

**When**:
- {действие}

**Then**:
```python
assert result.status == 200
assert result.data["id"] is not None
```

---

### SC-002: {Test Name}

{...аналогично}

---

## Level 2: Trajectory Tests (Log Markers)

### SC-010: Verify Log Markers for {ANCHOR_ID}

**Function**: `{function_name}`
**Module**: `{module_name}`

**Required Markers**:

| Point | Pattern | Required Fields |
|-------|---------|-----------------|
| ENTRY | `[{MODULE}][{FUNCTION}][{ANCHOR_ID}][ENTRY]` | module, function, anchor |
| EXIT | `[{MODULE}][{FUNCTION}][{ANCHOR_ID}][EXIT]` | result |
| CHECK | `[{MODULE}][{FUNCTION}][{ANCHOR_ID}][CHECK]` | check, result |
| DECISION | `[{MODULE}][{FUNCTION}][{ANCHOR_ID}][DECISION]` | decision, branch |
| ERROR | `[{MODULE}][{FUNCTION}][{ANCHOR_ID}][ERROR]` | reason |

**Test Code**:
```python
def test_anchor_log_markers():
    # Execute function
    result = function_under_test()
    
    # Verify markers in logs
    logs = get_captured_logs()
    
    assert has_log_marker(logs, "ENTRY", ANCHOR_ID)
    assert has_log_marker(logs, "EXIT", ANCHOR_ID)
    assert has_log_marker(logs, "CHECK", ANCHOR_ID, optional=True)
```

---

## Level 3: Integration Tests (E2E)

### SC-020: {Scenario Name}

**Description**: {описание E2E сценария}

**Steps**:

| Order | Action | Expected Result | Verify Markers |
|-------|--------|-----------------|----------------|
| 1 | {action} | {expected} | {marker refs} |
| 2 | {action} | {expected} | {marker refs} |
| 3 | {action} | {expected} | {marker refs} |

**Test Code**:
```python
def test_e2e_scenario():
    # Step 1: {description}
    response = client.post("/api/action", data)
    assert response.status_code == 200
    
    # Step 2: {description}
    # ...
    
    # Verify log markers from all involved ANCHORs
    logs = get_captured_logs()
    assert has_all_required_markers(logs, ["ANCHOR_1", "ANCHOR_2"])
```

---

## Test Data

### Fixtures

```yaml
fixture_1:
  - name: "test_user"
  - email: "test@example.com"
  - role: "learner"

fixture_2:
  - name: "admin_user"
  - email: "admin@example.com"
  - role: "admin"
```

### Mocks

| What | Why |
|------|-----|
| external_api | Изоляция от внешних сервисов |
| email_service | Предотвращение реальной отправки |

---

## Coverage Requirements

| Metric | Target | Actual |
|--------|--------|--------|
| Statements | 70% | - |
| Branches | 60% | - |
| Functions | 80% | - |

---

## Test Execution

### Commands

```bash
# Run all tests for this feature
pytest tests/unit/test_{feature}.py -v
pytest tests/integration/test_{feature}_flow.py -v
pytest tests/e2e/test_{feature}_e2e.py -v

# Run with coverage
pytest --cov=backend/apps/{module} --cov-report=term-missing

# Run specific test
pytest tests/unit/test_{feature}.py::test_sc_001 -v
```

### CI Integration

```yaml
test:
  script:
    - pytest tests/ --cov=backend --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## Defects Found

| ID | Description | Severity | Status |
|----|-------------|----------|--------|
| BUG-001 | {описание} | {critical|major|minor} | {open|fixed} |

---

## Sign-off

- [ ] All deterministic tests pass
- [ ] All trajectory tests pass (log markers verified)
- [ ] All integration tests pass
- [ ] Coverage meets requirements
- [ ] No critical defects open

**Approved by**: {имя}
**Date**: {дата}
