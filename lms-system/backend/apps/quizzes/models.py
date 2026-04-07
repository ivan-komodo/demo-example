"""
Quiz models for LMS System.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import log_line


# === CHUNK: QUIZ_MODELS_V1 [QUIZZES] ===
# Dependencies: COURSE_MODELS_V1


# [START_QUIZ_MODEL]
"""
ANCHOR: QUIZ_MODEL
PURPOSE: Модель вопроса теста, привязанного к модулю.

@PreConditions:
- нет нетривиальных предусловий

@PostConditions:
- создаёт модель Quiz с полями module, question, question_type, order_num
- при сохранении автоматически устанавливает order_num если не задан

@Invariants:
- question_type всегда один из: single, multiple, open
- order_num всегда положительное число
- каждый тест привязан к одному модулю

@SideEffects:
- при save() может изменять order_num других тестов модуля

@ForbiddenChanges:
- типы вопросов (single, multiple, open)
- связь с Module (CASCADE delete)
"""
class Quiz(models.Model):
    """
    Model for quiz questions.
    
    A quiz belongs to a module and supports different question types.
    """
    
    class QuestionType(models.TextChoices):
        SINGLE = 'single', _('Один правильный')
        MULTIPLE = 'multiple', _('Несколько правильных')
        OPEN = 'open', _('Открытый ответ')
    
    module = models.ForeignKey(
        'courses.Module',
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name=_('Модуль'),
    )
    question = models.TextField(_('Вопрос'))
    question_type = models.CharField(
        _('Тип вопроса'),
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE,
    )
    order_num = models.PositiveIntegerField(_('Порядковый номер'), default=0)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Тест')
        verbose_name_plural = _('Тесты')
        ordering = ['order_num', 'created_at']
    
    # [START_QUIZ_STR]
    """
    ANCHOR: QUIZ_STR
    PURPOSE: Строковое представление вопроса теста.

    @PreConditions:
    - экземпляр Quiz существует

    @PostConditions:
    - возвращает строковое представление вопроса

    @Invariants:
    - всегда возвращает строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода (module.title - question[:50]...)
    """
    def __str__(self):
        log_line("quizzes", "DEBUG", "quiz_str", "QUIZ_STR", "ENTRY", {
            "quiz_id": self.id,
            "module_id": self.module_id,
        })
        result = f'{self.module.title} - {self.question[:50]}...'
        log_line("quizzes", "DEBUG", "quiz_str", "QUIZ_STR", "EXIT", {
            "result": result[:50],
        })
        return result
    # [END_QUIZ_STR]
    
    # [START_QUIZ_SAVE]
    """
    ANCHOR: QUIZ_SAVE
    PURPOSE: Автоматическая установка порядкового номера при сохранении.

    @PreConditions:
    - экземпляр Quiz инициализирован
    - module привязан к валидному объекту Module

    @PostConditions:
    - при отсутствии order_num устанавливает следующий по порядку
    - экземпляр сохранён в БД

    @Invariants:
    - order_num всегда >= 1
    - order_num уникален в рамках модуля

    @SideEffects:
- запись в БД
    - возможен SELECT для определения max order_num

    @ForbiddenChanges:
    - логика вычисления order_num (max + 1)
    """
    def save(self, *args, **kwargs):
        log_line("quizzes", "DEBUG", "quiz_save", "QUIZ_SAVE", "ENTRY", {
            "quiz_id": self.id,
            "module_id": self.module_id,
            "order_num": self.order_num,
        })
        
        if not self.order_num:
            max_order = Quiz.objects.filter(module=self.module).aggregate(
                max_order=models.Max('order_num')
            )['max_order']
            self.order_num = (max_order or 0) + 1
            log_line("quizzes", "DEBUG", "quiz_save", "QUIZ_SAVE", "STATE_CHANGE", {
                "action": "auto_order_num",
                "new_order_num": self.order_num,
            })
        
        super().save(*args, **kwargs)
        log_line("quizzes", "DEBUG", "quiz_save", "QUIZ_SAVE", "EXIT", {
            "quiz_id": self.id,
            "order_num": self.order_num,
        })
    # [END_QUIZ_SAVE]


# [END_QUIZ_MODEL]


# [START_QUIZ_OPTION_MODEL]
"""
ANCHOR: QUIZ_OPTION_MODEL
PURPOSE: Модель варианта ответа на вопрос теста.

@PreConditions:
- нет нетривиальных предусловий

@PostConditions:
- создаёт модель QuizOption с полями quiz, text, is_correct, order_num

@Invariants:
- каждый вариант привязан к одному тесту
- is_correct всегда True или False

@SideEffects:
- нет побочных эффектов на уровне модели

@ForbiddenChanges:
- связь с Quiz (CASCADE delete)
"""
class QuizOption(models.Model):
    """
    Model for quiz answer options.
    
    Options belong to a quiz and indicate if they are correct.
    """
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name=_('Тест'),
    )
    text = models.TextField(_('Текст ответа'))
    is_correct = models.BooleanField(_('Правильный'), default=False)
    order_num = models.PositiveIntegerField(_('Порядковый номер'), default=0)
    
    class Meta:
        verbose_name = _('Вариант ответа')
        verbose_name_plural = _('Варианты ответов')
        ordering = ['order_num', 'id']
    
    # [START_QUIZ_OPTION_STR]
    """
    ANCHOR: QUIZ_OPTION_STR
    PURPOSE: Строковое представление варианта ответа.

    @PreConditions:
    - экземпляр QuizOption существует

    @PostConditions:
    - возвращает строковое представление варианта ответа

    @Invariants:
    - всегда возвращает строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода
    """
    def __str__(self):
        log_line("quizzes", "DEBUG", "quiz_option_str", "QUIZ_OPTION_STR", "ENTRY", {
            "option_id": self.id,
            "quiz_id": self.quiz_id,
        })
        result = f'{self.quiz.question[:30]}... - {self.text[:30]}...'
        log_line("quizzes", "DEBUG", "quiz_option_str", "QUIZ_OPTION_STR", "EXIT", {
            "result": result[:50],
        })
        return result
    # [END_QUIZ_OPTION_STR]


# [END_QUIZ_OPTION_MODEL]


# [START_QUIZ_ATTEMPT_MODEL]
"""
ANCHOR: QUIZ_ATTEMPT_MODEL
PURPOSE: Модель попытки прохождения теста пользователем.

@PreConditions:
- нет нетривиальных предусловий

@PostConditions:
- создаёт модель QuizAttempt с полями user, quiz, attempt_number, score
- attempt_number автоматически инкрементируется для каждого user+quiz

@Invariants:
- максимальное количество попыток = MAX_ATTEMPTS (3)
- score всегда Decimal(5,2) или None
- unique_together: user, quiz, attempt_number

@SideEffects:
- нет побочных эффектов на уровне модели

@ForbiddenChanges:
- MAX_ATTEMPTS = 3 (бизнес-ограничение)
- unique_together constraint
"""
class QuizAttempt(models.Model):
    """
    Model for quiz attempts.
    
    Tracks user attempts to answer a quiz with score.
    """
    
    MAX_ATTEMPTS = 3
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name=_('Пользователь'),
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_('Тест'),
    )
    attempt_number = models.PositiveIntegerField(_('Номер попытки'), default=1)
    score = models.DecimalField(
        _('Результат'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    completed_at = models.DateTimeField(_('Дата завершения'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Попытка теста')
        verbose_name_plural = _('Попытки тестов')
        ordering = ['-completed_at']
        unique_together = ['user', 'quiz', 'attempt_number']
    
    # [START_QUIZ_ATTEMPT_STR]
    """
    ANCHOR: QUIZ_ATTEMPT_STR
    PURPOSE: Строковое представление попытки теста.

    @PreConditions:
    - экземпляр QuizAttempt существует

    @PostConditions:
    - возвращает строковое представление попытки

    @Invariants:
    - всегда возвращает строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода
    """
    def __str__(self):
        log_line("quizzes", "DEBUG", "quiz_attempt_str", "QUIZ_ATTEMPT_STR", "ENTRY", {
            "attempt_id": self.id,
            "user_id": self.user_id,
            "quiz_id": self.quiz_id,
        })
        result = f'{self.user.email} - {self.quiz.question[:30]}... (попытка {self.attempt_number})'
        log_line("quizzes", "DEBUG", "quiz_attempt_str", "QUIZ_ATTEMPT_STR", "EXIT", {
            "result": result[:50],
        })
        return result
    # [END_QUIZ_ATTEMPT_STR]
    
    # [START_GET_NEXT_ATTEMPT_NUMBER]
    """
    ANCHOR: GET_NEXT_ATTEMPT_NUMBER
    PURPOSE: Получение номера следующей попытки для пользователя и теста.

    @PreConditions:
    - user — валидный пользователь
    - quiz — валидный вопрос теста

    @PostConditions:
    - возвращает номер следующей попытки (int >= 1)

    @Invariants:
    - результат всегда >= 1
    - резльтат = последняя попытка + 1 или 1

    @SideEffects:
    - SELECT запрос к БД для поиска последней попытки

    @ForbiddenChanges:
    - логика вычисления (last + 1 или 1)
    """
    @classmethod
    def get_next_attempt_number(cls, user, quiz):
        log_line("quizzes", "DEBUG", "get_next_attempt_number", "GET_NEXT_ATTEMPT_NUMBER", "ENTRY", {
            "user_id": user.id,
            "quiz_id": quiz.id,
        })
        
        last_attempt = cls.objects.filter(
            user=user,
            quiz=quiz
        ).order_by('-attempt_number').first()
        
        result = (last_attempt.attempt_number + 1) if last_attempt else 1
        
        log_line("quizzes", "DEBUG", "get_next_attempt_number", "GET_NEXT_ATTEMPT_NUMBER", "EXIT", {
            "next_attempt_number": result,
            "had_previous_attempts": last_attempt is not None,
        })
        return result
    # [END_GET_NEXT_ATTEMPT_NUMBER]
    
    # [START_CAN_ATTEMPT]
    """
    ANCHOR: CAN_ATTEMPT
    PURPOSE: Проверка возможности новой попытки прохождения теста.

    @PreConditions:
    - user — валидный пользователь
    - quiz — валидный вопрос теста

    @PostConditions:
    - возвращает True, если попыток < MAX_ATTEMPTS
    - возвращает False, если достигнут лимит попыток

    @Invariants:
    - всегда возвращает bool
    - лимит всегда MAX_ATTEMPTS

    @SideEffects:
    - SELECT COUNT запрос к БД

    @ForbiddenChanges:
    - сравнение с MAX_ATTEMPTS
    """
    @classmethod
    def can_attempt(cls, user, quiz):
        log_line("quizzes", "DEBUG", "can_attempt", "CAN_ATTEMPT", "ENTRY", {
            "user_id": user.id,
            "quiz_id": quiz.id,
        })
        
        attempt_count = cls.objects.filter(user=user, quiz=quiz).count()
        result = attempt_count < cls.MAX_ATTEMPTS
        
        log_line("quizzes", "DEBUG", "can_attempt", "CAN_ATTEMPT", "DECISION", {
            "decision": "allow_attempt" if result else "limit_reached",
            "current_attempts": attempt_count,
            "max_attempts": cls.MAX_ATTEMPTS,
        })
        log_line("quizzes", "DEBUG", "can_attempt", "CAN_ATTEMPT", "EXIT", {
            "result": result,
        })
        return result
    # [END_CAN_ATTEMPT]


# [END_QUIZ_ATTEMPT_MODEL]


# [START_QUIZ_ANSWER_MODEL]
"""
ANCHOR: QUIZ_ANSWER_MODEL
PURPOSE: Модель ответа пользователя на вопрос теста.

@PreConditions:
- нет нетривиальных предусловий

@PostConditions:
- создаёт модель QuizAnswer с полями attempt, quiz_option, text, is_correct

@Invariants:
- каждый ответ привязан к одной попытке
- is_correct может быть None (для открытых вопросов)

@SideEffects:
- нет побочных эффектов на уровне модели

@ForbiddenChanges:
- связь с QuizAttempt (CASCADE delete)
"""
class QuizAnswer(models.Model):
    """
    Model for quiz answers.
    
    Stores individual answers from quiz attempts.
    """
    
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('Попытка'),
    )
    quiz_option = models.ForeignKey(
        QuizOption,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('Вариант ответа'),
        null=True,
        blank=True,
    )
    text = models.TextField(_('Текст ответа'), blank=True)
    is_correct = models.BooleanField(_('Правильный'), null=True, blank=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Ответ на тест')
        verbose_name_plural = _('Ответы на тесты')
        ordering = ['created_at']
    
    # [START_QUIZ_ANSWER_STR]
    """
    ANCHOR: QUIZ_ANSWER_STR
    PURPOSE: Строковое представление ответа на тест.

    @PreConditions:
    - экземпляр QuizAnswer существует

    @PostConditions:
    - возвращает строковое представление ответа

    @Invariants:
    - всегда возвращает строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода
    """
    def __str__(self):
        log_line("quizzes", "DEBUG", "quiz_answer_str", "QUIZ_ANSWER_STR", "ENTRY", {
            "answer_id": self.id,
            "attempt_id": self.attempt_id,
        })
        result = f'{self.attempt} - {self.text[:30] if self.text else self.quiz_option.text[:30]}...'
        log_line("quizzes", "DEBUG", "quiz_answer_str", "QUIZ_ANSWER_STR", "EXIT", {
            "result": result[:50],
        })
        return result
    # [END_QUIZ_ANSWER_STR]


# [END_QUIZ_ANSWER_MODEL]


# === END_CHUNK: QUIZ_MODELS_V1 ===
