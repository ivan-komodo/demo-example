"""Progress services."""

from django.db import transaction

from core.utils import log_line

from .models import UserProgress


# === CHUNK: PROGRESS_SERVICES_V1 [PROGRESS] ===
# Описание: Бизнес-логика для управления прогрессом пользователей.
# Dependencies: PROGRESS_MODELS_V1


# [START_PROGRESS_SERVICE_CLASS]
"""
ANCHOR: PROGRESS_SERVICE_CLASS
PURPOSE: Сервисный класс для инкапсуляции бизнес-логики прогресса.

@PreConditions:
- нет нетривиальных предусловий для объявления класса

@PostConditions:
- предоставляет методы для управления прогрессом (get_or_create, mark_in_progress, mark_completed)

@Invariants:
- все методы класса статические
- все методы работы с прогрессом используют транзакции

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- все методы должны быть @staticmethod
"""
class ProgressService:
    """Service class for progress operations."""
    
    # [START_GET_OR_CREATE_PROGRESS]
    """
    ANCHOR: GET_OR_CREATE_PROGRESS
    PURPOSE: Получение или создание записи прогресса для пользователя по модулю.

    @PreConditions:
    - user аутентифицирован и существует
    - module существует в БД

    @PostConditions:
    - возвращает tuple (progress, created)
    - created=True если запись создана, False если получена существующая
    - при создании статус = NOT_STARTED

    @Invariants:
    - гарантируется уникальность (user, module) через get_or_create

    @SideEffects:
    - возможное создание записи в БД

    @ForbiddenChanges:
    - defaults при создании всегда {'status': NOT_STARTED}
    """
    @staticmethod
    def get_or_create_progress(user, module):
        log_line("progress", "DEBUG", "get_or_create_progress", "GET_OR_CREATE_PROGRESS", "ENTRY", {
            "user_id": user.id,
            "module_id": module.id,
        })
        
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            module=module,
            defaults={'status': UserProgress.Status.NOT_STARTED}
        )
        
        log_line("progress", "DEBUG", "get_or_create_progress", "GET_OR_CREATE_PROGRESS", "EXIT", {
            "progress_id": progress.id,
            "created": created,
            "status": progress.status,
        })
        
        return progress, created
    # [END_GET_OR_CREATE_PROGRESS]
    
    # [START_SERVICE_MARK_IN_PROGRESS]
    """
    ANCHOR: SERVICE_MARK_IN_PROGRESS
    PURPOSE: Отметить модуль как "в процессе прохождения" через сервис.

    @PreConditions:
    - user аутентифицирован
    - module существует в БД

    @PostConditions:
    - статус прогресса изменён на IN_PROGRESS
    - возвращается объект progress

    @Invariants:
    - операция атомарна (transaction.atomic)

    @SideEffects:
    - запись в БД (save progress)

    @ForbiddenChanges:
    - @transaction.atomic (гарантия атомарности)
    """
    @staticmethod
    @transaction.atomic
    def mark_in_progress(user, module):
        log_line("progress", "DEBUG", "mark_in_progress", "SERVICE_MARK_IN_PROGRESS", "ENTRY", {
            "user_id": user.id,
            "module_id": module.id,
        })
        
        progress, created = ProgressService.get_or_create_progress(user, module)
        
        log_line("progress", "DEBUG", "mark_in_progress", "SERVICE_MARK_IN_PROGRESS", "BRANCH", {
            "created": created,
            "current_status": progress.status,
        })
        
        progress.status = UserProgress.Status.IN_PROGRESS
        progress.save()
        
        log_line("progress", "INFO", "mark_in_progress", "SERVICE_MARK_IN_PROGRESS", "STATE_CHANGE", {
            "entity": "progress",
            "id": progress.id,
            "to": "in_progress",
        })
        
        log_line("progress", "DEBUG", "mark_in_progress", "SERVICE_MARK_IN_PROGRESS", "EXIT", {
            "result": "success",
            "progress_id": progress.id,
        })
        
        return progress
    # [END_SERVICE_MARK_IN_PROGRESS]
    
    # [START_SERVICE_MARK_COMPLETED]
    """
    ANCHOR: SERVICE_MARK_COMPLETED
    PURPOSE: Отметить модуль как завершённый с возможным указанием балла через сервис.

    @PreConditions:
    - user аутентифицирован
    - module существует в БД
    - score в допустимом диапазоне (если передан)

    @PostConditions:
    - статус прогресса изменён на COMPLETED
    - установлена дата завершения
    - установлен балл (если передан)

    @Invariants:
    - операция атомарна (transaction.atomic)

    @SideEffects:
    - запись в БД (save progress)

    @ForbiddenChanges:
    - @transaction.atomic (гарантия атомарности)
    """
    @staticmethod
    @transaction.atomic
    def mark_completed(user, module, score=None):
        log_line("progress", "DEBUG", "mark_completed", "SERVICE_MARK_COMPLETED", "ENTRY", {
            "user_id": user.id,
            "module_id": module.id,
            "score": str(score) if score else None,
        })
        
        progress, created = ProgressService.get_or_create_progress(user, module)
        
        log_line("progress", "DEBUG", "mark_completed", "SERVICE_MARK_COMPLETED", "BRANCH", {
            "created": created,
            "score_provided": score is not None,
        })
        
        progress.status = UserProgress.Status.COMPLETED
        progress.mark_completed(score=score)
        
        log_line("progress", "INFO", "mark_completed", "SERVICE_MARK_COMPLETED", "STATE_CHANGE", {
            "entity": "progress",
            "id": progress.id,
            "to": "completed",
            "score": str(score) if score else None,
        })
        
        log_line("progress", "DEBUG", "mark_completed", "SERVICE_MARK_COMPLETED", "EXIT", {
            "result": "success",
            "progress_id": progress.id,
        })
        
        return progress
    # [END_SERVICE_MARK_COMPLETED]


# [END_PROGRESS_SERVICE_CLASS]


# === END_CHUNK: PROGRESS_SERVICES_V1 ===
