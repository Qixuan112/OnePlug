/**
 * 插件市场 - 前端应用核心
 */

// API 配置
const API_BASE_URL = '/api';

// 存储键名
const STORAGE_KEYS = {
  TOKEN: 'plugin_marketplace_token',
  REFRESH_TOKEN: 'plugin_marketplace_refresh_token',
  USER: 'plugin_marketplace_user',
  TOKEN_EXPIRES: 'plugin_marketplace_token_expires'
};

/**
 * API 请求工具
 */
const api = {
  // 标记是否正在刷新 Token
  _isRefreshing: false,
  // 等待 Token 刷新的请求队列
  _refreshQueue: [],

  async request(url, options = {}) {
    // 检查 Token 是否需要刷新
    await this._checkAndRefreshToken();

    const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token 过期，尝试刷新
          const refreshed = await this._handleTokenExpired();
          if (refreshed) {
            // 刷新成功，重试请求
            return this.request(url, options);
          } else {
            // 刷新失败，清除登录状态并跳转
            auth.logout();
            window.location.href = '/login.html';
            return;
          }
        }
        // 尝试解析后端返回的错误信息
        let errorMessage = `HTTP ${response.status}: ${response.statusText || 'Bad Request'}`;
        try {
          const text = await response.text();
          if (text) {
            try {
              const errorData = JSON.parse(text);
              if (errorData && errorData.error) {
                errorMessage = errorData.error;
              } else if (errorData && errorData.message) {
                errorMessage = errorData.message;
              }
            } catch (e) {
              // 不是 JSON，使用文本内容
              errorMessage = `HTTP ${response.status}: ${text.substring(0, 200)}`;
            }
          }
        } catch (e) {
          // 读取失败，使用默认错误信息
        }
        throw new Error(errorMessage);
      }

      // 处理 204 No Content 响应
      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // 检查 Token 是否需要刷新
  async _checkAndRefreshToken() {
    const expiresAt = localStorage.getItem(STORAGE_KEYS.TOKEN_EXPIRES);
    if (!expiresAt) return;

    const expiresTime = parseInt(expiresAt);
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000;

    // 如果 Token 将在 5 分钟内过期，提前刷新
    if (expiresTime - now < fiveMinutes) {
      await this._refreshToken();
    }
  },

  // 处理 Token 过期
  async _handleTokenExpired() {
    if (this._isRefreshing) {
      // 如果正在刷新，等待刷新完成
      return new Promise((resolve) => {
        this._refreshQueue.push(resolve);
      });
    }
    return this._refreshToken();
  },

  // 刷新 Token
  async _refreshToken() {
    const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    if (!refreshToken) {
      return false;
    }

    this._isRefreshing = true;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      });

      if (!response.ok) {
        throw new Error('Refresh failed');
      }

      const data = await response.json();

      // 更新 Token
      localStorage.setItem(STORAGE_KEYS.TOKEN, data.access_token);
      // 更新过期时间（假设 Token 有效期为 1 小时）
      const expiresAt = Date.now() + 60 * 60 * 1000;
      localStorage.setItem(STORAGE_KEYS.TOKEN_EXPIRES, expiresAt.toString());

      // 通知等待的请求
      this._refreshQueue.forEach(resolve => resolve(true));
      this._refreshQueue = [];

      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // 通知等待的请求刷新失败
      this._refreshQueue.forEach(resolve => resolve(false));
      this._refreshQueue = [];
      return false;
    } finally {
      this._isRefreshing = false;
    }
  },

  get(url) {
    return this.request(url, { method: 'GET' });
  },

  post(url, data) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  put(url, data) {
    return this.request(url, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  delete(url) {
    return this.request(url, { method: 'DELETE' });
  }
};

/**
 * 认证管理
 */
const auth = {
  getToken() {
    return localStorage.getItem(STORAGE_KEYS.TOKEN);
  },
  
  getUser() {
    const userJson = localStorage.getItem(STORAGE_KEYS.USER);
    return userJson ? JSON.parse(userJson) : null;
  },
  
  setAuth(token, user, refreshToken = null) {
    localStorage.setItem(STORAGE_KEYS.TOKEN, token);
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    if (refreshToken) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
    }
    // 设置 Token 过期时间（假设有效期为 1 小时）
    const expiresAt = Date.now() + 60 * 60 * 1000;
    localStorage.setItem(STORAGE_KEYS.TOKEN_EXPIRES, expiresAt.toString());
  },

  logout() {
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
    localStorage.removeItem(STORAGE_KEYS.TOKEN_EXPIRES);
  },
  
  isAuthenticated() {
    return !!this.getToken();
  },
  
  hasRole(role) {
    const user = this.getUser();
    if (!user) return false;
    
    const roleHierarchy = {
      'user': 1,
      'developer': 2,
      'reviewer': 3,
      'admin': 4
    };
    
    return roleHierarchy[user.role] >= roleHierarchy[role];
  }
};

/**
 * 工具函数
 */
const utils = {
  /**
   * HTML 转义
   *
   * 插件名称、描述、manifest 字段等都来自开发者仓库里的 manifest.json，
   * 属于不可信输入。任何要拼进 innerHTML 的此类文本都必须先过这里。
   *
   * @param {*} value - 待转义的值
   * @returns {string} 转义后的字符串
   */
  escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  },

  /**
   * 校验并返回安全的链接地址
   *
   * 只放行 http/https，挡掉 javascript: / data: 等伪协议。
   *
   * @param {string} url - 原始地址
   * @param {string} fallback - 不合法时的回退值
   * @returns {string} 可安全放进 href 的地址（已转义）
   */
  safeUrl(url, fallback = '#') {
    if (!url) return fallback;
    try {
      const parsed = new URL(url, window.location.origin);
      if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
        return fallback;
      }
      return this.escapeHtml(parsed.href);
    } catch (e) {
      return fallback;
    }
  },

  /**
   * 校验并返回安全的图片地址
   *
   * 与 safeUrl 的区别：额外放行 data:image/*，因为
   * /api/avatar/proxy 返回的缓存头像就是 data URI。
   *
   * @param {string} url - 原始地址
   * @param {string} fallback - 不合法时的回退值
   * @returns {string} 可安全放进 img src 的地址（已转义）
   */
  safeImageSrc(url, fallback = '') {
    if (!url) return fallback;

    // data:image/xxx;base64,... —— 只允许图片类型，挡掉 data:text/html
    if (/^data:image\/(png|jpe?g|gif|webp|avif);base64,[a-z0-9+/=]+$/i.test(url)) {
      return this.escapeHtml(url);
    }

    return this.safeUrl(url, fallback);
  },

  /**
   * 渲染 Markdown 为安全的 HTML
   * 使用 marked 解析 + DOMPurify 净化
   *
   * 安全配置：
   * - 禁用危险标签（script, iframe, form 等）
   * - 禁用事件处理属性（onerror, onclick 等）
   * - 禁用 data-* 属性
   * - 限制 URL 协议（仅允许 http/https/mailto 等）
   *
   * README 来自任意 GitHub 仓库，Markdown 允许内嵌原始 HTML，
   * 不消毒直接 innerHTML 会造成存储型 XSS（审核员打开待审插件即中招）。
   *
   * @param {string} markdown - Markdown 源文本
   * @returns {string} 可安全插入 DOM 的 HTML
   */
  renderMarkdown(markdown) {
    if (!markdown) return '';

    // 依赖缺失时降级为纯文本，绝不回退到未消毒的 HTML
    if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') {
      console.error('marked / DOMPurify not loaded, falling back to plain text');
      return `<pre style="white-space: pre-wrap;">${this.escapeHtml(markdown)}</pre>`;
    }

    return DOMPurify.sanitize(marked.parse(markdown), {
      USE_PROFILES: { html: true },
      FORBID_TAGS: ['style', 'form', 'input', 'button', 'iframe', 'object', 'embed', 'script'],
      FORBID_ATTR: ['style', 'srcset', 'formaction', 'onerror', 'onload', 'onclick', 'onmouseover'],
      ADD_ATTR: ['target', 'rel'],
      ALLOW_DATA_ATTR: false,
      ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
    });
  },

  /**
   * 格式化日期
   */
  formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    const t = (key, params) => window.i18n && window.i18n.t ? window.i18n.t(key, params) : key;

    if (diffDays === 0) return t('date.today');
    if (diffDays === 1) return t('date.yesterday');
    if (diffDays < 7) return t('date.daysAgo').replace('{n}', diffDays);
    if (diffDays < 30) return t('date.weeksAgo').replace('{n}', Math.floor(diffDays / 7));
    return t('date.monthsAgo').replace('{n}', Math.floor(diffDays / 30));
  },
  
  /**
   * 格式化时间（精确到分钟）
   */
  formatTimeAgo(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    const t = (key, params) => window.i18n && window.i18n.t ? window.i18n.t(key, params) : key;
    const lang = window.i18n ? window.i18n.getCurrentLanguage() : 'zh-CN';

    if (diffMins < 1) return t('time.justNow');
    if (diffMins < 60) return t('time.minutesAgo').replace('{n}', diffMins);
    if (diffHours < 24) return t('time.hoursAgo').replace('{n}', diffHours);
    if (diffDays < 30) return t('time.daysAgo').replace('{n}', diffDays);
    return date.toLocaleDateString(lang === 'zh-CN' ? 'zh-CN' : 'en-US');
  },
  
  /**
   * 获取状态标签样式
   */
  getStatusBadge(status) {
    const t = (key, params) => window.i18n && window.i18n.t ? window.i18n.t(key, params) : key;
    const statusMap = {
      'pending': { text: t('status.pending'), class: 'badge-warning' },
      'approved': { text: t('status.approved'), class: 'badge-success' },
      'rejected': { text: t('status.rejected'), class: 'badge-error' },
      'removed': { text: t('status.removed'), class: 'badge-default' },
      'draft': { text: t('status.draft'), class: 'badge-default' }
    };
    return statusMap[status] || { text: status, class: 'badge-default' };
  },
  
  /**
   * 获取分类名称
   */
  getCategoryName(slug) {
    const t = (key, params) => window.i18n && window.i18n.t ? window.i18n.t(key, params) : key;
    const names = {
      'productivity': t('store.category.productivity'),
      'developer-tools': t('store.category.developerTools'),
      'design': t('store.category.design'),
      'communication': t('store.category.communication'),
      'utilities': t('store.category.utilities')
    };
    return names[slug] || slug;
  },
  
  /**
   * 防抖函数
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
  
  /**
   * 显示加载状态
   */
  showLoading(container, text = null) {
    const t = (key, params) => window.i18n && window.i18n.t ? window.i18n.t(key, params) : key;
    const loadingText = text || t('msg.loading');
    container.innerHTML = `
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">${loadingText}</p>
      </div>
    `;
  },
  
  /**
   * 显示错误状态
   */
  showError(container, message, onRetry) {
    const t = (key, params) => window.i18n && window.i18n.t ? window.i18n.t(key, params) : key;
    container.classList.remove('plugin-grid');
    container.classList.add('error-container');
    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <h3 class="empty-title">${t('msg.error')}</h3>
        <p class="empty-description">${message}</p>
        ${onRetry ? `<button class="btn btn-primary" onclick="${onRetry}">${t('btn.retry')}</button>` : ''}
      </div>
    `;
  },
  
  /**
   * 显示空状态
   */
  showEmpty(container, message) {
    const t = (key, params) => window.i18n && window.i18n.t ? window.i18n.t(key, params) : key;
    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
        </svg>
        <h3 class="empty-title">${t('msg.empty')}</h3>
        <p class="empty-description">${message}</p>
      </div>
    `;
  },

  /**
   * 获取头像 URL（使用代理缓存）
   * @param {string} originalUrl - 原始头像 URL
   * @param {string} fallbackName - 备用名称（用于生成默认头像）
   * @returns {string} 头像 URL
   */
  getAvatarUrl(originalUrl, fallbackName = '?') {
    if (!originalUrl) {
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(fallbackName)}&background=e5e7eb&color=6b7280&size=64`;
    }
    // 使用代理接口
    return `${API_BASE_URL}/avatar/proxy?url=${encodeURIComponent(originalUrl)}`;
  },

  /**
   * 批量获取头像 URL（使用代理缓存）
   * @param {string[]} urls - 原始头像 URL 数组
   * @returns {Promise<Object>} 缓存后的头像 URL 映射
   */
  async getAvatarUrlsBatch(urls) {
    const uniqueUrls = [...new Set(urls.filter(url => url))];
    if (uniqueUrls.length === 0) return {};

    try {
      const response = await fetch(`${API_BASE_URL}/avatar/proxy/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: uniqueUrls })
      });

      if (response.ok) {
        const data = await response.json();
        return data.results || {};
      }
    } catch (error) {
      console.error('Avatar batch fetch failed:', error);
    }

    // 失败时返回原始 URL
    const result = {};
    uniqueUrls.forEach(url => {
      result[url] = { url: url, cached: false };
    });
    return result;
  },

  /**
   * 创建带有缓存的头像图片元素 HTML
   * @param {string} src - 原始头像 URL
   * @param {string} alt - 图片 alt 文本
   * @param {string} className - CSS 类名
   * @param {Object} options - 其他选项
   * @returns {string} img 标签 HTML
   */
  createAvatarHtml(src, alt = '', className = '', options = {}) {
    const { width = 64, height = 64, fallbackName = alt || '?' } = options;
    const fallbackUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(fallbackName)}&background=e5e7eb&color=6b7280&size=${Math.max(width, height)}`;
    
    if (!src) {
      return `<img src="${fallbackUrl}" alt="${alt}" class="${className}" width="${width}" height="${height}">`;
    }

    // 使用代理 URL
    const proxyUrl = `${API_BASE_URL}/avatar/proxy?url=${encodeURIComponent(src)}`;
    
    return `<img src="${proxyUrl}" alt="${alt}" class="${className}" width="${width}" height="${height}" 
            onerror="this.onerror=null;this.src='${fallbackUrl}'">`;
  }
};

/**
 * 页面初始化
 */
document.addEventListener('DOMContentLoaded', () => {
  // 初始化国际化（如果 i18n.js 已加载）
  if (window.i18n) {
    window.i18n.init();
  }
  
  // 更新用户界面
  updateUserUI();
});

/**
 * 更新用户界面（显示登录状态）
 */
function updateUserUI() {
  const user = auth.getUser();
  const userContainers = document.querySelectorAll('.user-container');
  
  userContainers.forEach(container => {
    if (user) {
      // 根据角色构建导航按钮
      let navButtons = '<a href="developer.html" class="btn btn-ghost btn-sm">开发者中心</a>';
      
      // 审批者/管理员显示审批插件按钮
      if (user.role === 'reviewer' || user.role === 'admin') {
        navButtons += '<a href="review-plugins.html" class="btn btn-ghost btn-sm">审批插件</a>';
      }
      
      // 管理员显示管理层按钮
      if (user.role === 'admin') {
        navButtons += '<a href="admin.html" class="btn btn-ghost btn-sm">管理层</a>';
      }
      
      container.innerHTML = `
        <div class="flex items-center gap-2">
          ${navButtons}
          <img src="${utils.safeImageSrc(user.avatar, 'https://avatars.githubusercontent.com/u/0?v=4')}" alt="${utils.escapeHtml(user.username)}" class="w-5 h-5 rounded-full">
          <span class="text-sm">${utils.escapeHtml(user.username)}</span>
          <button class="btn btn-ghost btn-sm" onclick="auth.logout(); window.location.href='/'">退出</button>
        </div>
      `;
    } else {
      container.innerHTML = `
        <a href="/login.html" class="btn btn-primary btn-sm">登录</a>
      `;
    }
  });
}

// 导出全局变量
window.api = api;
window.auth = auth;
window.utils = utils;

/**
 * 主题管理
 */
const theme = {
  STORAGE_KEY: 'plugin_marketplace_theme',
  
  /**
   * 获取当前主题
   */
  getCurrentTheme() {
    return localStorage.getItem(this.STORAGE_KEY) || 'light';
  },
  
  /**
   * 设置主题
   */
  setTheme(themeName) {
    if (themeName === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem(this.STORAGE_KEY, themeName);
    this.updateToggleButton();
  },
  
  /**
   * 切换主题
   */
  toggle() {
    const currentTheme = this.getCurrentTheme();
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  },
  
  /**
   * 初始化主题
   */
  init() {
    const savedTheme = this.getCurrentTheme();
    this.setTheme(savedTheme);
    this.createToggleButton();
  },
  
  /**
   * 创建主题切换按钮
   */
  createToggleButton() {
    // 检查是否已存在
    if (document.querySelector('.theme-toggle')) return;
    
    const button = document.createElement('button');
    button.className = 'theme-toggle';
    button.setAttribute('aria-label', '切换主题');
    button.innerHTML = this.getIconSvg();
    button.addEventListener('click', () => this.toggle());
    document.body.appendChild(button);
  },
  
  /**
   * 更新切换按钮图标
   */
  updateToggleButton() {
    const button = document.querySelector('.theme-toggle');
    if (button) {
      button.innerHTML = this.getIconSvg();
    }
  },
  
  /**
   * 获取图标 SVG
   */
  getIconSvg() {
    const currentTheme = this.getCurrentTheme();
    if (currentTheme === 'dark') {
      // 月亮图标（当前是暗色模式，点击切换到亮色）
      return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
      </svg>`;
    } else {
      // 太阳图标（当前是亮色模式，点击切换到暗色）
      return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
      </svg>`;
    }
  }
};

// 初始化主题
document.addEventListener('DOMContentLoaded', () => {
  theme.init();
});

// 导出主题管理器
window.theme = theme;
