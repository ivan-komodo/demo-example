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
// ANCHOR: AUTH_CLASS
// @PreConditions:
// - нет нетривиальных предусловий
// @PostConditions:
// - создаёт экземпляр с методами для управления аутентификацией
// PURPOSE: Класс для управления аутентификацией пользователя.
class Auth {
    // [START_AUTH_CONSTRUCTOR]
    // ANCHOR: AUTH_CONSTRUCTOR
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - инициализирует user=null, isAuthenticated=false, вызывает init()
    // PURPOSE: Инициализация модуля аутентификации.
    constructor() {
        this.user = null;
        this.isAuthenticated = false;
        this.init();
    }
    // [END_AUTH_CONSTRUCTOR]

    /**
     * Инициализация модуля аутентификации
     */
    // [START_AUTH_INIT]
    // ANCHOR: AUTH_INIT
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - проверяет токены и восстанавливает сессию если возможно
    // PURPOSE: Автоматическая инициализация при загрузке страницы.
    async init() {
        // Проверяем наличие токенов
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');

        if (accessToken && refreshToken) {
            api.setAccessToken(accessToken);
            await this.checkAuth();
        }

        this.updateUI();
    }
    // [END_AUTH_INIT]

    /**
     * Проверка аутентификации
     * @returns {Promise<boolean>}
     */
    // [START_CHECK_AUTH]
    // ANCHOR: CHECK_AUTH
    // @PreConditions:
    // - access токен установлен в api
    // @PostConditions:
    // - при успехе устанавливает user и isAuthenticated=true
    // - при неудаче вызывает logout
    // PURPOSE: Проверка валидности текущей сессии.
    async checkAuth() {
        try {
            const user = await API.me();
            this.user = user;
            this.isAuthenticated = true;
            localStorage.setItem('user', JSON.stringify(user));
            return true;
        } catch (error) {
            console.error('Auth check failed:', error);
            this.logout();
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
    // ANCHOR: LOGIN
    // @PreConditions:
    // - email валидный email адрес
    // - password непустая строка
    // @PostConditions:
    // - при успехе сохраняет токены и user, обновляет UI
    // - при неудаче выбрасывает ошибку
    // PURPOSE: Аутентификация пользователя по email и паролю.
    async login(email, password) {
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
            
            return { success: true, user };
        } catch (error) {
            console.error('Login failed:', error);
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
    // ANCHOR: REGISTER
    // @PreConditions:
    // - data содержит email, password, full_name
    // @PostConditions:
    // - при успехе сохраняет токены и user, обновляет UI
    // - при неудаче выбрасывает ошибку
    // PURPOSE: Регистрация нового пользователя.
    async register(data) {
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
            
            return { success: true, user };
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }
    // [END_REGISTER]

    /**
     * Выход из системы
     */
    // [START_LOGOUT]
    // ANCHOR: LOGOUT
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - очищает токены, user, isAuthenticated, перенаправляет на login
    // PURPOSE: Завершение сессии пользователя.
    async logout() {
        try {
            await API.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            api.clearTokens();
            this.user = null;
            this.isAuthenticated = false;
            this.updateUI();
            window.location.href = '/login.html';
        }
    }
    // [END_LOGOUT]

    /**
     * Получить текущего пользователя
     * @returns {Object|null}
     */
    // [START_GET_USER]
    // ANCHOR: GET_USER
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - возвращает user из памяти или localStorage
    // PURPOSE: Получение данных текущего пользователя.
    getUser() {
        if (!this.user) {
            const userStr = localStorage.getItem('user');
            if (userStr) {
                try {
                    this.user = JSON.parse(userStr);
                } catch (e) {
                    this.user = null;
                }
            }
        }
        return this.user;
    }
    // [END_GET_USER]

    /**
     * Проверить роль пользователя
     * @param {string} role - роль для проверки (admin, trainer, learner)
     * @returns {boolean}
     */
    // [START_HAS_ROLE]
    // ANCHOR: HAS_ROLE
    // @PreConditions:
    // - role строка роли (admin, trainer, learner)
    // @PostConditions:
    // - возвращает true если user.role совпадает с role
    // PURPOSE: Проверка роли текущего пользователя.
    hasRole(role) {
        const user = this.getUser();
        return user && user.role === role;
    }
    // [END_HAS_ROLE]

    /**
     * Проверить, является ли пользователь администратором
     * @returns {boolean}
     */
    // [START_IS_ADMIN]
    // ANCHOR: IS_ADMIN
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - возвращает true если user.role === 'admin'
    // PURPOSE: Проверка роли администратора.
    isAdmin() {
        return this.hasRole('admin');
    }
    // [END_IS_ADMIN]

    /**
     * Проверить, является ли пользователь тренером
     * @returns {boolean}
     */
    // [START_IS_TRAINER]
    // ANCHOR: IS_TRAINER
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - возвращает true если user.role === 'trainer'
    // PURPOSE: Проверка роли тренера.
    isTrainer() {
        return this.hasRole('trainer');
    }
    // [END_IS_TRAINER]

    /**
     * Проверить, является ли пользователь обучающимся
     * @returns {boolean}
     */
    // [START_IS_LEARNER]
    // ANCHOR: IS_LEARNER
    // @PreConditions:
    // - нет нетривиальных предусловий
    // @PostConditions:
    // - возвращает true если user.role === 'learner'
    // PURPOSE: Проверка роли обучающегося.
    isLearner() {
        return this.hasRole('learner');
    }
    // [END_IS_LEARNER]

    /**
     * Обновить UI в зависимости от состояния аутентификации
     */
    // [START_UPDATE_UI]
    // ANCHOR: UPDATE_UI
    // @PreConditions:
    // - DOM элементы с id auth-buttons, user-menu, user-name существуют
    // @PostConditions:
    // - показывает/скрывает элементы в зависимости от isAuthenticated
    // PURPOSE: Обновление интерфейса при изменении состояния аутентификации.
    updateUI() {
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
        } else {
            // Показываем кнопки входа/регистрации
            if (authButtons) authButtons.style.display = 'flex';
            if (userMenu) userMenu.style.display = 'none';
            if (progressLink) progressLink.style.display = 'none';
            if (bookingsLink) bookingsLink.style.display = 'none';
        }
    }
    // [END_UPDATE_UI]

    /**
     * Требовать аутентификацию
     * Перенаправляет на страницу входа, если пользователь не аутентифицирован
     * @param {string} requiredRole - требуемая роль (опционально)
     * @returns {boolean}
     */
    // [START_REQUIRE_AUTH]
    // ANCHOR: REQUIRE_AUTH
    // @PreConditions:
    // - requiredRole опциональная строка роли
    // @PostConditions:
    // - возвращает true если пользователь аутентифицирован и имеет роль
    // - перенаправляет на login или показывает access denied
    // PURPOSE: Защита страниц от неавторизованного доступа.
    requireAuth(requiredRole = null) {
        if (!this.isAuthenticated) {
            window.location.href = '/login.html';
            return false;
        }

        if (requiredRole && !this.hasRole(requiredRole)) {
            this.showAccessDenied();
            return false;
        }

        return true;
    }
    // [END_REQUIRE_AUTH]

    /**
     * Показать сообщение об отказе в доступе
     */
    // [START_SHOW_ACCESS_DENIED]
    // ANCHOR: SHOW_ACCESS_DENIED
    // @PreConditions:
    // - DOM элемент .main существует
    // @PostConditions:
    // - заменяет содержимое .main сообщением о доступе запрещён
    // PURPOSE: Отображение сообщения об отсутствии прав.
    showAccessDenied() {
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
        }
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