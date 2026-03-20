/**
 * LMS System - API Client
 * Базовый клиент для работы с API
 */

const API_BASE_URL = '/api/v1';

/**
 * API Client class
 */
class APIClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.accessToken = null;
    }

    /**
     * Установить access token
     * @param {string} token 
     */
    setAccessToken(token) {
        this.accessToken = token;
        localStorage.setItem('access_token', token);
    }

    /**
     * Получить access token
     * @returns {string|null}
     */
    getAccessToken() {
        if (!this.accessToken) {
            this.accessToken = localStorage.getItem('access_token');
        }
        return this.accessToken;
    }

    /**
     * Установить refresh token
     * @param {string} token 
     */
    setRefreshToken(token) {
        localStorage.setItem('refresh_token', token);
    }

    /**
     * Получить refresh token
     * @returns {string|null}
     */
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    /**
     * Очистить токены
     */
    clearTokens() {
        this.accessToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    /**
     * Получить заголовки для запроса
     * @param {boolean} withAuth - добавлять ли авторизацию
     * @returns {Object}
     */
    getHeaders(withAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (withAuth && this.getAccessToken()) {
            headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
        }

        return headers;
    }

    /**
     * Обновить access token
     * @returns {Promise<boolean>}
     */
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

    /**
     * Выполнить запрос
     * @param {string} endpoint - эндпоинт API
     * @param {Object} options - опции запроса
     * @returns {Promise<Object>}
     */
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

    // HTTP методы

    /**
     * GET запрос
     * @param {string} endpoint 
     * @param {Object} params - query параметры
     * @returns {Promise<Object>}
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    /**
     * POST запрос
     * @param {string} endpoint 
     * @param {Object} body 
     * @returns {Promise<Object>}
     */
    async post(endpoint, body = {}) {
        return this.request(endpoint, { method: 'POST', body });
    }

    /**
     * PUT запрос
     * @param {string} endpoint 
     * @param {Object} body 
     * @returns {Promise<Object>}
     */
    async put(endpoint, body = {}) {
        return this.request(endpoint, { method: 'PUT', body });
    }

    /**
     * PATCH запрос
     * @param {string} endpoint 
     * @param {Object} body 
     * @returns {Promise<Object>}
     */
    async patch(endpoint, body = {}) {
        return this.request(endpoint, { method: 'PATCH', body });
    }

    /**
     * DELETE запрос
     * @param {string} endpoint 
     * @returns {Promise<Object>}
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(status, data) {
        super(data.detail || 'API Error');
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

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