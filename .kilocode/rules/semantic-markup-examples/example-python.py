# Эталонные фрагменты семантической разметки для Python (справочник, не исполнять как модуль).

# --- Design by Contract + явный конец блока ---
# [START_RECONCILE_LOGIC]
# ANCHOR: Финансовый модуль сверки данных
# @PreConditions:
# - data: непустой список транзакций
# - threshold: положительное число
# @PostConditions:
# - возвращает словарь с несовпадениями
# PURPOSE: Идентификация расхождений в платежах между системами.
def reconcile_payments(data, threshold=0.01):
    return {}


# [END_RECONCILE_LOGIC]

# --- Иерархические якоря (подсистема → фича → внутренний блок) ---
# ANCHOR_LAYER_1: AUTHENTICATION_SYSTEM
# Общее описание: Обработка регистрации и сессий.

# ANCHOR_LAYER_2: USER_REGISTRATION
def register_user(username: str, password: str) -> bool:
    # ANCHOR_LAYER_3: PASSWORD_VALIDATION
    # CRITICAL: Минимум 8 символов, 1 цифра.
    if len(password) < 8:
        return False
    # [END_VALIDATION]
    return True

# [END_REGISTRATION]
# [END_AUTH_SYSTEM]

# --- Критическая зона ответственности ---
# ANCHOR_CRITICAL: Валидация финансовых транзакций
# !ОБЯЗАТЕЛЬНО: Проверять остаток на счете ДО списания.
# !ЗАПРЕЩЕНО: Проводить операции с отрицательной суммой.
def process_transaction(amount: float, balance: float) -> None:
    pass


# END_ANCHOR_CRITICAL

# --- Семантический чанк (карта модуля) ---
# === CHUNK: TASK_CLASS_V1 [CORE] ===
# Описание: Базовая структура задачи и основная бизнес-логика.
# Dependencies: STORAGE_V1, UI_V1
class Task:
    pass


# === END_CHUNK: TASK_CLASS_V1 ===

# === EDITABLE SECTION START: LOGIC_DISCOUNT ===
# Здесь допускаются правки логики расчёта скидок по запросу.
def calculate_discount(price: float, user_category: str) -> float:
    return price * 0.9 if user_category == "gold" else price


# == EDITABLE SECTION END ==

# ANCHOR: PRICING_CORE (не редактировать без явного согласования)
