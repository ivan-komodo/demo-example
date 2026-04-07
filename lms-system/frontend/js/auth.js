/**
 * LMS System - Auth Module
 * Модуль аутентификации и авторизации
 */

// === CHUNK: AUTH_MODULE_V1 [FRONTEND] ===
// Описание: Модуль аутентификации для управления сессией пользователя.
// Dependencies: API_CLIENT_V1

/**
 * Auth class
 */
// [START_AUTH_CLASS]
/**
 * ANCHOR: AUTH_CLASS
 * PURPOSE: Класс для управления аутентификацией пользователя.
 * 
 * @PreConditions:
 * - нет нетривиальных предусловий
 * 
 * @PostConditions:
 * - создаёт экземпляр с методами для управления аутентификацией
 * 
 * @Invariants:
 * - user и isAuthenticated синхронизированы
 * - данные синхронизированы с localStorage
 * 
 * @SideEffects:
 * - чтение/запись localStorage
 * - HTTP запросы через API
 * 
 * @ForbiddenChanges:
 * - вызов init() в конструкторе
 */
class Auth {
    // [START_AUTH_CONSTRUCTOR]
    /**
     * ANCHOR: AUTH_CONSTRUCTOR
     * PURPOSE: Инициализация модуля аутентификации.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - инициализирует user=null, isAuthenticated=false, вызывает init()
     * 
     * @Invariants:
     * - начальное состояние всегда logged out
     * 
     * @SideEffects:
     * - вызывает init() для проверки токенов
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - начальные значения user=null, isAuthenticated=false
     */
    constructor() {
        logLine("auth", "DEBUG", "constructor", "AUTH_CONSTRUCTOR", "ENTRY", {});
        
        this.user = null;
        this.isAuthenticated = false;
        this.init();
        
        logLine("auth", "DEBUG", "constructor", "AUTH_CONSTRUCTOR", "EXIT", {
            "result": "initialized"
        });
    }
    // [END_AUTH_CONSTRUCTOR]

    /**
     * Инициализация модуля аутентификации
     */
    // [START_AUTH_INIT]
    /**
     * ANCHOR: AUTH_INIT
     * PURPOSE: Автоматическая инициализация при загрузке страницы.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - проверяет токены и восстанавливает сессию если возможно
     * 
     * @Invariants:
     * - при наличии токенов пытается восстановить сессию
     * - UI обновляется в конце
     * 
     * @SideEffects:
     * - чтение из localStorage
     * - возможный HTTP запрос для проверки auth
     * - обновление UI
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - вызов updateUI() в конце
     */
    async init() {
        logLine("auth", "DEBUG", "init", "AUTH_INIT", "ENTRY", {});
        
        // Проверяем наличие токенов
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');

        if (accessToken && refreshToken) {
            logLine("auth", "DEBUG", "init", "AUTH_INIT", "BRANCH", {
                "branch": "tokens_found",
                "has_access": !!accessToken,
                "has_refresh": !!refreshToken
            });
            
            api.setAccessToken(accessToken);
            await this.checkAuth();
        } else {
            logLine("auth", "DEBUG", "init", "AUTH_INIT", "BRANCH", {
                "branch": "no_tokens"
            });
        }

        this.updateUI();
        
        logLine("auth", "DEBUG", "init", "AUTH_INIT", "EXIT", {
            "result": "completed",
            "isAuthenticated": this.isAuthenticated
        });
    }
    // [END_AUTH_INIT]

    /**
     * Проверка аутентификации
     * @returns {Promise<boolean>}
     */
    // [START_CHECK_AUTH]
    /**
     * ANCHOR: CHECK_AUTH
     * PURPOSE: Проверка валидности текущей сессии.
     * 
     * @PreConditions:
     * - access токен установлен в api
     * 
     * @PostConditions:
     * - при успехе устанавливает user и isAuthenticated=true
     * - при неудаче вызывает logout
     * 
     * @Invariants:
     * - при неудаче всегда очищает состояние
     * 
     * @SideEffects:
     * - HTTP запрос к /auth/me/
     * - запись user в localStorage
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - при неудаче вызов logout()
     */
    async checkAuth() {
        logLine("auth", "DEBUG", "checkAuth", "CHECK_AUTH", "ENTRY", {});
        
        try {
            const user = await API.me();
            this.user = user;
            this.isAuthenticated = true;
            localStorage.setItem('user', JSON.stringify(user));
            
            logLine("auth", "INFO", "checkAuth", "CHECK_AUTH", "STATE_CHANGE", {
                "action": "session_restored",
                "user_id": user.id
            });
            logLine("auth", "DEBUG", "checkAuth", "CHECK_AUTH", "EXIT", {
                "result": "authenticated",
                "user_id": user.id
            });
            return true;
        } catch (error) {
            logLine("auth", "WARN", "checkAuth", "CHECK_AUTH", "ERROR", {
                "reason": "auth_check_failed",
                "error": error.message
            });
            this.logout();
            logLine("auth", "DEBUG", "checkAuth", "CHECK_AUTH", "EXIT", {
                "result": "failed"
            });
            return false;
        }
    }
    // [END_CHECK_AUTH]

    /**
     * Вход в систему
     * @param {string} email 
     * @param {string} password 
     * @returns {Promise<Object>}
     */
    // [START_LOGIN]
    /**
     * ANCHOR: LOGIN
     * PURPOSE: Аутентификация пользователя по email и паролю.
     * 
     * @PreConditions:
     * - email валидный email адрес
     * - password непустая строка
     * 
     * @PostConditions:
     * - при успехе сохраняет токены и user, обновляет UI
     * - при неудаче выбрасывает ошибку
     * 
     * @Invariants:
     * - при успехе isAuthenticated=true
     * - токены и user сохраняются в localStorage
     * 
     * @SideEffects:
     * - HTTP запрос к /auth/login/
     * - HTTP запрос к /auth/me/
     * - запись в localStorage
     * - обновление UI
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - порядок: login -> setTokens -> me -> saveUser -> updateUI
     */
    async login(email, password) {
        logLine("auth", "DEBUG", "login", "LOGIN", "ENTRY", {
            "email": email
        });
        
        try {
            const response = await API.login({ email, password });
            
            api.setAccessToken(response.access);
            api.setRefreshToken(response.refresh);
            
            // Получаем информацию о пользователе
            const user = await API.me();
            this.user = user;
            this.isAuthenticated = true;
            localStorage.setItem('user', JSON.stringify(user));
            
            this.updateUI();
            
            logLine("auth", "INFO", "login", "LOGIN", "STATE_CHANGE", {
                "action": "user_logged_in",
                "user_id": user.id,
                "email": email
            });
            logLine("auth", "DEBUG", "login", "LOGIN", "EXIT", {
                "result": "success",
                "user_id": user.id
            });
            
            return { success: true, user };
        } catch (error) {
            logLine("auth", "ERROR", "login", "LOGIN", "ERROR", {
                "reason": "login_failed",
                "email": email,
                "error": error.message
            });
            logLine("auth", "DEBUG", "login", "LOGIN", "EXIT", {
                "result": "failed"
            });
            throw error;
        }
    }
    // [END_LOGIN]

    /**
     * Регистрация
     * @param {Object} data - данные регистрации
     * @returns {Promise<Object>}
     */
    // [START_REGISTER]
    /**
     * ANCHOR: REGISTER
     * PURPOSE: Регистрация нового пользователя.
     * 
     * @PreConditions:
     * - data содержит email, password, full_name
     * 
     * @PostConditions:
     * - при успехе сохраняет токены и user, обновляет UI
     * - при неудаче выбрасывает ошибку
     * 
     * @Invariants:
     * - при успехе isAuthenticated=true
     * - токены и user сохраняются в localStorage
     * 
     * @SideEffects:
     * - HTTP запрос к /auth/register/
     * - HTTP запрос к /auth/me/
     * - запись в localStorage
     * - обновление UI
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - порядок: register -> setTokens -> me -> saveUser -> updateUI
     */
    async register(data) {
        logLine("auth", "DEBUG", "register", "REGISTER", "ENTRY", {
            "email": data.email
        });
        
        try {
            const response = await API.register(data);
            
            api.setAccessToken(response.access);
            api.setRefreshToken(response.refresh);
            
            // Получаем информацию о пользователе
            const user = await API.me();
            this.user = user;
            this.isAuthenticated = true;
            localStorage.setItem('user', JSON.stringify(user));
            
            this.updateUI();
            
            logLine("auth", "INFO", "register", "REGISTER", "STATE_CHANGE", {
                "action": "user_registered",
                "user_id": user.id,
                "email": data.email
            });
            logLine("auth", "DEBUG", "register", "REGISTER", "EXIT", {
                "result": "success",
                "user_id": user.id
            });
            
            return { success: true, user };
        } catch (error) {
            logLine("auth", "ERROR", "register", "REGISTER", "ERROR", {
                "reason": "register_failed",
                "email": data.email,
                "error": error.message
            });
            logLine("auth", "DEBUG", "register", "REGISTER", "EXIT", {
                "result": "failed"
            });
            throw error;
        }
    }
    // [END_REGISTER]

    /**
     * Выход из системы
     */
    // [START_LOGOUT]
    /**
     * ANCHOR: LOGOUT
     * PURPOSE: Завершение сессии пользователя.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - очищает токены, user, isAuthenticated, перенаправляет на login
     * 
     * @Invariants:
     * - всегда очищает состояние, даже при ошибке API
     * 
     * @SideEffects:
     * - HTTP запрос к /auth/logout/
     * - очистка localStorage
     * - редирект на /login.html
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - очистка состояния в finally блоке
     * - редирект на /login.html
     */
    async logout() {
        logLine("auth", "DEBUG", "logout", "LOGOUT", "ENTRY", {
            "user_id": this.user?.id
        });
        
        try {
            await API.logout();
        } catch (error) {
            logLine("auth", "WARN", "logout", "LOGOUT", "ERROR", {
                "reason": "logout_api_error",
                "error": error.message
            });
        } finally {
            api.clearTokens();
            this.user = null;
            this.isAuthenticated = false;
            this.updateUI();
            
            logLine("auth", "INFO", "logout", "LOGOUT", "STATE_CHANGE", {
                "action": "user_logged_out"
            });
            logLine("auth", "DEBUG", "logout", "LOGOUT", "EXIT", {
                "result": "success"
            });
            
            window.location.href = '/login.html';
        }
    }
    // [END_LOGOUT]

    /**
     * Получить текущего пользователя
     * @returns {Object|null}
     */
    // [START_GET_USER]
    /**
     * ANCHOR: GET_USER
     * PURPOSE: Получение данных текущего пользователя.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - возвращает user из памяти или localStorage
     * 
     * @Invariants:
     * - при отсутствии в памяти ищет в localStorage
     * 
     * @SideEffects:
     * - чтение из localStorage
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - fallback на localStorage
     */
    getUser() {
        logLine("auth", "DEBUG", "getUser", "GET_USER", "ENTRY", {});
        
        if (!this.user) {
            const userStr = localStorage.getItem('user');
            if (userStr) {
                try {
                    this.user = JSON.parse(userStr);
                    logLine("auth", "DEBUG", "getUser", "GET_USER", "BRANCH", {
                        "branch": "loaded_from_storage"
                    });
                } catch (e) {
                    this.user = null;
                    logLine("auth", "WARN", "getUser", "GET_USER", "ERROR", {
                        "reason": "parse_error"
                    });
                }
            }
        }
        
        logLine("auth", "DEBUG", "getUser", "GET_USER", "EXIT", {
            "result": this.user ? "found" : "not_found"
        });
        
        return this.user;
    }
    // [END_GET_USER]

    /**
     * Проверить роль пользователя
     * @param {string} role - роль для проверки (admin, trainer, learner)
     * @returns {boolean}
     */
    // [START_HAS_ROLE]
    /**
     * ANCHOR: HAS_ROLE
     * PURPOSE: Проверка роли текущего пользователя.
     * 
     * @PreConditions:
     * - role строка роли (admin, trainer, learner)
     * 
     * @PostConditions:
     * - возвращает true если user.role совпадает с role
     * 
     * @Invariants:
     * - при отсутствии user возвращает false
     * 
     * @SideEffects:
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - строгое равенство role
     */
    hasRole(role) {
        logLine("auth", "DEBUG", "hasRole", "HAS_ROLE", "ENTRY", {
            "required_role": role
        });
        
        const user = this.getUser();
        const result = user && user.role === role;
        
        logLine("auth", "DEBUG", "hasRole", "HAS_ROLE", "EXIT", {
            "result": result,
            "user_role": user?.role
        });
        
        return result;
    }
    // [END_HAS_ROLE]

    /**
     * Проверить, является ли пользователь администратором
     * @returns {boolean}
     */
    // [START_IS_ADMIN]
    /**
     * ANCHOR: IS_ADMIN
     * PURPOSE: Проверка роли администратора.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - возвращает true если user.role === 'admin'
     * 
     * @Invariants:
     * - делегирует в hasRole
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - проверка role === 'admin'
     */
    isAdmin() {
        return this.hasRole('admin');
    }
    // [END_IS_ADMIN]

    /**
     * Проверить, является ли пользователь тренером
     * @returns {boolean}
     */
    // [START_IS_TRAINER]
    /**
     * ANCHOR: IS_TRAINER
     * PURPOSE: Проверка роли тренера.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - возвращает true если user.role === 'trainer'
     * 
     * @Invariants:
     * - делегирует в hasRole
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - проверка role === 'trainer'
     */
    isTrainer() {
        return this.hasRole('trainer');
    }
    // [END_IS_TRAINER]

    /**
     * Проверить, является ли пользователь обучающимся
     * @returns {boolean}
     */
    // [START_IS_LEARNER]
    /**
     * ANCHOR: IS_LEARNER
     * PURPOSE: Проверка роли обучающегося.
     * 
     * @PreConditions:
     * - нет нетривиальных предусловий
     * 
     * @PostConditions:
     * - возвращает true если user.role === 'learner'
     * 
     * @Invariants:
     * - делегирует в hasRole
     * 
     * @SideEffects:
     * - нет побочных эффектов
     * 
     * @ForbiddenChanges:
     * - проверка role === 'learner'
     */
    isLearner() {
        return this.hasRole('learner');
    }
    // [END_IS_LEARNER]

    /**
     * Обновить UI в зависимости от состояния аутентификации
     */
    // [START_UPDATE_UI]
    /**
     * ANCHOR: UPDATE_UI
     * PURPOSE: Обновление интерфейса при изменении состояния аутентификации.
     * 
     * @PreConditions:
     * - DOM элементы с id auth-buttons, user-menu, user-name существуют
     * 
     * @PostConditions:
     * - показывает/скрывает элементы в зависимости от isAuthenticated
     * 
     * @Invariants:
     * - при authenticated показывается user-menu
     * - при not authenticated показывается auth-buttons
     * 
     * @SideEffects:
     * - изменение DOM
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - элементы: auth-buttons, user-menu, user-name, progress-link, bookings-link
     */
    updateUI() {
        logLine("auth", "DEBUG", "updateUI", "UPDATE_UI", "ENTRY", {
            "isAuthenticated": this.isAuthenticated
        });
        
        const authButtons = document.getElementById('auth-buttons');
        const userMenu = document.getElementById('user-menu');
        const userName = document.getElementById('user-name');
        const progressLink = document.getElementById('progress-link');
        const bookingsLink = document.getElementById('bookings-link');

        if (this.isAuthenticated && this.user) {
            // Показываем меню пользователя
            if (authButtons) authButtons.style.display = 'none';
            if (userMenu) {
                userMenu.style.display = 'flex';
                userMenu.style.alignItems = 'center';
                userMenu.style.gap = '1rem';
            }
            if (userName) {
                userName.textContent = this.user.full_name || this.user.email;
            }

            // Показываем ссылки в зависимости от роли
            if (progressLink) progressLink.style.display = 'inline';
            if (bookingsLink) bookingsLink.style.display = 'inline';
            
            logLine("auth", "DEBUG", "updateUI", "UPDATE_UI", "BRANCH", {
                "branch": "authenticated_ui"
            });
        } else {
            // Показываем кнопки входа/регистрации
            if (authButtons) authButtons.style.display = 'flex';
            if (userMenu) userMenu.style.display = 'none';
            if (progressLink) progressLink.style.display = 'none';
            if (bookingsLink) bookingsLink.style.display = 'none';
            
            logLine("auth", "DEBUG", "updateUI", "UPDATE_UI", "BRANCH", {
                "branch": "unauthenticated_ui"
            });
        }
        
        logLine("auth", "DEBUG", "updateUI", "UPDATE_UI", "EXIT", {
            "result": "updated"
        });
    }
    // [END_UPDATE_UI]

    /**
     * Требовать аутентификацию
     * Перенаправляет на страницу входа, если пользователь не аутентифицирован
     * @param {string} requiredRole - требуемая роль (опционально)
     * @returns {boolean}
     */
    // [START_REQUIRE_AUTH]
    /**
     * ANCHOR: REQUIRE_AUTH
     * PURPOSE: Защита страниц от неавторизованного доступа.
     * 
     * @PreConditions:
     * - requiredRole опциональная строка роли
     * 
     * @PostConditions:
     * - возвращает true если пользователь аутентифицирован и имеет роль
     * - перенаправляет на login или показывает access denied
     * 
     * @Invariants:
     * - при отсутствии auth редирект на login
     * - при отсутствии роли показывает access denied
     * 
     * @SideEffects:
     * - возможный редирект на /login.html
     * - возможное изменение DOM (access denied)
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - редирект на /login.html при неаутентифицированном
     */
    requireAuth(requiredRole = null) {
        logLine("auth", "DEBUG", "requireAuth", "REQUIRE_AUTH", "ENTRY", {
            "requiredRole": requiredRole
        });
        
        if (!this.isAuthenticated) {
            logLine("auth", "WARN", "requireAuth", "REQUIRE_AUTH", "DECISION", {
                "decision": "redirect_to_login",
                "reason": "not_authenticated"
            });
            logLine("auth", "DEBUG", "requireAuth", "REQUIRE_AUTH", "EXIT", {
                "result": "redirect_login"
            });
            window.location.href = '/login.html';
            return false;
        }

        if (requiredRole && !this.hasRole(requiredRole)) {
            logLine("auth", "WARN", "requireAuth", "REQUIRE_AUTH", "DECISION", {
                "decision": "access_denied",
                "required": requiredRole,
                "actual": this.user?.role
            });
            logLine("auth", "DEBUG", "requireAuth", "REQUIRE_AUTH", "EXIT", {
                "result": "access_denied"
            });
            this.showAccessDenied();
            return false;
        }

        logLine("auth", "DEBUG", "requireAuth", "REQUIRE_AUTH", "EXIT", {
            "result": "authorized"
        });
        return true;
    }
    // [END_REQUIRE_AUTH]

    /**
     * Показать сообщение об отказе в доступе
     */
    // [START_SHOW_ACCESS_DENIED]
    /**
     * ANCHOR: SHOW_ACCESS_DENIED
     * PURPOSE: Отображение сообщения об отсутствии прав.
     * 
     * @PreConditions:
     * - DOM элемент .main существует
     * 
     * @PostConditions:
     * - заменяет содержимое .main сообщением о доступе запрещён
     * 
     * @Invariants:
     * - всегда показывает одинаковое сообщение
     * 
     * @SideEffects:
     * - изменение DOM
     * - логирование операции
     * 
     * @ForbiddenChanges:
     * - HTML структура сообщения
     */
    showAccessDenied() {
        logLine("auth", "DEBUG", "showAccessDenied", "SHOW_ACCESS_DENIED", "ENTRY", {});
        
        const main = document.querySelector('.main');
        if (main) {
            main.innerHTML = `
                <div class="container">
                    <div class="card text-center">
                        <h2>Доступ запрещен</h2>
                        <p>У вас нет прав для просмотра этой страницы.</p>
                        <a href="/" class="btn btn-primary">На главную</a>
                    </div>
                </div>
            `;
            
            logLine("auth", "INFO", "showAccessDenied", "SHOW_ACCESS_DENIED", "STATE_CHANGE", {
                "action": "access_denied_shown"
            });
        }
        
        logLine("auth", "DEBUG", "showAccessDenied", "SHOW_ACCESS_DENIED", "EXIT", {
            "result": "shown"
        });
    }
    // [END_SHOW_ACCESS_DENIED]
}
// [END_AUTH_CLASS]

// === END_CHUNK: AUTH_MODULE_V1 ===

// Создаем глобальный экземпляр
const auth = new Auth();

/**
 * Обработчик формы входа
 * @param {Event} event 
 */
// [START_HANDLE_LOGIN]
// ANCHOR: HANDLE_LOGIN
// @PreConditions:
// - event событие submit формы
// - форма содержит поля email и password
// @PostConditions:
// - при успехе перенаправляет на главную
// - при неудаче показывает ошибку
// PURPOSE: Обработка отправки формы входа.
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = form.email.value;
    const password = form.password.value;
    const errorDiv = document.getElementById('login-error');
    
    try {
        await auth.login(email, password);
        window.location.href = '/';
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.data?.detail || 'Ошибка входа';
            errorDiv.style.display = 'block';
        }
    }
}
// [END_HANDLE_LOGIN]

/**
 * Обработчик формы регистрации
 * @param {Event} event 
 */
// [START_HANDLE_REGISTER]
// ANCHOR: HANDLE_REGISTER
// @PreConditions:
// - event событие submit формы
// - форма содержит поля email, password, password_confirm, full_name
// @PostConditions:
// - при успехе перенаправляет на главную
// - при неудаче показывает ошибку
// PURPOSE: Обработка отправки формы регистрации.
async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const data = {
        email: form.email.value,
        password: form.password.value,
        password_confirm: form.password_confirm.value,
        full_name: form.full_name.value,
    };
    const errorDiv = document.getElementById('register-error');
    
    try {
        await auth.register(data);
        window.location.href = '/';
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.data?.detail || 'Ошибка регистрации';
            errorDiv.style.display = 'block';
        }
    }
}
// [END_HANDLE_REGISTER]

/**
 * Обработчик выхода
 * @param {Event} event 
 */
// [START_HANDLE_LOGOUT]
// ANCHOR: HANDLE_LOGOUT
// @PreConditions:
// - event событие click
// @PostConditions:
// - вызывает auth.logout()
// PURPOSE: Обработка клика по кнопке выхода.
async function handleLogout(event) {
    event.preventDefault();
    await auth.logout();
}
// [END_HANDLE_LOGOUT]

// Export for use in other modules
window.auth = auth;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.handleLogout = handleLogout;