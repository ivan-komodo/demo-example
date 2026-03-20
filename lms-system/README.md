# LMS System - MVP

Система управления обучением (Learning Management System) - минимально жизнеспособный продукт (MVP) для управления обучением сотрудников.

## 📋 Описание

LMS System - это веб-приложение для управления корпоративным обучением, которое позволяет:

- Управлять курсами и модулями
- Проходить тесты для проверки знаний
- Отслеживать прогресс обучения
- Бронировать обучающие ресурсы (аудитории, тренеры)
- Получать уведомления о важных событиях

## 🏗️ Архитектура

```
[Frontend: HTML + Plain JS] ← HTTPS → [Backend: Django (Python)] ←→ [PostgreSQL]
                                                               ↓
                                                          [Redis] ← кэширование
                                                               ↓
                                                     [File Storage] ← файлы (PDF, видео)
```

## 🛠️ Технологический стек

| Компонент | Технология |
|-----------|------------|
| **Backend** | Python 3.11+ / Django 4.2 LTS / Django REST Framework 3.14 |
| **Frontend** | HTML5 / CSS3 / Vanilla JavaScript (ES6+) |
| **Database** | PostgreSQL 15+ |
| **Cache** | Redis 7.x |
| **Auth** | JWT + Refresh Token (djangorestframework-simplejwt) |
| **API Docs** | drf-spectacular (OpenAPI/Swagger) |
| **Containerization** | Docker / Docker Compose |
| **Web Server** | Nginx 1.25 |

## 📁 Структура проекта

```
lms-system/
├── backend/                # Django backend
│   ├── config/            # Конфигурация проекта
│   │   ├── settings/      # Настройки (base, development, production)
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/              # Django приложения
│   │   ├── users/         # Управление пользователями
│   │   ├── courses/       # Курсы и модули
│   │   ├── quizzes/       # Тесты и попытки
│   │   ├── progress/      # Прогресс пользователей
│   │   ├── bookings/      # Бронирование ресурсов
│   │   └── notifications/ # Уведомления
│   ├── core/              # Общая логика
│   ├── static/            # Статические файлы
│   ├── media/             # Загруженные файлы
│   └── tests/             # Тесты
├── frontend/              # Frontend (HTML, CSS, JS)
│   ├── index.html
│   ├── css/
│   └── js/
├── docker/                # Docker конфигурация
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx/
└── docs/                  # Документация
```

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (для контейнеризированного запуска)

### Установка для разработки

1. **Клонирование репозитория:**
   ```bash
   git clone <repository-url>
   cd lms-system
   ```

2. **Создание виртуального окружения:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Установка зависимостей:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Настройка переменных окружения:**
   ```bash
   cp backend/.env.example backend/.env
   # Отредактируйте .env файл с вашими настройками
   ```

5. **Миграции базы данных:**
   ```bash
   cd backend
   python manage.py migrate
   ```

6. **Создание суперпользователя:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Запуск сервера:**
   ```bash
   python manage.py runserver
   ```

8. **Открытие в браузере:**
   - Frontend: http://localhost:8000/
   - API: http://localhost:8000/api/v1/
   - Admin: http://localhost:8000/admin/
   - Swagger: http://localhost:8000/api/docs/

### Запуск через Docker

1. **Сборка и запуск контейнеров:**
   ```bash
   make docker-build
   make docker-up
   ```

2. **Применение миграций:**
   ```bash
   make docker-migrate
   ```

3. **Остановка контейнеров:**
   ```bash
   make docker-down
   ```

## 📚 API Endpoints

### Аутентификация
- `POST /api/v1/auth/login/` - Вход в систему
- `POST /api/v1/auth/register/` - Регистрация
- `POST /api/v1/auth/refresh/` - Обновление токена
- `POST /api/v1/auth/logout/` - Выход из системы
- `GET /api/v1/auth/me/` - Информация о текущем пользователе

### Курсы
- `GET /api/v1/courses/` - Список курсов
- `POST /api/v1/courses/` - Создание курса
- `GET /api/v1/courses/{id}/` - Детали курса
- `PATCH /api/v1/courses/{id}/` - Обновление курса
- `DELETE /api/v1/courses/{id}/` - Удаление курса
- `POST /api/v1/courses/{id}/enroll/` - Запись на курс

### Модули
- `GET /api/v1/modules/` - Список модулей
- `POST /api/v1/modules/` - Создание модуля
- `GET /api/v1/modules/{id}/` - Детали модуля
- `PATCH /api/v1/modules/{id}/` - Обновление модуля
- `DELETE /api/v1/modules/{id}/` - Удаление модуля

### Тесты
- `GET /api/v1/quizzes/` - Список тестов
- `GET /api/v1/quizzes/{id}/` - Детали теста
- `POST /api/v1/quizzes/{id}/submit/` - Отправка ответов

### Прогресс
- `GET /api/v1/progress/` - Список прогресса
- `GET /api/v1/progress/{id}/` - Детали прогресса
- `PATCH /api/v1/progress/{id}/` - Обновление прогресса

### Бронирование
- `GET /api/v1/bookings/` - Список бронирований
- `POST /api/v1/bookings/` - Создание бронирования
- `GET /api/v1/bookings/{id}/` - Детали бронирования
- `PATCH /api/v1/bookings/{id}/` - Обновление бронирования
- `DELETE /api/v1/bookings/{id}/` - Отмена бронирования

### Уведомления
- `GET /api/v1/notifications/` - Список уведомлений
- `PATCH /api/v1/notifications/{id}/` - Пометить как прочитанное
- `POST /api/v1/notifications/mark-all-read/` - Пометить все как прочитанные

## 👥 Роли пользователей

| Роль | Описание | Права |
|------|----------|-------|
| **admin** | Администратор | Полный доступ ко всем функциям |
| **trainer** | Тренер | Создание и управление курсами, тестами |
| **learner** | Обучающийся | Просмотр курсов, прохождение тестов, бронирование |

## 🧪 Тестирование

```bash
# Запуск всех тестов
make test

# Запуск с покрытием
make test-cov

# Запуск линтеров
make lint
```

## 📝 Команды Makefile

```bash
make help                 # Показать список команд
make install              # Установить зависимости
make dev                  # Запустить dev-сервер
make test                 # Запустить тесты
make migrate              # Применить миграции
make makemigrations       # Создать миграции
make createsuperuser      # Создать суперпользователя
make collectstatic        # Собрать статику
make clean                # Удалить кэш и временные файлы
make docker-build         # Собрать Docker образы
make docker-up            # Запустить контейнеры
make docker-down          # Остановить контейнеры
make docker-logs          # Показать логи контейнеров
```

## 📖 Документация

- [Техническое задание](../plans/ТЗ_v2.md)
- [Project Context](../.kilocode/rules/project-context.md)
- API документация: `/api/docs/` (Swagger UI)
- API схема: `/api/schema/` (OpenAPI JSON)

## 🔐 Безопасность

- Хеширование паролей с bcrypt
- JWT аутентификация с refresh token
- CORS защита
- CSRF защита
- Rate limiting (100 запросов/минута)
- Валидация входных данных

## 📊 Мониторинг и логирование

- Структурированное логирование (JSON)
- Интеграция с Sentry (для production)
- Логирование входов и бизнес-событий

## 🔄 CI/CD

Проект настроен для автоматического тестирования и деплоя:
- Линтеры (flake8, black)
- Unit и интеграционные тесты
- Сборка Docker образов

## 📄 Лицензия

MIT License

## 👨‍💻 Авторы

Разработано в рамках MVP-проекта.

---

*Документация обновлена: Март 2026*