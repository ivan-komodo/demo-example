/**
 * LMS System - Auth Module
 * Модуль аутентификации и авторизации
 */

/**
 * Auth class
 */
class Auth {
    constructor() {
        this.user = null;
        this.isAuthenticated = false;
        this.init();
    }

    /**
     * Инициализация модуля аутентификации
     */
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

    /**
     * Проверка аутентификации
     * @returns {Promise<boolean>}
     */
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

    /**
     * Вход в систему
     * @param {string} email 
     * @param {string} password 
     * @returns {Promise<Object>}
     */
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

    /**
     * Регистрация
     * @param {Object} data - данные регистрации
     * @returns {Promise<Object>}
     */
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

    /**
     * Выход из системы
     */
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

    /**
     * Получить текущего пользователя
     * @returns {Object|null}
     */
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

    /**
     * Проверить роль пользователя
     * @param {string} role - роль для проверки (admin, trainer, learner)
     * @returns {boolean}
     */
    hasRole(role) {
        const user = this.getUser();
        return user && user.role === role;
    }

    /**
     * Проверить, является ли пользователь администратором
     * @returns {boolean}
     */
    isAdmin() {
        return this.hasRole('admin');
    }

    /**
     * Проверить, является ли пользователь тренером
     * @returns {boolean}
     */
    isTrainer() {
        return this.hasRole('trainer');
    }

    /**
     * Проверить, является ли пользователь обучающимся
     * @returns {boolean}
     */
    isLearner() {
        return this.hasRole('learner');
    }

    /**
     * Обновить UI в зависимости от состояния аутентификации
     */
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

    /**
     * Требовать аутентификацию
     * Перенаправляет на страницу входа, если пользователь не аутентифицирован
     * @param {string} requiredRole - требуемая роль (опционально)
     * @returns {boolean}
     */
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

    /**
     * Показать сообщение об отказе в доступе
     */
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
}

// Создаем глобальный экземпляр
const auth = new Auth();

/**
 * Глобальная функция выхода
 */
function logout() {
    auth.logout();
}

// Export for use in other modules
window.auth = auth;
window.logout = logout;