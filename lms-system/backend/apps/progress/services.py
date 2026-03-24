"""Progress services."""

from django.db import transaction

from .models import UserProgress


# === CHUNK: PROGRESS_SERVICES_V1 [PROGRESS] ===
# Описание: Бизнес-логика для управления прогрессом пользователей.
# Dependencies: PROGRESS_MODELS_V1


# [START_PROGRESS_SERVICE_CLASS]
# ANCHOR: PROGRESS_SERVICE_CLASS
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет методы для управления прогрессом
# PURPOSE: Сервисный класс для инкапсуляции бизнес-логики прогресса.
class ProgressService:
    """Service class for progress operations."""
    
    # [START_GET_OR_CREATE_PROGRESS]
    # ANCHOR: GET_OR_CREATE_PROGRESS
    # @PreConditions:
    # - user аутентифицирован
    # - module_id указывает на существующий модуль
    # @PostConditions:
    # - возвращает существующую или новую запись прогресса
    # PURPOSE: Получение или создание записи прогресса для пользователя по модулю.
    @staticmethod
    def get_or_create_progress(user, module):
        """Get existing progress or create new one."""
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            module=module,
            defaults={'status': UserProgress.Status.NOT_STARTED}
        )
        return progress, created
    # [END_GET_OR_CREATE_PROGRESS]
    
    # [START_MARK_IN_PROGRESS]
    # ANCHOR: MARK_IN_PROGRESS
    # @PreConditions:
    # - user аутентифицирован
    # - module_id указывает на существующий модуль
    # @PostConditions:
    # - статус прогресса изменён на IN_PROGRESS
    # PURPOSE: Отметить модуль как "в процессе прохождения".
    @staticmethod
    @transaction.atomic
    def mark_in_progress(user, module):
        """Mark module as in progress."""
        progress, _ = ProgressService.get_or_create_progress(user, module)
        progress.status = UserProgress.Status.IN_PROGRESS
        progress.save()
        return progress
    # [END_MARK_IN_PROGRESS]
    
    # [START_MARK_COMPLETED]
    # ANCHOR: MARK_COMPLETED
    # @PreConditions:
    # - user аутентифицирован
    # - module_id указывает на существующий модуль
    # - score в допустимом диапазоне (если передан)
    # @PostConditions:
    # - статус прогресса изменён на COMPLETED
    # - установлена дата завершения
    # - установлен балл (если передан)
    # PURPOSE: Отметить модуль как завершённый с возможным указанием балла.
    @staticmethod
    @transaction.atomic
    def mark_completed(user, module, score=None):
        """Mark module as completed."""
        progress, _ = ProgressService.get_or_create_progress(user, module)
        progress.status = UserProgress.Status.COMPLETED
        progress.mark_completed(score=score)
        return progress
    # [END_MARK_COMPLETED]


# [END_PROGRESS_SERVICE_CLASS]


# === END_CHUNK: PROGRESS_SERVICES_V1 ===