"""Quizzes admin."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Quiz, QuizAnswer, QuizAttempt, QuizOption


class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 2


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['question', 'module', 'question_type', 'order_num', 'created_at']
    list_filter = ['question_type', 'created_at']
    search_fields = ['question', 'module__title']
    inlines = [QuizOptionInline]
    raw_id_fields = ['module']


@admin.register(QuizOption)
class QuizOptionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'text', 'is_correct', 'order_num']
    list_filter = ['is_correct']
    raw_id_fields = ['quiz']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'attempt_number', 'score', 'completed_at']
    list_filter = ['completed_at', 'attempt_number']
    raw_id_fields = ['user', 'quiz']


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'quiz_option', 'is_correct', 'created_at']
    list_filter = ['is_correct', 'created_at']
    raw_id_fields = ['attempt', 'quiz_option']