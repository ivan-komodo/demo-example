"""
Quiz models for LMS System.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# === CHUNK: QUIZ_MODELS_V1 [QUIZZES] ===
# Описание: Модели для тестов, вариантов ответов, попыток и ответов.
# Dependencies: COURSE_MODELS_V1


# [START_QUIZ_MODEL]
# ANCHOR: QUIZ_MODEL
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт модель Quiz с полями module, question, question_type, order_num
# PURPOSE: Модель вопроса теста, привязанного к модулю.
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
    # ANCHOR: QUIZ_STR
    # @PreConditions:
    # - экземпляр Quiz существует
    # @PostConditions:
    # - возвращает строковое представление вопроса
    # PURPOSE: Строковое представление вопроса теста.
    def __str__(self):
        return f'{self.module.title} - {self.question[:50]}...'
    # [END_QUIZ_STR]
    
    # [START_QUIZ_SAVE]
    # ANCHOR: QUIZ_SAVE
    # @PreConditions:
    # - экземпляр Quiz инициализирован
    # @PostConditions:
    # - при отсутствии order_num устанавливает следующий по порядку
    # - экземпляр сохранён в БД
    # PURPOSE: Автоматическая установка порядкового номера при сохранении.
    def save(self, *args, **kwargs):
        """Auto-set order_num if not provided."""
        if not self.order_num:
            max_order = Quiz.objects.filter(module=self.module).aggregate(
                max_order=models.Max('order_num')
            )['max_order']
            self.order_num = (max_order or 0) + 1
        super().save(*args, **kwargs)
    # [END_QUIZ_SAVE]


# [END_QUIZ_MODEL]


# [START_QUIZ_OPTION_MODEL]
# ANCHOR: QUIZ_OPTION_MODEL
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт модель QuizOption с полями quiz, text, is_correct, order_num
# PURPOSE: Модель варианта ответа на вопрос теста.
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
    # ANCHOR: QUIZ_OPTION_STR
    # @PreConditions:
    # - экземпляр QuizOption существует
    # @PostConditions:
    # - возвращает строковое представление варианта ответа
    # PURPOSE: Строковое представление варианта ответа.
    def __str__(self):
        return f'{self.quiz.question[:30]}... - {self.text[:30]}...'
    # [END_QUIZ_OPTION_STR]


# [END_QUIZ_OPTION_MODEL]


# [START_QUIZ_ATTEMPT_MODEL]
# ANCHOR: QUIZ_ATTEMPT_MODEL
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт модель QuizAttempt с полями user, quiz, attempt_number, score
# PURPOSE: Модель попытки прохождения теста пользователем.
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
    # ANCHOR: QUIZ_ATTEMPT_STR
    # @PreConditions:
    # - экземпляр QuizAttempt существует
    # @PostConditions:
    # - возвращает строковое представление попытки
    # PURPOSE: Строковое представление попытки теста.
    def __str__(self):
        return f'{self.user.email} - {self.quiz.question[:30]}... (попытка {self.attempt_number})'
    # [END_QUIZ_ATTEMPT_STR]
    
    # [START_GET_NEXT_ATTEMPT_NUMBER]
    # ANCHOR: GET_NEXT_ATTEMPT_NUMBER
    # @PreConditions:
    # - user — валидный пользователь
    # - quiz — валидный вопрос теста
    # @PostConditions:
    # - возвращает номер следующей попытки (int)
    # PURPOSE: Получение номера следующей попытки для пользователя и теста.
    @classmethod
    def get_next_attempt_number(cls, user, quiz):
        """Get the next attempt number for a user and quiz."""
        last_attempt = cls.objects.filter(
            user=user,
            quiz=quiz
        ).order_by('-attempt_number').first()
        
        return (last_attempt.attempt_number + 1) if last_attempt else 1
    # [END_GET_NEXT_ATTEMPT_NUMBER]
    
    # [START_CAN_ATTEMPT]
    # ANCHOR: CAN_ATTEMPT
    # @PreConditions:
    # - user — валидный пользователь
    # - quiz — валидный вопрос теста
    # @PostConditions:
    # - возвращает True, если пользователь может попытаться пройти тест
    # - возвращает False, если достигнут лимит попыток
    # PURPOSE: Проверка возможности новой попытки прохождения теста.
    @classmethod
    def can_attempt(cls, user, quiz):
        """Check if user can attempt the quiz."""
        attempt_count = cls.objects.filter(user=user, quiz=quiz).count()
        return attempt_count < cls.MAX_ATTEMPTS
    # [END_CAN_ATTEMPT]


# [END_QUIZ_ATTEMPT_MODEL]


# [START_QUIZ_ANSWER_MODEL]
# ANCHOR: QUIZ_ANSWER_MODEL
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт модель QuizAnswer с полями attempt, quiz_option, text, is_correct
# PURPOSE: Модель ответа пользователя на вопрос теста.
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
    # ANCHOR: QUIZ_ANSWER_STR
    # @PreConditions:
    # - экземпляр QuizAnswer существует
    # @PostConditions:
    # - возвращает строковое представление ответа
    # PURPOSE: Строковое представление ответа на тест.
    def __str__(self):
        return f'{self.attempt} - {self.text[:30] if self.text else self.quiz_option.text[:30]}...'
    # [END_QUIZ_ANSWER_STR]


# [END_QUIZ_ANSWER_MODEL]


# === END_CHUNK: QUIZ_MODELS_V1 ===