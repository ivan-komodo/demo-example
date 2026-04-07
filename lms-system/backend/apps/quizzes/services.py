"""Quiz services."""

from decimal import Decimal

from django.contrib.auth import get_user_model

from typing import Optional

from core.utils import log_line

from .models import Quiz, QuizAnswer, QuizAttempt

User = get_user_model()


# === CHUNK: QUIZ_SERVICES_V1 [QUIZZES] ===
# Dependencies: QUIZ_MODELS_V1


# [START_QUIZ_SERVICE]
"""
ANCHOR: QUIZ_SERVICE
PURPOSE: Сервис для управления результатами тестов.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет методы для расчёта результатов тестов

@Invariants:
- все методы статические
- не изменяет состояние напрямую

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- все методы статические
"""
class QuizService:
    """Service for quiz management."""
    
    # [START_CALCULATE_SCORE]
    """
    ANCHOR: CALCULATE_SCORE
    PURPOSE: Расчёт результата попытки прохождения теста.

    @PreConditions:
    - attempt — валидный экземпляр QuizAttempt
    - attempt.quiz существует

    @PostConditions:
    - для открытых вопросов возвращает None (требуется ручная проверка)
    - для тестов возвращает Decimal — процент правильных ответов
    - при отсутствии правильных вариантов возвращает Decimal('0.00')

    @Invariants:
    - результат всегда Decimal или None
    - результат в диапазоне 0-100

    @SideEffects:
    - SELECT запрос к БД для получения answers и options

    @ForbiddenChanges:
    - логика для открытых вопросов (return None)
    - формула расчёта (correct/total * 100)
    """
    @staticmethod
    def calculate_score(attempt: QuizAttempt) -> Optional[Decimal]:
        log_line("quizzes", "DEBUG", "calculate_score", "CALCULATE_SCORE", "ENTRY", {
            "attempt_id": attempt.id,
            "quiz_id": attempt.quiz_id,
            "user_id": attempt.user_id,
        })
        
        quiz = attempt.quiz
        
        log_line("quizzes", "DEBUG", "calculate_score", "CALCULATE_SCORE", "BRANCH", {
            "branch": "question_type_check",
            "question_type": quiz.question_type,
        })
        
        if quiz.question_type == Quiz.QuestionType.OPEN:
            log_line("quizzes", "DEBUG", "calculate_score", "CALCULATE_SCORE", "DECISION", {
                "decision": "open_question_requires_manual_grading",
                "quiz_id": quiz.id,
            })
            log_line("quizzes", "DEBUG", "calculate_score", "CALCULATE_SCORE", "EXIT", {
                "result": None,
                "reason": "open_question",
            })
            return None
        
        answers = attempt.answers.select_related('quiz_option')
        correct_answers = sum(1 for a in answers if a.is_correct)
        total_options = quiz.options.filter(is_correct=True).count()
        
        log_line("quizzes", "DEBUG", "calculate_score", "CALCULATE_SCORE", "CHECK", {
            "check": "correct_answers_count",
            "correct_answers": correct_answers,
            "total_correct_options": total_options,
        })
        
        if total_options == 0:
            log_line("quizzes", "WARN", "calculate_score", "CALCULATE_SCORE", "DECISION", {
                "decision": "no_correct_options_defined",
                "quiz_id": quiz.id,
            })
            log_line("quizzes", "DEBUG", "calculate_score", "CALCULATE_SCORE", "EXIT", {
                "result": "0.00",
                "reason": "no_correct_options",
            })
            return Decimal('0.00')
        
        score = Decimal(str((correct_answers / total_options) * 100))
        
        log_line("quizzes", "INFO", "calculate_score", "CALCULATE_SCORE", "STATE_CHANGE", {
            "entity": "quiz_attempt",
            "id": attempt.id,
            "score_calculated": str(score),
            "correct_answers": correct_answers,
            "total_options": total_options,
        })
        log_line("quizzes", "DEBUG", "calculate_score", "CALCULATE_SCORE", "EXIT", {
            "result": str(score),
        })
        return score
    # [END_CALCULATE_SCORE]
    
    # [START_GET_BEST_SCORE]
    """
    ANCHOR: GET_BEST_SCORE
    PURPOSE: Получение лучшего результата пользователя по тесту.

    @PreConditions:
    - user — валидный пользователь
    - quiz — валидный вопрос теста

    @PostConditions:
    - возвращает лучший результат среди всех попыток
    - возвращает None, если попыток не было

    @Invariants:
    - результат всегда Decimal или None

    @SideEffects:
    - SELECT запрос к БД

    @ForbiddenChanges:
    - логика выбора max score
    """
    @staticmethod
    def get_best_score(user: User, quiz: Quiz) -> Optional[Decimal]:
        log_line("quizzes", "DEBUG", "get_best_score", "GET_BEST_SCORE", "ENTRY", {
            "user_id": user.id,
            "quiz_id": quiz.id,
        })
        
        attempts = QuizAttempt.objects.filter(user=user, quiz=quiz)
        
        log_line("quizzes", "DEBUG", "get_best_score", "GET_BEST_SCORE", "CHECK", {
            "check": "attempts_exist",
            "attempts_count": attempts.count(),
        })
        
        if not attempts.exists():
            log_line("quizzes", "DEBUG", "get_best_score", "GET_BEST_SCORE", "DECISION", {
                "decision": "no_attempts_found",
                "user_id": user.id,
                "quiz_id": quiz.id,
            })
            log_line("quizzes", "DEBUG", "get_best_score", "GET_BEST_SCORE", "EXIT", {
                "result": None,
                "reason": "no_attempts",
            })
            return None
        
        scores = [a.score for a in attempts if a.score is not None]
        
        log_line("quizzes", "DEBUG", "get_best_score", "GET_BEST_SCORE", "CHECK", {
            "check": "valid_scores",
            "scores_count": len(scores),
        })
        
        if not scores:
            log_line("quizzes", "DEBUG", "get_best_score", "GET_BEST_SCORE", "DECISION", {
                "decision": "no_valid_scores",
            })
            log_line("quizzes", "DEBUG", "get_best_score", "GET_BEST_SCORE", "EXIT", {
                "result": None,
                "reason": "no_valid_scores",
            })
            return None
        
        result = max(scores)
        
        log_line("quizzes", "INFO", "get_best_score", "GET_BEST_SCORE", "EXIT", {
            "result": str(result),
            "total_attempts": attempts.count(),
            "valid_scores_count": len(scores),
        })
        return result
    # [END_GET_BEST_SCORE]


# [END_QUIZ_SERVICE]


# === END_CHUNK: QUIZ_SERVICES_V1 ===
