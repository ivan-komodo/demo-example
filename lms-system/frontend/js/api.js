/**
 * LMS System - API Client
 * Базовый клиент для работы с API
 */

const API_BASE_URL = '/api/v1';

// [START_LOG_LINE]
/**
 * ANCHOR: LOG_LINE_JS
 * PURPOSE: AI-friendly логирование для автоматического анализа и диагностики ошибок.
 * 
 * @PreConditions:
 * - module: непустая строка с названием модуля
 * - level: один из "DEBUG" | "INFO" | "WARN" | "ERROR"
 * - functionName: непустая строка с названием функции
 * - anchor: ANCHOR_ID из контракта (UPPER_SNAKE_CASE)
 * - point: одна из точек ENTRY | EXIT | BRANCH | DECISION | CHECK | ERROR | RETRY | STATE_CHANGE
 * - data: объект с контекстными данными
 * 
 * @PostConditions:
 * - выводит структурированный лог в console
 * 
 * @Invariants:
 * - формат лога всегда JSON-структурированный
 * - anchor всегда совпадает с контрактом функции
 * 
 * @SideEffects:
 * - вывод в console
 * 
 * @ForbiddenChanges:
 * - формат лога (JSON structured)
 * - обязательные поля: timestamp, module, level, function, anchor, point
 */
function logLine(module, level, functionName, anchor, point, data = {}) {
    const logEntry = {
        timestamp: new Date().toISOString(),
        module: module,
        level: level,
        function: functionName,
        anchor: anchor,
        point: point,
        data: data
    };
    
    const logMessage = JSON.stringify(logEntry);
    
    switch (level) {
        case 'DEBUG':
            console.debug(logMessage);
            break;
        case 'INFO':
            console.info(logMessage);
            break;
        case 'WARN':
            console.warn(logMessage);
            break;
        case 'ERROR':
            console.error(logMessage);
            break;
    }
}
// [END_LOG_LINE]


// === CHUNK: API_CLIENT_V1 [FRONTEND] ===
// Описание: API клиент для взаимодействия с backend.
// Dependencies: LOG_LINE_JS

/**
 * API Client class
 */
// [START_API_CLIENT_CLASS]
/**
 * ANCHOR: API_CLIENT_CLASS
 * PURPOSE: Класс для управления HTTP запросами к API с авторизацией.
 * 
 * @PreConditions:
 * - baseUrl валидный URL строки API
 * 
 * @PostConditions:
 * - создаёт экземпляр клиента с методами для HTTP запросов
 * 
 * @Invariants:
 * - всегда хранит baseUrl и accessToken
 * - токены синхронизированы с localStorage
 * 
 * @SideEffects:
 * - чтение/запись localStorage
 * 
 * @ForbiddenChanges:
 * - формат Authorization header (Bearer token)
 */
class APIClient {
    // [START_API_CLIENT_CONSTRUCTOR]
    /**
     * ANCHOR: API_CLIENT_CONSTRUCTOR
     * PURPOSE: Инициализация API клиента.
     * 
     * @PreConditions:
     * - baseUrl строка базового URL API
     * 
     * @PostConditions:
     * - инициализирует клиент с baseUrl и пустым accessToken
     * 
     * @Invariants:
     * - accessToken всегда null при создании
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - начальное значение accessToken = null
     */
    constructor(baseUrl) {
        logLine("api", "DEBUG", "constructor", "API_CLIENT_CONSTRUCTOR", "ENTRY", {
            "baseUrl": baseUrl
        });
        
        this.baseUrl = baseUrl;
        this.accessToken = null;
        
        logLine("api", "DEBUG", "constructor", "API_CLIENT_CONSTRUCTOR", "EXIT", {
            "result": "initialized"
        });
    }
    // [END_API_CLIENT_CONSTRUCTOR]

    /**
     * Установить access token
     * @param {string} token 
     */
    // [START_SET_ACCESS_TOKEN]
    /**
     * ANCHOR: SET_ACCESS_TOKEN
     * PURPOSE: Сохранение access токена.
     * 
     * @PreConditions:
     * - token валидная строка JWT токена
     * 
     * @PostConditions:
     * - сохраняет токен в памяти и localStorage
     * 
     * @Invariants:
     * - токен всегда синхронизирован с localStorage
     * 
     * @SideEffects:
     * - запись в localStorage
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - ключ localStorage 'access_token'
     */
    setAccessToken(token) {
        logLine("api", "DEBUG", "setAccessToken", "SET_ACCESS_TOKEN", "ENTRY", {
            "token_prefix": token ? token.substring(0, 10) + "..." : null
        });
        
        this.accessToken = token;
        localStorage.setItem('access_token', token);
        
        logLine("api", "INFO", "setAccessToken", "SET_ACCESS_TOKEN", "STATE_CHANGE", {
            "action": "access_token_set"
        });
        logLine("api", "DEBUG", "setAccessToken", "SET_ACCESS_TOKEN", "EXIT", {
            "result": "success"
        });
    }
    // [END_SET_ACCESS_TOKEN]

    /**
     * Получить access token
     * @returns {string|null}
     */
    // [START_GET_ACCESS_TOKEN]
    /**
     * ANCHOR: GET_ACCESS_TOKEN
     * PURPOSE: Получение access токена.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - возвращает токен из памяти или localStorage
     * 
     * @Invariants:
     * - при отсутствии в памяти ищет в localStorage
     * 
     * @SideEffects:
     * - чтение из localStorage
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - fallback на localStorage при null в памяти
     */
    getAccessToken() {
        logLine("api", "DEBUG", "getAccessToken", "GET_ACCESS_TOKEN", "ENTRY", {});
        
        if (!this.accessToken) {
            this.accessToken = localStorage.getItem('access_token');
            logLine("api", "DEBUG", "getAccessToken", "GET_ACCESS_TOKEN", "BRANCH", {
                "branch": "loaded_from_storage",
                "found": !!this.accessToken
            });
        }
        
        logLine("api", "DEBUG", "getAccessToken", "GET_ACCESS_TOKEN", "EXIT", {
            "result": this.accessToken ? "found" : "not_found"
        });
        
        return this.accessToken;
    }
    // [END_GET_ACCESS_TOKEN]

    /**
     * Установить refresh token
     * @param {string} token 
     */
    // [START_SET_REFRESH_TOKEN]
    /**
     * ANCHOR: SET_REFRESH_TOKEN
     * PURPOSE: Сохранение refresh токена.
     * 
     * @PreConditions:
     * - token валидная строка JWT токена
     * 
     * @PostConditions:
     * - сохраняет токен в localStorage
     * 
     * @Invariants:
     * - токен хранится только в localStorage (не в памяти)
     * 
     * @SideEffects:
     * - запись в localStorage
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - ключ localStorage 'refresh_token'
     */
    setRefreshToken(token) {
        logLine("api", "DEBUG", "setRefreshToken", "SET_REFRESH_TOKEN", "ENTRY", {
            "token_prefix": token ? token.substring(0, 10) + "..." : null
        });
        
        localStorage.setItem('refresh_token', token);
        
        logLine("api", "INFO", "setRefreshToken", "SET_REFRESH_TOKEN", "STATE_CHANGE", {
            "action": "refresh_token_set"
        });
        logLine("api", "DEBUG", "setRefreshToken", "SET_REFRESH_TOKEN", "EXIT", {
            "result": "success"
        });
    }
    // [END_SET_REFRESH_TOKEN]

    /**
     * Получить refresh token
     * @returns {string|null}
     */
    // [START_GET_REFRESH_TOKEN]
    /**
     * ANCHOR: GET_REFRESH_TOKEN
     * PURPOSE: Получение refresh токена.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - возвращает токен из localStorage или null
     * 
     * @Invariants:
     * - всегда читает напрямую из localStorage
     * 
     * @SideEffects:
     * - чтение из localStorage
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - прямой доступ к localStorage
     */
    getRefreshToken() {
        logLine("api", "DEBUG", "getRefreshToken", "GET_REFRESH_TOKEN", "ENTRY", {});
        
        const token = localStorage.getItem('refresh_token');
        
        logLine("api", "DEBUG", "getRefreshToken", "GET_REFRESH_TOKEN", "EXIT", {
            "result": token ? "found" : "not_found"
        });
        
        return token;
    }
    // [END_GET_REFRESH_TOKEN]

    /**
     * Очистить токены
     */
    // [START_CLEAR_TOKENS]
    /**
     * ANCHOR: CLEAR_TOKENS
     * PURPOSE: Очистка данных аутентификации.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - удаляет все токены из памяти и localStorage
     * 
     * @Invariants:
     * - очищаются все связанные данные (access, refresh, user)
     * 
     * @SideEffects:
     * - удаление из localStorage
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - удаляются ключи: access_token, refresh_token, user
     */
    clearTokens() {
        logLine("api", "DEBUG", "clearTokens", "CLEAR_TOKENS", "ENTRY", {});
        
        this.accessToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        logLine("api", "INFO", "clearTokens", "CLEAR_TOKENS", "STATE_CHANGE", {
            "action": "tokens_cleared"
        });
        logLine("api", "DEBUG", "clearTokens", "CLEAR_TOKENS", "EXIT", {
            "result": "success"
        });
    }
    // [END_CLEAR_TOKENS]

    /**
     * Получить заголовки для запроса
     * @param {boolean} withAuth - добавлять ли авторизацию
     * @returns {Object}
     */
    // [START_GET_HEADERS]
    /**
     * ANCHOR: GET_HEADERS
     * PURPOSE: Формирование заголовков HTTP запроса.
     * 
     * @PreConditions:
     * - withAuth булево значение
     * 
     * @PostConditions:
     * - возвращает объект заголовков с Content-Type и опционально Authorization
     * 
     * @Invariants:
     * - Content-Type всегда 'application/json'
     * - Authorization только при withAuth=true и наличии токена
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - формат Authorization header (Bearer token)
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
    // [END_GET_HEADERS]

    /**
     * Обновить access token
     * @returns {Promise<boolean>}
     */
    // [START_REFRESH_ACCESS_TOKEN]
    /**
     * ANCHOR: REFRESH_ACCESS_TOKEN
     * PURPOSE: Обновление access токена через refresh токен.
     * 
     * @PreConditions:
     * - refresh токен существует в localStorage
     * 
     * @PostConditions:
     * - при успехе обновляет access токен и возвращает true
     * - при неудаче очищает токены и возвращает false
     * 
     * @Invariants:
     * - при неудаче всегда очищает токены
     * 
     * @SideEffects:
     * - HTTP запрос к /auth/refresh/
     * - обновление localStorage
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - endpoint /auth/refresh/
     */
    async refreshAccessToken() {
        logLine("api", "DEBUG", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "ENTRY", {});
        
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            logLine("api", "WARN", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "ERROR", {
                "reason": "no_refresh_token"
            });
            logLine("api", "DEBUG", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "EXIT", {
                "result": "failed"
            });
            return false;
        }

        try {
            logLine("api", "DEBUG", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "STATE_CHANGE", {
                "action": "refresh_request"
            });
            
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
                
                logLine("api", "INFO", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "STATE_CHANGE", {
                    "action": "token_refreshed"
                });
                logLine("api", "DEBUG", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "EXIT", {
                    "result": "success"
                });
                return true;
            } else {
                logLine("api", "WARN", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "ERROR", {
                    "reason": "refresh_failed",
                    "status": response.status
                });
                this.clearTokens();
                logLine("api", "DEBUG", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "EXIT", {
                    "result": "failed"
                });
                return false;
            }
        } catch (error) {
            logLine("api", "ERROR", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "ERROR", {
                "reason": "network_error",
                "error": error.message
            });
            this.clearTokens();
            logLine("api", "DEBUG", "refreshAccessToken", "REFRESH_ACCESS_TOKEN", "EXIT", {
                "result": "failed"
            });
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
    /**
     * ANCHOR: REQUEST
     * PURPOSE: Выполнение HTTP запроса с обработкой авторизации.
     * 
     * @PreConditions:
     * - endpoint строка пути API
     * - options объект с method, body, withAuth, retry
     * 
     * @PostConditions:
     * - возвращает JSON ответ или выбрасывает APIError
     * - при 401 пытается обновить токен и повторить запрос
     * 
     * @Invariants:
     * - при 401 с retry=true делается только одна попытка обновления токена
     * - при ошибке сети выбрасывается APIError со status=0
     * 
     * @SideEffects:
     * - HTTP запрос
     * - возможное обновление токена
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - редирект на /login.html при неудачном обновлении токена
     */
    async request(endpoint, options = {}) {
        const {
            method = 'GET',
            body = null,
            withAuth = true,
            retry = true,
        } = options;

        logLine("api", "DEBUG", "request", "REQUEST", "ENTRY", {
            "endpoint": endpoint,
            "method": method,
            "withAuth": withAuth
        });

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
                logLine("api", "DEBUG", "request", "REQUEST", "BRANCH", {
                    "branch": "401_retry",
                    "endpoint": endpoint
                });
                
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Повторяем запрос с новым токеном
                    logLine("api", "DEBUG", "request", "REQUEST", "RETRY", {
                        "endpoint": endpoint
                    });
                    return this.request(endpoint, { ...options, retry: false });
                } else {
                    // Перенаправляем на страницу входа
                    logLine("api", "WARN", "request", "REQUEST", "ERROR", {
                        "reason": "refresh_failed_redirect",
                        "endpoint": endpoint
                    });
                    window.location.href = '/login.html';
                    throw new Error('Unauthorized');
                }
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                logLine("api", "ERROR", "request", "REQUEST", "ERROR", {
                    "reason": "http_error",
                    "status": response.status,
                    "endpoint": endpoint
                });
                throw new APIError(response.status, errorData);
            }

            // Для ответов без контента (204 No Content)
            if (response.status === 204) {
                logLine("api", "DEBUG", "request", "REQUEST", "EXIT", {
                    "result": "no_content"
                });
                return null;
            }

            const data = await response.json();
            logLine("api", "DEBUG", "request", "REQUEST", "EXIT", {
                "result": "success",
                "endpoint": endpoint
            });
            return data;
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            logLine("api", "ERROR", "request", "REQUEST", "ERROR", {
                "reason": "network_error",
                "error": error.message,
                "endpoint": endpoint
            });
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
    /**
     * ANCHOR: GET
     * PURPOSE: Выполнение GET запроса.
     * 
     * @PreConditions:
     * - endpoint строка пути API
     * - params объект query параметров
     * 
     * @PostConditions:
     * - возвращает результат GET запроса
     * 
     * @Invariants:
     * - params преобразуются в query string
     * 
     * @SideEffects:
     * - делегирует в request()
     * 
     * @ForbiddenChanges:
     * - method='GET' всегда
     */
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
    /**
     * ANCHOR: POST
     * PURPOSE: Выполнение POST запроса.
     * 
     * @PreConditions:
     * - endpoint строка пути API
     * - body объект данных для отправки
     * 
     * @PostConditions:
     * - возвращает результат POST запроса
     * 
     * @Invariants:
     * - body всегда сериализуется в JSON
     * 
     * @SideEffects:
     * - делегирует в request()
     * 
     * @ForbiddenChanges:
     * - method='POST' всегда
     */
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
    /**
     * ANCHOR: PUT
     * PURPOSE: Выполнение PUT запроса.
     * 
     * @PreConditions:
     * - endpoint строка пути API
     * - body объект данных для отправки
     * 
     * @PostConditions:
     * - возвращает результат PUT запроса
     * 
     * @Invariants:
     * - body всегда сериализуется в JSON
     * 
     * @SideEffects:
     * - делегирует в request()
     * 
     * @ForbiddenChanges:
     * - method='PUT' всегда
     */
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
    /**
     * ANCHOR: PATCH
     * PURPOSE: Выполнение PATCH запроса.
     * 
     * @PreConditions:
     * - endpoint строка пути API
     * - body объект данных для отправки
     * 
     * @PostConditions:
     * - возвращает результат PATCH запроса
     * 
     * @Invariants:
     * - body всегда сериализуется в JSON
     * 
     * @SideEffects:
     * - делегирует в request()
     * 
     * @ForbiddenChanges:
     * - method='PATCH' всегда
     */
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
    /**
     * ANCHOR: DELETE
     * PURPOSE: Выполнение DELETE запроса.
     * 
     * @PreConditions:
     * - endpoint строка пути API
     * 
     * @PostConditions:
     * - возвращает результат DELETE запроса
     * 
     * @Invariants:
     * - без body
     * 
     * @SideEffects:
     * - делегирует в request()
     * 
     * @ForbiddenChanges:
     * - method='DELETE' всегда
     */
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
/**
 * ANCHOR: API_ERROR_CLASS
 * PURPOSE: Класс ошибки для API запросов.
 * 
 * @PreConditions:
 * - status HTTP статус код
 * - data объект с деталями ошибки
 * 
 * @PostConditions:
 * - создаёт Error с дополнительными полями status и data
 * 
 * @Invariants:
 * - name всегда 'APIError'
 * - message берётся из data.detail или default
 * 
 * @SideEffects:
 * - нет побочных эффектов
 * 
 * @ForbiddenChanges:
 * - name='APIError'
 */
class APIError extends Error {
    // [START_API_ERROR_CONSTRUCTOR]
    /**
     * ANCHOR: API_ERROR_CONSTRUCTOR
     * PURPOSE: Инициализация ошибки API.
     * 
     * @PreConditions:
     * - status числовой HTTP статус
     * - data объект с деталями ошибки
     * 
     * @PostConditions:
     * - создаёт экземпляр ошибки с name, status, data
     * 
     * @Invariants:
     * - message всегда задаётся
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - поля name, status, data
     */
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