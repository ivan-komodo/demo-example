"""Quiz services."""

from decimal import Decimal

from django.contrib.auth import get_user_model

from .models import Quiz, QuizAnswer, QuizAttempt

User = get_user_model()


# === CHUNK: QUIZ_SERVICES_V1 [QUIZZES] ===
# Описание: Сервисные функции для расчёта результатов тестов.
# Dependencies: QUIZ_MODELS_V1


# [START_QUIZ_SERVICE]
# ANCHOR: QUIZ_SERVICE
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет методы для расчёта результатов тестов
# PURPOSE: Сервис для управления результатами тестов.
class QuizService:
    """Service for quiz management."""
    
    # [START_CALCULATE_SCORE]
    # ANCHOR: CALCULATE_SCORE
    # @PreConditions:
    # - attempt — валидный экземпляр QuizAttempt
    # @PostConditions:
    # - для открытых вопросов возвращает None (требуется ручная проверка)
    # - для тестов возвращает Decimal — процент правильных ответов
    # PURPOSE: Расчёт результата попытки прохождения теста.
    @staticmethod
    def calculate_score(attempt: QuizAttempt) -> Decimal:
        """Calculate score for a quiz attempt."""
        quiz = attempt.quiz
        
        if quiz.question_type == Quiz.QuestionType.OPEN:
            # Open answers need manual grading
            return None
        
        answers = attempt.answers.select_related('quiz_option')
        correct_answers = sum(1 for a in answers if a.is_correct)
        total_options = quiz.options.filter(is_correct=True).count()
        
        if total_options == 0:
            return Decimal('0.00')
        
        score = Decimal(str((correct_answers / total_options) * 100))
        return score
    # [END_CALCULATE_SCORE]
    
    # [START_GET_BEST_SCORE]
    # ANCHOR: GET_BEST_SCORE
    # @PreConditions:
    # - user — валидный пользователь
    # - quiz — валидный вопрос теста
    # @PostConditions:
    # - возвращает лучший результат среди всех попыток
    # - возвращает None, если попыток не было
    # PURPOSE: Получение лучшего результата пользователя по тесту.
    @staticmethod
    def get_best_score(user: User, quiz: Quiz) -> Decimal:
        """Get best score for a user on a quiz."""
        attempts = QuizAttempt.objects.filter(user=user, quiz=quiz)
        if not attempts.exists():
            return None
        
        return max(a.score for a in attempts if a.score is not None)
    # [END_GET_BEST_SCORE]


# [END_QUIZ_SERVICE]


# === END_CHUNK: QUIZ_SERVICES_V1 ===