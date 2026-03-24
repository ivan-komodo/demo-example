/**
 * LMS System - API Client
 * Базовый клиент для работы с API
 */

const API_BASE_URL = '/api/v1';

// === CHUNK: API_CLIENT_V1 [FRONTEND] ===
// Описание: API клиент для взаимодействия с backend.
// Dependencies: none

/**
 * API Client class
 */
// [START_API_CLIENT_CLASS]
// ANCHOR: API_CLIENT_CLASS
// @PreConditions:
// - baseUrl валидный URL строки API
// @PostConditions:
// - создаёт экземпляр клиента с методами для HTTP запросов
// PURPOSE: Класс для управления HTTP запросами к API с авторизацией.
class APIClient {
    // [START_API_CLIENT_CONSTRUCTOR]
    // ANCHOR: API_CLIENT_CONSTRUCTOR
    // @PreConditions:
    // - baseUrl строка базового URL API
    // @PostConditions:
    // - инициализирует клиент с baseUrl и пустым accessToken
    // PURPOSE: Инициализация API клиента.
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.accessToken = null;
    }
    // [END_API_CLIENT_CONSTRUCTOR]

    /**
     * Установить access token
     * @param {string} token 
     */
    // [START_SET_ACCESS_TOKEN]
    // ANCHOR: SET_ACCESS_TOKEN
    // @PreConditions:
    // - token валидная строка JWT токена
    // @PostConditions:
    // - сохраняет токен в памяти и localStorage
    // PURPOSE: Сохранение access токена.
    setAccessToken(token) {
        this.accessToken = token;
        localStorage.setItem('access_token', token);
    }
    // [END_SET_ACCESS_TOKEN]

    /**
     * Получить access token
     * @returns {string|null}
     */
    // [START_GET_ACCESS_TOKEN]
    // ANCHOR: GET_ACCESS_TOKEN
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - возвращает токен из памяти или localStorage
    // PURPOSE: Получение access токена.
    getAccessToken() {
        if (!this.accessToken) {
            this.accessToken = localStorage.getItem('access_token');
        }
        return this.accessToken;
    }
    // [END_GET_ACCESS_TOKEN]

    /**
     * Установить refresh token
     * @param {string} token 
     */
    // [START_SET_REFRESH_TOKEN]
    // ANCHOR: SET_REFRESH_TOKEN
    // @PreConditions:
    // - token валидная строка JWT токена
    // @PostConditions:
    // - сохраняет токен в localStorage
    // PURPOSE: Сохранение refresh токена.
    setRefreshToken(token) {
        localStorage.setItem('refresh_token', token);
    }
    // [END_SET_REFRESH_TOKEN]

    /**
     * Получить refresh token
     * @returns {string|null}
     */
    // [START_GET_REFRESH_TOKEN]
    // ANCHOR: GET_REFRESH_TOKEN
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - возвращает токен из localStorage или null
    // PURPOSE: Получение refresh токена.
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }
    // [END_GET_REFRESH_TOKEN]

    /**
     * Очистить токены
     */
    // [START_CLEAR_TOKENS]
    // ANCHOR: CLEAR_TOKENS
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - удаляет все токены из памяти и localStorage
    // PURPOSE: Очистка данных аутентификации.
    clearTokens() {
        this.accessToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }
    // [END_CLEAR_TOKENS]

    /**
     * Получить заголовки для запроса
     * @param {boolean} withAuth - добавлять ли авторизацию
     * @returns {Object}
     */
    // [START_GET_HEADERS]
    // ANCHOR: GET_HEADERS
    // @PreConditions:
    // - withAuth булево значение
    // @PostConditions:
    // - возвращает объект заголовков с Content-Type и опционально Authorization
    // PURPOSE: Формирование заголовков HTTP запроса.
    getHeaders(withAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (withAuth && this.getAccessToken()) {
            headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
        }

        return headers;
    }
    // [END_GET_HEADERS]

    /**
     * Обновить access token
     * @returns {Promise<boolean>}
     */
    // [START_REFRESH_ACCESS_TOKEN]
    // ANCHOR: REFRESH_ACCESS_TOKEN
    // @PreConditions:
    // - refresh токен существует в localStorage
    // @PostConditions:
    // - при успехе обновляет access токен и возвращает true
    // - при неудаче очищает токены и возвращает false
    // PURPOSE: Обновление access токена через refresh токен.
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            return false;
        }

        try {
            const response = await fetch(`${this.baseUrl}/auth/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                this.setAccessToken(data.access);
                return true;
            } else {
                this.clearTokens();
                return false;
            }
        } catch (error) {
            console.error('Error refreshing token:', error);
            this.clearTokens();
            return false;
        }
    }
    // [END_REFRESH_ACCESS_TOKEN]

    /**
     * Выполнить запрос
     * @param {string} endpoint - эндпоинт API
     * @param {Object} options - опции запроса
     * @returns {Promise<Object>}
     */
    // [START_REQUEST]
    // ANCHOR: REQUEST
    // @PreConditions:
    // - endpoint строка пути API
    // - options объект с method, body, withAuth, retry
    // @PostConditions:
    // - возвращает JSON ответ или выбрасывает APIError
    // - при 401 пытается обновить токен и повторить запрос
    // PURPOSE: Выполнение HTTP запроса с обработкой авторизации.
    async request(endpoint, options = {}) {
        const {
            method = 'GET',
            body = null,
            withAuth = true,
            retry = true,
        } = options;

        const url = `${this.baseUrl}${endpoint}`;
        const headers = this.getHeaders(withAuth);

        const fetchOptions = {
            method,
            headers,
        };

        if (body && method !== 'GET') {
            fetchOptions.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(url, fetchOptions);

            // Если токен истек, пробуем обновить
            if (response.status === 401 && retry && withAuth) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Повторяем запрос с новым токеном
                    return this.request(endpoint, { ...options, retry: false });
                } else {
                    // Перенаправляем на страницу входа
                    window.location.href = '/login.html';
                    throw new Error('Unauthorized');
                }
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(response.status, errorData);
            }

            // Для ответов без контента (204 No Content)
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            console.error('API request error:', error);
            throw new APIError(0, { detail: 'Ошибка соединения с сервером' });
        }
    }
    // [END_REQUEST]

    // HTTP методы

    /**
     * GET запрос
     * @param {string} endpoint 
     * @param {Object} params - query параметры
     * @returns {Promise<Object>}
     */
    // [START_GET]
    // ANCHOR: GET
    // @PreConditions:
    // - endpoint строка пути API
    // - params объект query параметров
    // @PostConditions:
    // - возвращает результат GET запроса
    // PURPOSE: Выполнение GET запроса.
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }
    // [END_GET]

    /**
     * POST запрос
     * @param {string} endpoint 
     * @param {Object} body 
     * @returns {Promise<Object>}
     */
    // [START_POST]
    // ANCHOR: POST
    // @PreConditions:
    // - endpoint строка пути API
    // - body объект данных для отправки
    // @PostConditions:
    // - возвращает результат POST запроса
    // PURPOSE: Выполнение POST запроса.
    async post(endpoint, body = {}) {
        return this.request(endpoint, { method: 'POST', body });
    }
    // [END_POST]

    /**
     * PUT запрос
     * @param {string} endpoint 
     * @param {Object} body 
     * @returns {Promise<Object>}
     */
    // [START_PUT]
    // ANCHOR: PUT
    // @PreConditions:
    // - endpoint строка пути API
    // - body объект данных для отправки
    // @PostConditions:
    // - возвращает результат PUT запроса
    // PURPOSE: Выполнение PUT запроса.
    async put(endpoint, body = {}) {
        return this.request(endpoint, { method: 'PUT', body });
    }
    // [END_PUT]

    /**
     * PATCH запрос
     * @param {string} endpoint 
     * @param {Object} body 
     * @returns {Promise<Object>}
     */
    // [START_PATCH]
    // ANCHOR: PATCH
    // @PreConditions:
    // - endpoint строка пути API
    // - body объект данных для отправки
    // @PostConditions:
    // - возвращает результат PATCH запроса
    // PURPOSE: Выполнение PATCH запроса.
    async patch(endpoint, body = {}) {
        return this.request(endpoint, { method: 'PATCH', body });
    }
    // [END_PATCH]

    /**
     * DELETE запрос
     * @param {string} endpoint 
     * @returns {Promise<Object>}
     */
    // [START_DELETE]
    // ANCHOR: DELETE
    // @PreConditions:
    // - endpoint строка пути API
    // @PostConditions:
    // - возвращает результат DELETE запроса
    // PURPOSE: Выполнение DELETE запроса.
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
    // [END_DELETE]
}
// [END_API_CLIENT_CLASS]


/**
 * Custom API Error class
 */
// [START_API_ERROR_CLASS]
// ANCHOR: API_ERROR_CLASS
// @PreConditions:
// - status HTTP статус код
// - data объект с деталями ошибки
// @PostConditions:
// - создаёт Error с дополнительными полями status и data
// PURPOSE: Класс ошибки для API запросов.
class APIError extends Error {
    // [START_API_ERROR_CONSTRUCTOR]
    // ANCHOR: API_ERROR_CONSTRUCTOR
    // @PreConditions:
    // - status числовой HTTP статус
    // - data объект с деталями ошибки
    // @PostConditions:
    // - создаёт экземпляр ошибки с name, status, data
    // PURPOSE: Инициализация ошибки API.
    constructor(status, data) {
        super(data.detail || 'API Error');
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
    // [END_API_ERROR_CONSTRUCTOR]
}
// [END_API_ERROR_CLASS]


// === END_CHUNK: API_CLIENT_V1 ===

// Создаем глобальный экземпляр API клиента
const api = new APIClient(API_BASE_URL);

/**
 * API endpoints
 */
const API = {
    // Auth
    login: (credentials) => api.post('/auth/login/', credentials),
    register: (data) => api.post('/auth/register/', data),
    logout: () => api.post('/auth/logout/'),
    refresh: () => api.post('/auth/refresh/', { refresh: api.getRefreshToken() }),
    me: () => api.get('/auth/me/'),

    // Courses
    courses: {
        list: (params) => api.get('/courses/', params),
        get: (id) => api.get(`/courses/${id}/`),
        create: (data) => api.post('/courses/', data),
        update: (id, data) => api.patch(`/courses/${id}/`, data),
        delete: (id) => api.delete(`/courses/${id}/`),
        enroll: (id) => api.post(`/courses/${id}/enroll/`),
    },

    // Modules
    modules: {
        list: (courseId) => api.get('/modules/', { course: courseId }),
        get: (id) => api.get(`/modules/${id}/`),
        create: (data) => api.post('/modules/', data),
        update: (id, data) => api.patch(`/modules/${id}/`, data),
        delete: (id) => api.delete(`/modules/${id}/`),
    },

    // Quizzes
    quizzes: {
        list: (moduleId) => api.get('/quizzes/', { module: moduleId }),
        get: (id) => api.get(`/quizzes/${id}/`),
        submit: (id, answers) => api.post(`/quizzes/${id}/submit/`, { answers }),
    },

    // Progress
    progress: {
        list: (params) => api.get('/progress/', params),
        get: (id) => api.get(`/progress/${id}/`),
        update: (id, data) => api.patch(`/progress/${id}/`, data),
    },

    // Bookings
    bookings: {
        list: (params) => api.get('/bookings/', params),
        get: (id) => api.get(`/bookings/${id}/`),
        create: (data) => api.post('/bookings/', data),
        update: (id, data) => api.patch(`/bookings/${id}/`, data),
        delete: (id) => api.delete(`/bookings/${id}/`),
    },

    // Resources
    resources: {
        list: (params) => api.get('/resources/', params),
        get: (id) => api.get(`/resources/${id}/`),
    },

    // Notifications
    notifications: {
        list: (params) => api.get('/notifications/', params),
        get: (id) => api.get(`/notifications/${id}/`),
        markRead: (id) => api.patch(`/notifications/${id}/`, { is_read: true }),
        markAllRead: () => api.post('/notifications/mark-all-read/'),
    },
};

// Export for use in other modules
window.api = api;
window.API = API;
window.APIError = APIError;