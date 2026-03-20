"""
Quiz models for LMS System.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    
    def __str__(self):
        return f'{self.module.title} - {self.question[:50]}...'
    
    def save(self, *args, **kwargs):
        """Auto-set order_num if not provided."""
        if not self.order_num:
            max_order = Quiz.objects.filter(module=self.module).aggregate(
                max_order=models.Max('order_num')
            )['max_order']
            self.order_num = (max_order or 0) + 1
        super().save(*args, **kwargs)


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
    
    def __str__(self):
        return f'{self.quiz.question[:30]}... - {self.text[:30]}...'


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
    
    def __str__(self):
        return f'{self.user.email} - {self.quiz.question[:30]}... (попытка {self.attempt_number})'
    
    @classmethod
    def get_next_attempt_number(cls, user, quiz):
        """Get the next attempt number for a user and quiz."""
        last_attempt = cls.objects.filter(
            user=user,
            quiz=quiz
        ).order_by('-attempt_number').first()
        
        return (last_attempt.attempt_number + 1) if last_attempt else 1
    
    @classmethod
    def can_attempt(cls, user, quiz):
        """Check if user can attempt the quiz."""
        attempt_count = cls.objects.filter(user=user, quiz=quiz).count()
        return attempt_count < cls.MAX_ATTEMPTS


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
    
    def __str__(self):
        return f'{self.attempt} - {self.text[:30] if self.text else self.quiz_option.text[:30]}...'