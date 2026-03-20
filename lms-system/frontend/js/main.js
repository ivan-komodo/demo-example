/**
 * LMS System - Main Module
 * Главный модуль приложения
 */

/**
 * Утилиты
 */
const Utils = {
    /**
     * Форматирование даты
     * @param {string|Date} date 
     * @returns {string}
     */
    formatDate(date) {
        const d = new Date(date);
        return d.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    },

    /**
     * Форматирование даты и времени
     * @param {string|Date} date 
     * @returns {string}
     */
    formatDateTime(date) {
        const d = new Date(date);
        return d.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    },

    /**
     * Показать уведомление
     * @param {string} message 
     * @param {string} type - success, error, warning, info
     */
    showNotification(message, type = 'info') {
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

        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    },

    /**
     * Показать индикатор загрузки
     * @param {HTMLElement} element 
     */
    showLoading(element) {
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
            </div>
        `;
    },

    /**
     * Обработать ошибку API
     * @param {Error} error 
     */
    handleError(error) {
        console.error('Error:', error);
        
        if (error instanceof APIError) {
            const message = error.data?.detail || 
                           error.data?.message || 
                           'Произошла ошибка';
            Utils.showNotification(message, 'error');
        } else {
            Utils.showNotification('Произошла ошибка при выполнении запроса', 'error');
        }
    },

    /**
     * Получить параметр из URL
     * @param {string} name 
     * @returns {string|null}
     */
    getUrlParam(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    },

    /**
     * Дебаунс функция
     * @param {Function} func 
     * @param {number} wait 
     * @returns {Function}
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
};

/**
 * Компонент карточки курса
 * @param {Object} course 
 * @returns {string}
 */
function createCourseCard(course) {
    const statusBadge = course.status === 'published' 
        ? '<span class="badge badge-success">Опубликовано</span>'
        : course.status === 'draft'
        ? '<span class="badge badge-warning">Черновик</span>'
        : '<span class="badge badge-secondary">Архив</span>';

    return `
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
}

/**
 * Компонент карточки бронирования
 * @param {Object} booking 
 * @returns {string}
 */
function createBookingCard(booking) {
    const statusBadge = booking.status === 'confirmed'
        ? '<span class="badge badge-success">Подтверждено</span>'
        : booking.status === 'pending'
        ? '<span class="badge badge-warning">Ожидание</span>'
        : '<span class="badge badge-error">Отменено</span>';

    return `
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
}

/**
 * Компонент элемента прогресса
 * @param {Object} progress 
 * @returns {string}
 */
function createProgressItem(progress) {
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

    return `
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
}

/**
 * Инициализация страницы
 */
document.addEventListener('DOMContentLoaded', () => {
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

    // Обновляем UI аутентификации
    if (window.auth) {
        auth.updateUI();
    }

    console.log('LMS System initialized');
});

// Export for use in other modules
window.Utils = Utils;