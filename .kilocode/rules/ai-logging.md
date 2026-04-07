# AI-friendly логирование

## Назначение

Логи в этом проекте предназначены не только для человека, но и для автоматического анализа ИИ-агентом. Логи должны помогать ИИ локализовать ошибку, понимать траекторию исполнения и восстанавливать смысл произошедшего без чтения всего кода.

---

## Ключевой принцип

**Логи — это интерфейс самокоррекции. Код проектируется под цикл: ожидание по контракту → выполнение → лог → сравнение ожидания и результата → исправление.**

---

## 1. Требования к логам для ИИ

### 1.1 Обязательные свойства логов

| Требование | Зачем |
|------------|-------|
| Маркировка типа записи (INFO/DEBUG/ERROR) | Быстрая фильтрация |
| Ссылка на ANCHOR | Связь с контрактом и кодом |
| Вход в критичные функции | Трассировка пути исполнения |
| Выход из критичных функций | Подтверждение завершения |
| Логирование условий и ветвлений | Понимание решений |
| Логирование причин отказа | Диагностика ошибок |
| Ключевые входные данные | Воспроизведение контекста |
| Ключевые результаты | Верификация постусловий |
| Идентификаторы сущностей | Трассировка сквозного потока |

### 1.2 Запрещённые практики

- **Пустые логи** — без диагностической информации
- **Декоративные логи** — "Processing...", "Done!" без контекста
- **Логи без anchor** — разрушают связь с контрактом
- **Логи с разными anchor в одном блоке** — нарушают трассировку

---

## 2. Формат логирования

### 2.1 Сигнатура функции логирования

```typescript
logLine(
  module: string,      // Модуль/подсистема
  level: "DEBUG" | "INFO" | "WARN" | "ERROR",
  functionName: string,
  anchor: string,      // ANCHOR_ID из контракта
  point: string,       // Точка в функции: ENTRY, EXIT, BRANCH, DECISION, ERROR
  data: object         // Контекстные данные
): void
```

### 2.2 Точки логирования

| Point | Когда использовать |
|-------|-------------------|
| `ENTRY` | Вход в функцию |
| `EXIT` | Успешный выход из функции |
| `BRANCH` | Ветвление в логике |
| `DECISION` | Принятие решения |
| `CHECK` | Результат проверки |
| `ERROR` | Ошибка/отказ |
| `RETRY` | Повторная попытка |
| `STATE_CHANGE` | Изменение состояния |

---

## 3. Шаблон логирования в функции

### 3.1 Минимальный каркас

```typescript
// [START_PROCESS_ORDER]
/*
 * ANCHOR: PROCESS_ORDER
 * PURPOSE: Обработка заказа пользователя
 * ...
 */
async function processOrder(orderId: string, userId: string): Promise<OrderResult> {
  // ENTRY: фиксируем вход
  logLine("orders", "DEBUG", "processOrder", "PROCESS_ORDER", "ENTRY", {
    orderId,
    userId,
  });

  // BRANCH: логируем ветвление
  if (!orderId) {
    logLine("orders", "WARN", "processOrder", "PROCESS_ORDER", "ERROR", {
      reason: "missing_order_id",
    });
    logLine("orders", "DEBUG", "processOrder", "PROCESS_ORDER", "EXIT", {
      result: "rejected",
    });
    return { success: false, error: "MISSING_ORDER_ID" };
  }

  // DECISION: логируем решение
  const isValid = await validateOrder(orderId);
  logLine("orders", "DEBUG", "processOrder", "PROCESS_ORDER", "CHECK", {
    check: "order_validity",
    result: isValid,
  });

  if (!isValid) {
    logLine("orders", "WARN", "processOrder", "PROCESS_ORDER", "DECISION", {
      decision: "reject_invalid_order",
      orderId,
    });
    logLine("orders", "DEBUG", "processOrder", "PROCESS_ORDER", "EXIT", {
      result: "rejected",
      reason: "invalid_order",
    });
    return { success: false, error: "INVALID_ORDER" };
  }

  // STATE_CHANGE: логируем изменение
  const result = await executeOrder(orderId);
  logLine("orders", "INFO", "processOrder", "PROCESS_ORDER", "STATE_CHANGE", {
    entity: "order",
    id: orderId,
    from: "pending",
    to: "processing",
  });

  // EXIT: фиксируем выход
  logLine("orders", "DEBUG", "processOrder", "PROCESS_ORDER", "EXIT", {
    result: "success",
    orderId,
  });
  return { success: true, data: result };
}
// [END_PROCESS_ORDER]
```

### 3.2 Python-версия

```python
# [START_PROCESS_ORDER]
# ANCHOR: PROCESS_ORDER
# PURPOSE: Обработка заказа пользователя
# ...
def process_order(order_id: str, user_id: str) -> dict:
    log_line("orders", "DEBUG", "process_order", "PROCESS_ORDER", "ENTRY", {
        "order_id": order_id,
        "user_id": user_id,
    })
    
    if not order_id:
        log_line("orders", "WARN", "process_order", "PROCESS_ORDER", "ERROR", {
            "reason": "missing_order_id",
        })
        log_line("orders", "DEBUG", "process_order", "PROCESS_ORDER", "EXIT", {
            "result": "rejected",
        })
        return {"success": False, "error": "MISSING_ORDER_ID"}
    
    # ... остальная логика
    
    log_line("orders", "DEBUG", "process_order", "PROCESS_ORDER", "EXIT", {
        "result": "success",
        "order_id": order_id,
    })
    return {"success": True}
# [END_PROCESS_ORDER]
```

---

## 4. Детализация логирования

### 4.1 Уровни детализации по важности

| Уровень | Тип данных для логирования |
|---------|---------------------------|
| Критичный | Все входы/выходы, все решения, все ошибки |
| Важный | Входы/выходы, ключевые решения, ошибки |
| Обычный | Входы/выходы, ошибки |
| Вспомогательный | Только ошибки |

### 4.2 Критерии критичности блока

Блок считается критичным, если:
- Управляет деньгами/ресурсами
- Обеспечивает безопасность
- Является точкой интеграции
- Влияет на данные пользователя
- Выполняется редко (сложно воспроизвести)
- Имеет сложную условную логику

---

## 5. Логи для автоматического дебага

### 5.1 Информация для восстановления контекста

Лог должен содержать достаточно данных, чтобы ИИ мог:
1. Понять, какая ветка была выполнена
2. Понять, почему была выбрана эта ветка
3. Воспроизвести состояние на момент ошибки
4. Сопоставить с контрактом функции

### 5.2 Пример достаточного лог-блока

```typescript
// Хорошо: достаточно для автоматического анализа
logLine("orders", "ERROR", "processOrder", "PROCESS_ORDER", "ERROR", {
  reason: "payment_failed",
  orderId: "ORD-12345",
  userId: "USR-67890",
  amount: 1500.00,
  currency: "RUB",
  paymentProvider: "stripe",
  errorCode: "INSUFFICIENT_FUNDS",
  retryCount: 3,
  maxRetries: 3,
  suggestedAction: "notify_user",
});

// Плохо: недостаточно для анализа
logLine("orders", "ERROR", "processOrder", "PROCESS_ORDER", "ERROR", {
  message: "Payment failed",
});
```

---

## 6. Связка логов с контрактами

### 6.1 Проверка соответствия

Каждый лог уровня INFO/ERROR должен быть сопоставим с контрактом:

| Лог | Контракт |
|-----|----------|
| `EXIT { result: "success" }` | Соответствует постусловию успеха |
| `EXIT { result: "rejected" }` | Соответствует постусловию ошибки |
| `ERROR { reason: "..." }` | Объяснимо через предусловия |
| `STATE_CHANGE` | Отражён в `@SideEffects` |

### 6.2 Детектор расхождений

Если лог показывает поведение, не описанное в контракте — это признак:
1. Неполного контракта
2. Нарушения контракта
3. Требуется обновление контракта или реализация

---

## 7. Чеклист логирования

### 7.1 Перед сдачей кода

- [ ] Каждая критичная функция имеет ENTRY и EXIT логи
- [ ] Все ветвления имеют BRANCH или DECISION логи
- [ ] Все ошибки имеют ERROR логи с причиной
- [ ] Все логи содержат anchor, совпадающий с контрактом
- [ ] Данные в логах достаточны для воспроизведения контекста
- [ ] Нет декоративных логов без диагностической ценности
- [ ] Побочные эффекты отражены в логах (STATE_CHANGE)

### 7.2 Критерий готовности

Логирование считается готовым, если по логам ИИ может восстановить:
- Что произошло
- Почему произошло
- В каком месте кода произошло
- Какой был контекст
- Какой контракт был нарушен (если была ошибка)

---

## Эталон

- `.kilocode/rules/semantic-markup-examples/example-typescript.ts`
- `.kilocode/rules/semantic-markup-examples/example-python.py`
