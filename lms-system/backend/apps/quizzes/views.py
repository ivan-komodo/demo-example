"""Quiz views."""

from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser
from core.utils import log_line

from .models import Quiz, QuizAnswer, QuizAttempt, QuizOption
from .serializers import (
    QuizAttemptSerializer,
    QuizCreateSerializer,
    QuizListSerializer,
    QuizSerializer,
    SubmitAnswerSerializer,
)


# === CHUNK: QUIZ_VIEWS_V1 [QUIZZES] ===
# Dependencies: QUIZ_MODELS_V1, QUIZ_SERIALIZERS_V1


# [START_QUIZ_VIEWSET]
"""
ANCHOR: QUIZ_VIEWSET
PURPOSE: ViewSet для управления вопросами тестов.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет CRUD операции для тестов
- предоставляет action для отправки ответов

@Invariants:
- все действия требуют аутентификации
- пользователи видят только тесты доступных модулей

@SideEffects:
- CRUD операции изменяют БД
- submit action создаёт попытки и ответы

@ForbiddenChanges:
- permission_classes = [IsAuthenticated]
- MAX_ATTEMPTS ограничение
"""
class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for Quiz model."""
    
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticated]
    
    # [START_GET_SERIALIZER_CLASS_QUIZ]
    """
    ANCHOR: GET_SERIALIZER_CLASS_QUIZ
    PURPOSE: Выбор сериализатора в зависимости от действия.

    @PreConditions:
    - request.user аутентифицирован
    - self.action определён

    @PostConditions:
    - возвращает QuizCreateSerializer для create
    - возвращает QuizListSerializer для list
    - возвращает QuizSerializer для остальных действий

    @Invariants:
    - всегда возвращает класс сериализатора

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - маппинг action -> serializer
    """
    def get_serializer_class(self):
        log_line("quizzes", "DEBUG", "get_serializer_class", "GET_SERIALIZER_CLASS_QUIZ", "ENTRY", {
            "action": self.action,
        })
        
        if self.action == 'create':
            result = QuizCreateSerializer
        elif self.action == 'list':
            result = QuizListSerializer
        else:
            result = QuizSerializer
        
        log_line("quizzes", "DEBUG", "get_serializer_class", "GET_SERIALIZER_CLASS_QUIZ", "EXIT", {
            "serializer": result.__name__,
        })
        return result
    # [END_GET_SERIALIZER_CLASS_QUIZ]
    
    # [START_GET_QUERYSET_QUIZ]
    """
    ANCHOR: GET_QUERYSET_QUIZ
    PURPOSE: Фильтрация тестов по модулю через query-параметры.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - при наличии module_id фильтрует тесты по модулю
    - возвращает QuerySet с prefetch_related и select_related

    @Invariants:
    - всегда возвращает QuerySet

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - prefetch_related('options')
    - select_related('module')
    """
    def get_queryset(self):
        log_line("quizzes", "DEBUG", "get_queryset", "GET_QUERYSET_QUIZ", "ENTRY", {
            "user_id": self.request.user.id,
        })
        
        queryset = Quiz.objects.prefetch_related('options').select_related('module')
        module_id = self.request.query_params.get('module_id')
        
        log_line("quizzes", "DEBUG", "get_queryset", "GET_QUERYSET_QUIZ", "BRANCH", {
            "branch": "module_filter",
            "module_id": module_id,
        })
        
        if module_id:
            queryset = queryset.filter(module_id=module_id)
            log_line("quizzes", "DEBUG", "get_queryset", "GET_QUERYSET_QUIZ", "STATE_CHANGE", {
                "action": "filter_by_module",
                "module_id": module_id,
            })
        
        log_line("quizzes", "DEBUG", "get_queryset", "GET_QUERYSET_QUIZ", "EXIT", {
            "queryset_count": queryset.count(),
        })
        return queryset
    # [END_GET_QUERYSET_QUIZ]
    
    # [START_SUBMIT_QUIZ]
    """
    ANCHOR: SUBMIT_QUIZ
    PURPOSE: Отправка ответов на тест и получение результата.

    @PreConditions:
    - тест существует
    - request.user аутентифицирован
    - пользователь не достиг лимита попыток (MAX_ATTEMPTS)

    @PostConditions:
    - создаётся новая попытка QuizAttempt
    - вычисляется и сохраняется результат
    - возвращается результат попытки

    @Invariants:
    - attempt_number автоинкрементируется
    - score в диапазоне 0-100 или None

    @SideEffects:
    - создание QuizAttempt
    - создание QuizAnswer(s)
    - UPDATE attempt.score

    @ForbiddenChanges:
    - проверка лимита попыток (MAX_ATTEMPTS)
    - логика расчёта score
    """
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        log_line("quizzes", "DEBUG", "submit", "SUBMIT_QUIZ", "ENTRY", {
            "user_id": request.user.id,
            "quiz_id": pk,
        })
        
        quiz = self.get_object()
        
        log_line("quizzes", "DEBUG", "submit", "SUBMIT_QUIZ", "CHECK", {
            "check": "can_attempt",
            "quiz_id": quiz.id,
            "user_id": request.user.id,
        })
        
        if not QuizAttempt.can_attempt(request.user, quiz):
            log_line("quizzes", "WARN", "submit", "SUBMIT_QUIZ", "ERROR", {
                "reason": "max_attempts_reached",
                "quiz_id": quiz.id,
                "user_id": request.user.id,
                "max_attempts": QuizAttempt.MAX_ATTEMPTS,
            })
            log_line("quizzes", "DEBUG", "submit", "SUBMIT_QUIZ", "EXIT", {
                "result": "rejected",
                "reason": "max_attempts",
            })
            return Response(
                {'error': 'Достигнут лимит попыток (максимум 3).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        attempt_number = QuizAttempt.get_next_attempt_number(request.user, quiz)
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            attempt_number=attempt_number
        )
        
        log_line("quizzes", "INFO", "submit", "SUBMIT_QUIZ", "STATE_CHANGE", {
            "action": "attempt_created",
            "attempt_id": attempt.id,
            "attempt_number": attempt_number,
            "quiz_id": quiz.id,
            "user_id": request.user.id,
        })
        
        score = Decimal('0.00')
        total_questions = 1
        
        log_line("quizzes", "DEBUG", "submit", "SUBMIT_QUIZ", "BRANCH", {
            "branch": "question_type",
            "question_type": quiz.question_type,
        })
        
        if quiz.question_type == Quiz.QuestionType.OPEN:
            log_line("quizzes", "DEBUG", "submit", "SUBMIT_QUIZ", "DECISION", {
                "decision": "open_answer_needs_manual_grading",
                "quiz_id": quiz.id,
            })
            QuizAnswer.objects.create(
                attempt=attempt,
                text=serializer.validated_data.get('text', ''),
                is_correct=None
            )
            log_line("quizzes", "INFO", "submit", "SUBMIT_QUIZ", "STATE_CHANGE", {
                "action": "answer_created",
                "attempt_id": attempt.id,
                "answer_type": "open",
                "is_correct": None,
            })
        else:
            option_ids = serializer.validated_data.get('option_ids', [])
            correct_options = quiz.options.filter(is_correct=True)
            selected_options = quiz.options.filter(id__in=option_ids)
            
            correct_count = selected_options.filter(is_correct=True).count()
            total_correct = correct_options.count()
            
            log_line("quizzes", "DEBUG", "submit", "SUBMIT_QUIZ", "CHECK", {
                "check": "answer_evaluation",
                "selected_count": selected_options.count(),
                "correct_count": correct_count,
                "total_correct": total_correct,
            })
            
            if quiz.question_type == Quiz.QuestionType.SINGLE:
                log_line("quizzes", "DEBUG", "submit", "SUBMIT_QUIZ", "DECISION", {
                    "decision": "single_choice_scoring",
                    "correct_count": correct_count,
                    "selected_count": selected_options.count(),
                })
                if correct_count == 1 and selected_options.count() == 1:
                    score = Decimal('100.00')
                    log_line("quizzes", "INFO", "submit", "SUBMIT_QUIZ", "STATE_CHANGE", {
                        "action": "score_calculated",
                        "score": "100.00",
                        "reason": "single_correct",
                    })
                else:
                    log_line("quizzes", "INFO", "submit", "SUBMIT_QUIZ", "STATE_CHANGE", {
                        "action": "score_calculated",
                        "score": "0.00",
                        "reason": "single_incorrect",
                    })
            else:
                log_line("quizzes", "DEBUG", "submit", "SUBMIT_QUIZ", "DECISION", {
                    "decision": "multiple_choice_scoring",
                    "correct_count": correct_count,
                    "total_correct": total_correct,
                })
                if total_correct > 0:
                    score = Decimal(str((correct_count / total_correct) * 100))
                    log_line("quizzes", "INFO", "submit", "SUBMIT_QUIZ", "STATE_CHANGE", {
                        "action": "score_calculated",
                        "score": str(score),
                        "formula": f"{correct_count}/{total_correct}*100",
                    })
            
            for option in selected_options:
                QuizAnswer.objects.create(
                    attempt=attempt,
                    quiz_option=option,
                    is_correct=option.is_correct
                )
            
            log_line("quizzes", "INFO", "submit", "SUBMIT_QUIZ", "STATE_CHANGE", {
                "action": "answers_created",
                "attempt_id": attempt.id,
                "answers_count": selected_options.count(),
            })
        
        attempt.score = score
        attempt.save(update_fields=['score'])
        
        log_line("quizzes", "INFO", "submit", "SUBMIT_QUIZ", "STATE_CHANGE", {
            "entity": "quiz_attempt",
            "id": attempt.id,
            "field": "score",
            "value": str(score),
        })
        
        response_data = {
            'attempt': QuizAttemptSerializer(attempt).data,
            'score': score,
            'is_correct': score == 100
        }
        
        log_line("quizzes", "INFO", "submit", "SUBMIT_QUIZ", "EXIT", {
            "result": "success",
            "attempt_id": attempt.id,
            "score": str(score),
            "is_correct": score == 100,
        })
        return Response(response_data)
    # [END_SUBMIT_QUIZ]
    
    # [START_GET_ATTEMPTS]
    """
    ANCHOR: GET_ATTEMPTS
    PURPOSE: Получение попыток пользователя для конкретного теста.

    @PreConditions:
    - тест существует
    - request.user аутентифицирован

    @PostConditions:
    - возвращает список попыток пользователя для теста

    @Invariants:
    - пользователь видит только свои попытки

    @SideEffects:
    - SELECT запрос к БД

    @ForbiddenChanges:
    - фильтрация по request.user
    """
    @action(detail=True, methods=['get'])
    def attempts(self, request, pk=None):
        log_line("quizzes", "DEBUG", "attempts", "GET_ATTEMPTS", "ENTRY", {
            "user_id": request.user.id,
            "quiz_id": pk,
        })
        
        quiz = self.get_object()
        attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz)
        serializer = QuizAttemptSerializer(attempts, many=True)
        
        log_line("quizzes", "DEBUG", "attempts", "GET_ATTEMPTS", "EXIT", {
            "result": "success",
            "attempts_count": attempts.count(),
            "quiz_id": quiz.id,
        })
        return Response(serializer.data)
    # [END_GET_ATTEMPTS]


# [END_QUIZ_VIEWSET]


# [START_QUIZ_ATTEMPT_VIEWSET]
"""
ANCHOR: QUIZ_ATTEMPT_VIEWSET
PURPOSE: ViewSet для просмотра попыток прохождения тестов.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет read-only операции для попыток

@Invariants:
- пользователь видит только свои попытки

@SideEffects:
- нет побочных эффектов (read-only)

@ForbiddenChanges:
- permission_classes = [IsAuthenticated]
- ReadOnlyModelViewSet
"""
class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for QuizAttempt model."""
    
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_QUERYSET_ATTEMPT]
    """
    ANCHOR: GET_QUERYSET_ATTEMPT
    PURPOSE: Фильтрация попыток по пользователю и тесту.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - возвращает только попытки текущего пользователя
    - при наличии quiz_id фильтрует по тесту

    @Invariants:
    - всегда возвращает QuerySet только для request.user

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - фильтрация по request.user (пользователь видит только свои попытки)
    """
    def get_queryset(self):
        log_line("quizzes", "DEBUG", "get_queryset", "GET_QUERYSET_ATTEMPT", "ENTRY", {
            "user_id": self.request.user.id,
        })
        
        queryset = QuizAttempt.objects.select_related('quiz').filter(user=self.request.user)
        quiz_id = self.request.query_params.get('quiz_id')
        
        log_line("quizzes", "DEBUG", "get_queryset", "GET_QUERYSET_ATTEMPT", "BRANCH", {
            "branch": "quiz_filter",
            "quiz_id": quiz_id,
        })
        
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
            log_line("quizzes", "DEBUG", "get_queryset", "GET_QUERYSET_ATTEMPT", "STATE_CHANGE", {
                "action": "filter_by_quiz",
                "quiz_id": quiz_id,
            })
        
        log_line("quizzes", "DEBUG", "get_queryset", "GET_QUERYSET_ATTEMPT", "EXIT", {
            "queryset_count": queryset.count(),
        })
        return queryset
    # [END_GET_QUERYSET_ATTEMPT]


# [END_QUIZ_ATTEMPT_VIEWSET]


# === END_CHUNK: QUIZ_VIEWS_V1 ===
