/**
 * LMS System - Main Module
 * Главный модуль приложения
 */

// === CHUNK: MAIN_MODULE_V1 [FRONTEND] ===
// Описание: Главный модуль с утилитами и компонентами UI.
// Dependencies: API_CLIENT_V1, AUTH_MODULE_V1

/**
 * Утилиты
 */
// [START_UTILS_OBJECT]
/**
 * ANCHOR: UTILS_OBJECT
 * PURPOSE: Объект с утилитами общего назначения.
 * 
 * @PreConditions:
 * - нет нетривиальных предусловий
 * 
 * @PostConditions:
 * - предоставляет методы для форматирования, уведомлений, обработки ошибок
 * 
 * @Invariants:
 * - все методы stateless
 * 
 * @SideEffects:
 * - методы модифицируют DOM (showNotification, showLoading)
 * 
 * @ForbiddenChanges:
 * - формат даты ru-RU
 */
const Utils = {
    /**
     * Форматирование даты
     * @param {string|Date} date 
     * @returns {string}
     */
    // [START_FORMAT_DATE]
    /**
     * ANCHOR: FORMAT_DATE
     * PURPOSE: Форматирование даты для отображения.
     * 
     * @PreConditions:
     * - date валидная строка даты или объект Date
     * 
     * @PostConditions:
     * - возвращает строку в формате "день месяц год" (ru-RU)
     * 
     * @Invariants:
     * - всегда использует locale ru-RU
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - locale 'ru-RU'
     */
    formatDate(date) {
        logLine("main", "DEBUG", "formatDate", "FORMAT_DATE", "ENTRY", {});
        
        const d = new Date(date);
        const result = d.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
        
        logLine("main", "DEBUG", "formatDate", "FORMAT_DATE", "EXIT", {
            "result": result
        });
        
        return result;
    },
    // [END_FORMAT_DATE]

    /**
     * Форматирование даты и времени
     * @param {string|Date} date 
     * @returns {string}
     */
    // [START_FORMAT_DATE_TIME]
    /**
     * ANCHOR: FORMAT_DATE_TIME
     * PURPOSE: Форматирование даты и времени для отображения.
     * 
     * @PreConditions:
     * - date валидная строка даты или объект Date
     * 
     * @PostConditions:
     * - возвращает строку в формате "день месяц год час:минута" (ru-RU)
     * 
     * @Invariants:
     * - всегда использует locale ru-RU
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - locale 'ru-RU'
     */
    formatDateTime(date) {
        logLine("main", "DEBUG", "formatDateTime", "FORMAT_DATE_TIME", "ENTRY", {});
        
        const d = new Date(date);
        const result = d.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
        
        logLine("main", "DEBUG", "formatDateTime", "FORMAT_DATE_TIME", "EXIT", {
            "result": result
        });
        
        return result;
    },
    // [END_FORMAT_DATE_TIME]

    /**
     * Показать уведомление
     * @param {string} message 
     * @param {string} type - success, error, warning, info
     */
    // [START_SHOW_NOTIFICATION]
    /**
     * ANCHOR: SHOW_NOTIFICATION
     * PURPOSE: Отображение всплывающего уведомления.
     * 
     * @PreConditions:
     * - message строка сообщения
     * - type строка типа уведомления
     * 
     * @PostConditions:
     * - создаёт и показывает уведомление, скрывает через 5 секунд
     * 
     * @Invariants:
     * - контейнер уведомлений всегда в z-index:1000, top-right
     * - авто-скрытие через 5 секунд
     * 
     * @SideEffects:
     * - добавление элементов в DOM
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - позиция контейнера (fixed, top-right)
     * - таймаут 5 секунд
     */
    showNotification(message, type = 'info') {
        logLine("main", "DEBUG", "showNotification", "SHOW_NOTIFICATION", "ENTRY", {
            "message": message.substring(0, 50),
            "type": type
        });
        
        // Создаем контейнер для уведомлений, если его нет
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            `;
            document.body.appendChild(container);
            logLine("main", "DEBUG", "showNotification", "SHOW_NOTIFICATION", "BRANCH", {
                "branch": "container_created"
            });
        }

        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            padding: 1rem 1.5rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            background-color: ${
                type === 'success' ? '#dcfce7' :
                type === 'error' ? '#fee2e2' :
                type === 'warning' ? '#fef3c7' : '#e0f2fe'
            };
            color: ${
                type === 'success' ? '#166534' :
                type === 'error' ? '#991b1b' :
                type === 'warning' ? '#92400e' : '#075985'
            };
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            animation: slideIn 0.3s ease;
            max-width: 400px;
        `;
        
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" style="
                background: none;
                border: none;
                cursor: pointer;
                font-size: 1.2rem;
                padding: 0;
                margin-left: auto;
            ">×</button>
        `;

        container.appendChild(notification);
        
        logLine("main", "INFO", "showNotification", "SHOW_NOTIFICATION", "STATE_CHANGE", {
            "action": "notification_shown",
            "type": type
        });
        logLine("main", "DEBUG", "showNotification", "SHOW_NOTIFICATION", "EXIT", {
            "result": "shown"
        });

        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    },
    // [END_SHOW_NOTIFICATION]

    /**
     * Показать индикатор загрузки
     * @param {HTMLElement} element 
     */
    // [START_SHOW_LOADING]
    /**
     * ANCHOR: SHOW_LOADING
     * PURPOSE: Отображение индикатора загрузки.
     * 
     * @PreConditions:
     * - element DOM элемент
     * 
     * @PostConditions:
     * - заменяет содержимое элемента спиннером загрузки
     * 
     * @Invariants:
     * - всегда показывает одинаковую структуру спиннера
     * 
     * @SideEffects:
     * - изменение innerHTML элемента
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - HTML структура спиннера
     */
    showLoading(element) {
        logLine("main", "DEBUG", "showLoading", "SHOW_LOADING", "ENTRY", {});
        
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
            </div>
        `;
        
        logLine("main", "DEBUG", "showLoading", "SHOW_LOADING", "EXIT", {
            "result": "shown"
        });
    },
    // [END_SHOW_LOADING]

    /**
     * Обработать ошибку API
     * @param {Error} error 
     */
    // [START_HANDLE_ERROR]
    /**
     * ANCHOR: HANDLE_ERROR
     * PURPOSE: Централизованная обработка ошибок API.
     * 
     * @PreConditions:
     * - error объект ошибки
     * 
     * @PostConditions:
     * - логирует ошибку и показывает уведомление
     * 
     * @Invariants:
     * - всегда показывает уведомление
     * 
     * @SideEffects:
     * - console.error
     * - showNotification
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - извлечение detail/message из ошибки
     */
    handleError(error) {
        logLine("main", "DEBUG", "handleError", "HANDLE_ERROR", "ENTRY", {
            "error_type": error.constructor.name
        });
        
        console.error('Error:', error);
        
        if (error instanceof APIError) {
            const message = error.data?.detail || 
                           error.data?.message || 
                           'Произошла ошибка';
            
            logLine("main", "ERROR", "handleError", "HANDLE_ERROR", "ERROR", {
                "reason": "api_error",
                "status": error.status,
                "message": message
            });
            
            Utils.showNotification(message, 'error');
        } else {
            logLine("main", "ERROR", "handleError", "HANDLE_ERROR", "ERROR", {
                "reason": "unknown_error",
                "message": error.message
            });
            
            Utils.showNotification('Произошла ошибка при выполнении запроса', 'error');
        }
        
        logLine("main", "DEBUG", "handleError", "HANDLE_ERROR", "EXIT", {
            "result": "handled"
        });
    },
    // [END_HANDLE_ERROR]

    /**
     * Получить параметр из URL
     * @param {string} name 
     * @returns {string|null}
     */
    // [START_GET_URL_PARAM]
    /**
     * ANCHOR: GET_URL_PARAM
     * PURPOSE: Получение query-параметра из URL.
     * 
     * @PreConditions:
     * - name строка имени параметра
     * 
     * @PostConditions:
     * - возвращает значение параметра или null
     * 
     * @Invariants:
     * - использует URLSearchParams
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - чтение из window.location.search
     */
    getUrlParam(name) {
        logLine("main", "DEBUG", "getUrlParam", "GET_URL_PARAM", "ENTRY", {
            "param": name
        });
        
        const params = new URLSearchParams(window.location.search);
        const result = params.get(name);
        
        logLine("main", "DEBUG", "getUrlParam", "GET_URL_PARAM", "EXIT", {
            "result": result
        });
        
        return result;
    },
    // [END_GET_URL_PARAM]

    /**
     * Дебаунс функция
     * @param {Function} func 
     * @param {number} wait 
     * @returns {Function}
     */
    // [START_DEBOUNCE]
    /**
     * ANCHOR: DEBOUNCE
     * PURPOSE: Создание функции с задержкой выполнения.
     * 
     * @PreConditions:
     * - func функция для debounce
     * - wait время задержки в мс
     * 
     * @PostConditions:
     * - возвращает функцию с debounce
     * 
     * @Invariants:
     * - только последний вызов выполняется
     * 
     * @SideEffects:
     * - нет побочных эффектов при создании
     * 
     * @ForbiddenChanges:
     * - стандартный паттерн debounce
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    // [END_DEBOUNCE]
};
// [END_UTILS_OBJECT]

/**
 * Компонент карточки курса
 * @param {Object} course 
 * @returns {string}
 */
// [START_CREATE_COURSE_CARD]
/**
 * ANCHOR: CREATE_COURSE_CARD
 * PURPOSE: Создание HTML карточки курса для списка.
 * 
 * @PreConditions:
 * - course объект с id, title, description, status, modules_count
 * 
 * @PostConditions:
 * - возвращает HTML строку карточки курса
 * 
 * @Invariants:
 * - всегда возвращает валидный HTML
 * 
 * @SideEffects:
 * - нет побочных эффектов (чистая функция)
 * 
 * @ForbiddenChanges:
 * - структура карточки курса
 */
function createCourseCard(course) {
    logLine("main", "DEBUG", "createCourseCard", "CREATE_COURSE_CARD", "ENTRY", {
        "course_id": course.id
    });
    
    const statusBadge = course.status === 'published' 
        ? '<span class="badge badge-success">Опубликовано</span>'
        : course.status === 'draft'
        ? '<span class="badge badge-warning">Черновик</span>'
        : '<span class="badge badge-secondary">Архив</span>';

    const result = `
        <div class="card course-card" data-course-id="${course.id}">
            <div class="card-header">
                <h3 class="card-title">${course.title}</h3>
                ${statusBadge}
            </div>
            <p class="card-text">${course.description || 'Описание отсутствует'}</p>
            <div class="card-footer">
                <small>Модулей: ${course.modules_count || 0}</small>
                <a href="/course.html?id=${course.id}" class="btn btn-primary">Подробнее</a>
            </div>
        </div>
    `;
    
    logLine("main", "DEBUG", "createCourseCard", "CREATE_COURSE_CARD", "EXIT", {
        "result": "html_created"
    });
    
    return result;
}
// [END_CREATE_COURSE_CARD]

/**
 * Компонент карточки бронирования
 * @param {Object} booking 
 * @returns {string}
 */
// [START_CREATE_BOOKING_CARD]
/**
 * ANCHOR: CREATE_BOOKING_CARD
 * PURPOSE: Создание HTML карточки бронирования для списка.
 * 
 * @PreConditions:
 * - booking объект с id, title, resource_name, start_time, end_time, status
 * 
 * @PostConditions:
 * - возвращает HTML строку карточки бронирования
 * 
 * @Invariants:
 * - всегда возвращает валидный HTML
 * 
 * @SideEffects:
 * - нет побочных эффектов (чистая функция)
 * 
 * @ForbiddenChanges:
 * - структура карточки бронирования
 */
function createBookingCard(booking) {
    logLine("main", "DEBUG", "createBookingCard", "CREATE_BOOKING_CARD", "ENTRY", {
        "booking_id": booking.id
    });
    
    const statusBadge = booking.status === 'confirmed'
        ? '<span class="badge badge-success">Подтверждено</span>'
        : booking.status === 'pending'
        ? '<span class="badge badge-warning">Ожидание</span>'
        : '<span class="badge badge-error">Отменено</span>';

    const result = `
        <div class="card booking-card" data-booking-id="${booking.id}">
            <div class="card-header">
                <h3 class="card-title">${booking.title}</h3>
                ${statusBadge}
            </div>
            <p class="card-text">
                <strong>Ресурс:</strong> ${booking.resource_name}<br>
                <strong>Начало:</strong> ${Utils.formatDateTime(booking.start_time)}<br>
                <strong>Окончание:</strong> ${Utils.formatDateTime(booking.end_time)}
            </p>
            <div class="card-footer">
                <a href="/booking.html?id=${booking.id}" class="btn btn-outline">Детали</a>
            </div>
        </div>
    `;
    
    logLine("main", "DEBUG", "createBookingCard", "CREATE_BOOKING_CARD", "EXIT", {
        "result": "html_created"
    });
    
    return result;
}
// [END_CREATE_BOOKING_CARD]

/**
 * Компонент элемента прогресса
 * @param {Object} progress 
 * @returns {string}
 */
// [START_CREATE_PROGRESS_ITEM]
/**
 * ANCHOR: CREATE_PROGRESS_ITEM
 * PURPOSE: Создание HTML элемента прогресса для списка.
 * 
 * @PreConditions:
 * - progress объект с id, module_title, course_title, status, score, completed_at
 * 
 * @PostConditions:
 * - возвращает HTML строку элемента прогресса
 * 
 * @Invariants:
 * - всегда возвращает валидный HTML
 * - progress bar показывается только для in_progress/completed
 * 
 * @SideEffects:
 * - нет побочных эффектов (чистая функция)
 * 
 * @ForbiddenChanges:
 * - структура элемента прогресса
 */
function createProgressItem(progress) {
    logLine("main", "DEBUG", "createProgressItem", "CREATE_PROGRESS_ITEM", "ENTRY", {
        "progress_id": progress.id
    });
    
    const statusBadge = progress.status === 'completed'
        ? '<span class="badge badge-success">Завершен</span>'
        : progress.status === 'in_progress'
        ? '<span class="badge badge-warning">В процессе</span>'
        : '<span class="badge badge-secondary">Не начат</span>';

    const progressBar = progress.status !== 'not_started' 
        ? `<div class="progress-bar">
            <div class="progress-fill" style="width: ${progress.score || 0}%"></div>
           </div>`
        : '';

    const result = `
        <div class="card progress-item" data-progress-id="${progress.id}">
            <div class="card-header">
                <h3 class="card-title">${progress.module_title}</h3>
                ${statusBadge}
            </div>
            <p class="card-text">
                <strong>Курс:</strong> ${progress.course_title}<br>
                ${progress.completed_at ? `<strong>Завершен:</strong> ${Utils.formatDate(progress.completed_at)}` : ''}
            </p>
            ${progressBar}
        </div>
    `;
    
    logLine("main", "DEBUG", "createProgressItem", "CREATE_PROGRESS_ITEM", "EXIT", {
        "result": "html_created"
    });
    
    return result;
}
// [END_CREATE_PROGRESS_ITEM]

/**
 * Инициализация страницы
 */
// [START_DOM_CONTENT_LOADED]
/**
 * ANCHOR: DOM_CONTENT_LOADED
 * PURPOSE: Инициализация приложения при загрузке страницы.
 * 
 * @PreConditions:
 * - DOM загружен
 * 
 * @PostConditions:
 * - добавляет стили анимаций, обновляет UI аутентификации
 * 
 * @Invariants:
 * - всегда добавляет стили для анимаций
 * - всегда вызывает auth.updateUI если auth доступен
 * 
 * @SideEffects:
 * - добавление стилей в head
 * - вызов auth.updateUI()
 * - console.log
 * - логирование операции
 * 
 * @ForbiddenChanges:
 * - стили анимаций и компонентов
 */
document.addEventListener('DOMContentLoaded', () => {
    logLine("main", "DEBUG", "DOMContentLoaded", "DOM_CONTENT_LOADED", "ENTRY", {});
    
    // Добавляем стили для анимаций
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        @keyframes slideOut {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
        .progress-bar {
            height: 8px;
            background-color: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 1rem;
        }
        .progress-fill {
            height: 100%;
            background-color: #3b82f6;
            transition: width 0.3s ease;
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .badge-success { background-color: #dcfce7; color: #166534; }
        .badge-warning { background-color: #fef3c7; color: #92400e; }
        .badge-error { background-color: #fee2e2; color: #991b1b; }
        .badge-secondary { background-color: #f1f5f9; color: #475569; }
        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }
    `;
    document.head.appendChild(style);
    
    logLine("main", "DEBUG", "DOMContentLoaded", "DOM_CONTENT_LOADED", "STATE_CHANGE", {
        "action": "styles_added"
    });

    // Обновляем UI аутентификации
    if (window.auth) {
        auth.updateUI();
        logLine("main", "DEBUG", "DOMContentLoaded", "DOM_CONTENT_LOADED", "BRANCH", {
            "branch": "auth_ui_updated"
        });
    }

    console.log('LMS System initialized');
    
    logLine("main", "INFO", "DOMContentLoaded", "DOM_CONTENT_LOADED", "STATE_CHANGE", {
        "action": "app_initialized"
    });
    logLine("main", "DEBUG", "DOMContentLoaded", "DOM_CONTENT_LOADED", "EXIT", {
        "result": "success"
    });
});
// [END_DOM_CONTENT_LOADED]

// === END_CHUNK: MAIN_MODULE_V1 ===

// Export for use in other modules
window.Utils = Utils;