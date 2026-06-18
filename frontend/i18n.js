/**
 * KiraAI 插件商店 - 国际化 (i18n) 模块
 * 支持中英文双语切换
 */

// 翻译字典
const translations = {
  'zh-CN': {
    // 侧边栏
    'sidebar.devCenter': '开发者中心',
    'sidebar.dashboard': '仪表盘',
    'sidebar.myPlugins': '我的插件',
    'sidebar.submit': '提交插件',

    // 站点名称
    'site.name': 'KiraAI 插件商店',
    'site.tagline': '发现和安装优质的开源插件',
    
    // 导航
    'nav.browse': '浏览商店',
    'nav.browseStore': '浏览商店',
    'nav.login': '登录',
    'nav.logout': '退出',
    'nav.developer': '开发者中心',
    'nav.review': '审批插件',
    'nav.admin': '管理层',
    'nav.myPlugins': '我的插件',
    'nav.submit': '提交插件',
    'nav.dashboard': '仪表盘',
    'nav.browse_store': '浏览商店',
    
    // 首页
    'hero.title': '发现优质开源插件',
    'hero.subtitle': '基于 GitHub 的插件市场，严格审核，安全可靠。为开发者提供高质量的插件发现平台。',
    'hero.browseBtn': '浏览插件',
    'hero.publishBtn': '发布插件',
    'featured.title': '精选插件',
    'featured.badge': '{current} / {total}',
    'featured.viewAll': '查看全部',
    'creators.title': '活跃创作者',
    'creators.viewAll': '查看全部',
    'footer.thanks': '特别鸣谢',
    'footer.github': 'GitHub',
    'footer.contributors': '开源贡献者',
    'footer.community': '社区支持者',
    'footer.docs': '相关说明',
    'footer.terms': '服务条款',
    'footer.privacy': '隐私政策',
    'footer.contact': '联系我们',
    
    // 插件商店
    'store.title': 'KiraAI 插件商店',
    'store.searchPlaceholder': '搜索插件...',
    'store.sortBy': '排序:',
    'store.sort.stars': '最多 Stars',
    'store.sort.updated': '最近更新',
    'store.sort.name': '名称',
    'store.category': '分类:',
    'store.category.all': '全部分类',
    'store.category.productivity': '生产力',
    'store.category.developerTools': '开发工具',
    'store.category.design': '设计',
    'store.category.communication': '通讯',
    'store.category.utilities': '实用工具',
    'store.results.count': '共 {count} 个插件',
    'store.empty': '没有找到匹配的插件',
    'store.loadMore': '加载更多',
    'store.loading': '加载中...',
    
    // 插件卡片
    'plugin.by': 'by',
    'plugin.install': '安装',
    'plugin.detail': '详情',
    'plugin.github': 'GitHub',
    'plugin.stars': 'stars',
    'plugin.updated': '更新于',
    'plugin.version': '版本',
    
    // 插件详情
    'detail.title': '插件详情',
    'detail.back': '返回商店',
    'detail.overview': '概览',
    'detail.readme': 'README',
    'detail.releases': '版本发布',
    'detail.install': '安装',
    'detail.github': '查看源码',
    'detail.report': '举报',
    'detail.author.plugins': '个插件',
    'detail.tabs.overview': '概览',
    'detail.tabs.files': '文件',
    'detail.tabs.versions': '版本历史',
    'detail.lastUpdated': '最后更新',
    'detail.license': '许可证',
    'detail.loading': '加载插件详情...',
    'detail.noDescription': '暂无描述',
    'detail.uncategorized': '未分类',
    'detail.loadFailed': '加载失败',
    'detail.loadFailedDesc': '无法加载插件详情，请稍后重试',
    'detail.visitRepo': '访问仓库',
    'detail.download': '下载',
    'detail.stats.stars': 'Stars',
    'detail.stats.forks': 'Forks',
    'detail.stats.issues': 'Issues',
    'detail.stats.language': '语言',
    'detail.pluginInfo': '插件信息',
    'detail.manifest.display_name': '名称',
    'detail.manifest.version': '版本',
    'detail.manifest.author': '作者',
    'detail.emptyId': '插件ID不能为空',
    
    // 登录
    'login.title': '欢迎回来',
    'login.subtitle': '使用 GitHub 账号登录以继续',
    'login.githubBtn': '使用 GitHub 登录',
    'login.terms': '登录即表示您同意我们的服务条款',
    'login.noAccount': '还没有账号？',
    'login.register': '注册 GitHub 账号',
    'login.error': '登录失败，请重试',
    'login.error.accessDenied': '您拒绝了授权请求',
    'login.error.invalidRequest': '无效的请求参数',
    'login.error.invalidScope': '无效的权限范围',
    'login.error.authFailed': '认证失败，请重试',
    'login.error.tokenExchangeFailed': '无法获取访问令牌',
    'login.error.userFetchFailed': '无法获取用户信息',
    'login.error.default': '登录过程中发生错误，请重试',
    
    // 开发者中心
    'dev.title': '开发者仪表盘',
    'dev.center': '开发者中心',
    'dev.welcome': '欢迎回来！管理您的插件提交。',
    'dev.stats.total': '全部插件',
    'dev.stats.pending': '待审核',
    'dev.stats.approved': '已通过',
    'dev.stats.rejected': '已驳回',
    'dev.quickActions': '快捷操作',
    'dev.action.submit': '提交新插件',
    'dev.action.myPlugins': '我的插件',
    'dev.action.docs': '开发文档',
    'dev.recent': '最近提交',
    'dev.viewAll': '查看全部',
    'dev.submitted': '提交于',
    'dev.reviewed': '审核于',
    'dev.dashboard': '仪表盘',
    'dev.myPlugins': '我的插件',

    // 我的插件
    'myPlugins.title': '我的插件',
    'myPlugins.subtitle': '管理您提交的所有插件',
    'myPlugins.new': '提交新插件',
    'myPlugins.empty': '您还没有提交任何插件',
    'myPlugins.emptyAction': '立即提交第一个插件',
    'myPlugins.edit': '编辑',
    'myPlugins.delete': '删除',
    'myPlugins.withdraw': '撤回',
    'myPlugins.resubmit': '重新提交',
    'myPlugins.viewRepo': '查看仓库',
    'myPlugins.submittedAt': '提交于',
    'myPlugins.withdrawConfirm': '确定要撤回此插件吗？',
    'myPlugins.withdrawSuccess': '撤回成功',
    'myPlugins.withdrawError400': '只能撤回待审核的插件',
    'myPlugins.unpublishConfirm': '确定要下架插件 "{name}" 吗？下架后其他用户将无法安装。',
    'myPlugins.unpublishSuccess': '下架成功',
    'myPlugins.unpublishError400': '只能下架已通过的插件',

    // 提交插件
    'submit.title': '提交插件',
    'submit.editTitle': '编辑插件',
    'submit.subtitle': '提交您的插件到 KiraAI 插件商店',
    'submit.githubUrl': 'GitHub 仓库地址',
    'submit.githubUrlPlaceholder': 'https://github.com/username/repo',
    'submit.category': '插件分类',
    'submit.selectCategory': '请选择分类',
    'submit.description': '插件描述',
    'submit.descriptionPlaceholder': '简要描述您的插件功能和用途...',
    'submit.submitBtn': '提交审核',
    'submit.saveBtn': '保存修改',
    'submit.cancel': '取消',
    'submit.fetching': '正在获取仓库信息...',
    'submit.rules.title': '提交规范',
    'submit.rules.validRepo': 'GitHub 仓库必须可访问',
    'submit.rules.hasReadme': '仓库需要包含 README.md',
    'submit.rules.unique': '插件不能与已有插件重复',
    'submit.rules.safe': '插件内容需符合社区规范',
    'submit.validateBtn': '验证仓库',
    'submit.githubUrlHint': '请输入有效的 GitHub 仓库地址',
    'submit.tags': '标签',
    'submit.tagsPlaceholder': '输入标签，用逗号分隔',
    'submit.submitting': '提交中...',
    
    // 审批插件
    'review.title': '插件审批',
    'review.subtitle': '审核待审批的插件提交',
    'review.pending': '待审批',
    'review.reviewed': '已审批',
    'review.empty.pending': '暂无待审批的插件',
    'review.empty.reviewed': '暂无已审批记录',
    'review.approve': '通过',
    'review.reject': '驳回',
    'review.reason': '驳回原因',
    'review.reasonPlaceholder': '请输入驳回原因...',
    'review.history': '审批历史',
    'review.pendingPlugins': '待审批插件',
    'review.reviewHistory': '审批历史',
    'review.modalTitle': '审核插件',
    'review.rejectTitle': '驳回插件',
    'review.confirmReject': '确认驳回',
    'review.pendingStats': '待审批',
    'review.approvedStats': '已通过',
    'review.rejectedStats': '已驳回',
    'review.audit': '审核',
    
    // 管理后台
    'admin.title': '管理仪表盘',
    'admin.subtitle': '系统概览和管理入口',
    'admin.stats.plugins': '插件统计',
    'admin.stats.users': '用户统计',
    'admin.stats.pending': '待审批',
    'admin.stats.approved': '已通过',
    'admin.menu.plugins': '插件管理',
    'admin.menu.categories': '分类管理',
    'admin.menu.users': '用户管理',
    'admin.menu.reviewers': '审核员管理',
    'admin.menu.stats': '数据统计',
    'admin.managementCenter': '管理中心',
    'admin.welcome_back': '欢迎回来，{username}',
    'admin.no_activity': '暂无活动记录',
    'admin.sidebar.managementCenter': '管理中心',
    'admin.sidebar.dashboard': '仪表盘',
    'admin.sidebar.userManagement': '用户管理',
    'admin.sidebar.pluginManagement': '插件管理',
    'admin.sidebar.reviewerManagement': '审核员管理',
    'admin.sidebar.categoryManagement': '分类管理',
    'admin.sidebar.statistics': '数据统计',
    
    // 插件管理
    'adminPlugins.title': '插件管理',
    'adminPlugins.subtitle': '管理所有插件的审核状态',
    'adminPlugins.tab.all': '全部',
    'adminPlugins.tab.pending': '待审核',
    'adminPlugins.tab.approved': '已通过',
    'adminPlugins.tab.rejected': '已驳回',
    'adminPlugins.tab.removed': '已下架',
    'adminPlugins.search': '搜索插件...',
    'adminPlugins.filterStatus': '状态筛选',
    'adminPlugins.bulkActions': '批量操作',
    'adminPlugins.actions.approve': '批量通过',
    'adminPlugins.actions.reject': '批量驳回',
    'adminPlugins.actions.delete': '批量删除',
    'adminPlugins.search.label': '搜索',
    'adminPlugins.search.placeholder': '搜索插件...',
    'adminPlugins.pluginList.title': '插件列表',
    'adminPlugins.table.name': '插件名称',
    'adminPlugins.table.author': '作者',
    'adminPlugins.table.category': '分类',
    'adminPlugins.table.status': '状态',
    'adminPlugins.table.submitted': '提交时间',
    'adminPlugins.table.actions': '操作',
    'adminPlugins.actions.viewRepo': '查看仓库',
    'adminPlugins.actions.ban': '下架',
    'adminPlugins.confirmBan': '确定要下架此插件吗？',
    'adminPlugins.banSuccess': '下架成功',
    'adminPlugins.banFailed': '下架失败',
    'adminPlugins.stats.totalPlugins': '全部插件',
    'adminPlugins.stats.pendingReview': '待审核',
    
    // 用户管理
    'admin.users.title': '用户管理',
    'admin.users.subtitle': '管理系统用户和权限',
    
    // 分类管理
    'admin.categories.title': '分类管理',
    'admin.categories.subtitle': '管理插件分类',
    
    // 审核员管理
    'admin.reviewers.title': '审核员管理',
    'admin.reviewers.subtitle': '管理插件审核员',
    
    // 数据统计
    'admin.stats.title': '数据统计',
    'admin.stats.subtitle': '查看系统统计数据',
    
    // 状态标签
    'status.pending': '待审核',
    'status.approved': '已通过',
    'status.rejected': '已驳回',
    'status.removed': '已下架',
    'status.draft': '草稿',
    
    // 通用按钮
    'btn.save': '保存',
    'btn.cancel': '取消',
    'btn.confirm': '确认',
    'btn.delete': '删除',
    'btn.edit': '编辑',
    'btn.close': '关闭',
    'btn.retry': '重试',
    'btn.back': '返回',
    'btn.backToStore': '← 返回商店',
    'btn.next': '下一步',
    'btn.previous': '上一步',
    'btn.submit': '提交',
    'btn.search': '搜索',
    'btn.filter': '筛选',
    'btn.reset': '重置',
    'btn.view': '查看',
    'btn.more': '更多',
    
    // 提示信息
    'msg.loading': '加载中...',
    'msg.loadingPlugins': '加载插件中...',
    'msg.error': '出错了',
    'msg.error.load': '加载失败，请重试',
    'msg.error.action': '操作失败，请重试',
    'msg.empty': '暂无数据',
    'msg.empty.plugins': '暂无插件',
    'msg.empty.search': '没有找到匹配的插件',
    'msg.success.save': '保存成功',
    'msg.success.submit': '提交成功',
    'msg.success.delete': '删除成功',
    'msg.confirm.delete': '确定要删除吗？此操作不可撤销。',
    'msg.confirm.logout': '确定要退出登录吗？',
    
    // 语言切换
    'lang.switch': '切换语言',
    'lang.zh': '中文',
    'lang.en': 'English',
    
    // 分页
    'pagination.prev': '上一页',
    'pagination.next': '下一页',
    'pagination.page': '第 {page} 页',
    'pagination.total': '共 {total} 页',
    
    // 日期时间
    'date.today': '今天',
    'date.yesterday': '昨天',
    'date.daysAgo': '{n} 天前',
    'date.weeksAgo': '{n} 周前',
    'date.monthsAgo': '{n} 月前',
    'time.justNow': '刚刚',
    'time.minutesAgo': '{n} 分钟前',
    'time.hoursAgo': '{n} 小时前',
    'time.daysAgo': '{n} 天前',
    
    // 回调页面
    'callback.title': '授权回调',
    'callback.loading.title': '正在登录...',
    'callback.loading.processing': '正在处理 GitHub 授权',
    'callback.error.title': '登录失败',
    'callback.error.defaultMessage': '授权过程中发生错误',
    'callback.error.backToLogin': '返回登录页',
    'callback.error.githubDenied': 'GitHub 授权被拒绝: {error}',
    'callback.error.noAuthCode': '未收到授权码',
    'callback.error.loginFailed': '登录失败',
    'callback.error.genericError': '登录过程中发生错误',
    
    // 贡献者页面
    'contributors.title': '开源贡献者',
    'contributors.subtitle': '感谢所有为 KiraAI 插件生态做出贡献的开发者',
    'contributors.totalDevelopers': '贡献者',
    'contributors.totalPlugins': '插件',
    'contributors.totalStars': 'Stars',
    'contributors.empty': '还没有开发者贡献插件',
    'contributors.viewPlugins': '查看插件',

    // 角色
    'roles.user': '用户',
    'roles.developer': '开发者',
    'roles.reviewer': '审核员',
    'roles.admin': '管理员',
    
    // 作者页面
    'author.title': '作者主页',
    'author.plugins': '个插件',
    'author.backToStore': '返回商店',
    'author.publishedPlugins': '发布的插件',
    'author.noPlugins': '该作者暂无插件',
    'author.loadError': '加载作者信息失败',

    // 活动相关
    'activity.plugin_submit': '提交插件',
    'activity.desc_submit': '提交了新插件',
    'activity.plugin_approve': '通过插件',
    'activity.desc_approve': '通过了插件审核',
    'activity.plugin_reject': '驳回插件',
    'activity.desc_reject': '驳回了插件',
    'activity.plugin_ban': '下架插件',
    'activity.desc_ban': '下架了插件',
    'activity.role_assign': '分配角色',
    'activity.desc_assign_role': '分配了角色',
    'activity.role_revoke': '撤销角色',
    'activity.desc_revoke_role': '撤销了角色',
    'activity.operation': '操作',
    'activity.desc_default': '执行了操作',

    // Admin 相关
    'admin.management_center': '管理中心',
    'admin.dashboard': '仪表盘',
    'admin.user_management': '用户管理',
    'admin.plugin_management': '插件管理',
    'admin.reviewer_management': '审核员管理',
    'admin.category_management': '分类管理',
    'admin.statistics': '数据统计',
    'admin.quick_actions': '快捷操作',
    'admin.recent_activity': '最近活动',
    'admin.no_activity': '暂无活动',
    'admin.welcome_back': '欢迎回来',
    'admin.stats.total_plugins': '全部插件',
    'admin.stats.total_users': '全部用户',
    'admin.stats.pending': '待审核',
    'admin.stats.approved': '已通过',

    // Review 相关
    'review.noPermission': '没有权限',
    'review.emptyPendingTitle': '暂无待审批插件',
    'review.emptyPendingDesc': '当前没有需要审批的插件',
    'review.pendingBadge': '待审批',
    'review.emptyHistoryTitle': '暂无审批历史',
    'review.emptyHistoryDesc': '还没有审批记录',
    'review.review': '审批',
    'review.pluginName': '插件名称',
    'review.action': '操作',
    'review.comment': '评论',
    'review.reviewTime': '审批时间',
    'review.approved': '已通过',
    'review.rejected': '已驳回',
    'review.confirmApprove': '确认通过此插件吗？',
    'review.approvedSuccess': '已通过审核',
    'review.statusChanged': '状态已更改',
    'review.enterReason': '请输入原因',
    'review.rejectedSuccess': '已驳回',
    'review.loadDetailError': '加载详情失败',
    'review.repoInfo': '仓库信息',
    'review.repoUrl': '仓库地址',
    'review.info': '信息',
    'review.githubData': 'GitHub 数据',
    'review.reasonHelp': '请输入审批意见或驳回原因',

    // Submit 相关
    'submit.rulesTitle': '提交规范',
    'submit.rule1': 'GitHub 仓库必须可访问',
    'submit.rule2': '仓库需要包含 README.md',
    'submit.rule3': '插件不能与已有插件重复',
    'submit.rule4': '插件内容需符合社区规范',
    'submit.errorNoUrl': '请输入 GitHub 仓库地址',
    'submit.validationFailed': '验证失败',
    'submit.validationError': '验证出错',
    'submit.errorValidateFirst': '请先验证仓库',
    'submit.errorSelectCategory': '请选择分类',
    'submit.submitting': '提交中...',
    'submit.submitFailed': '提交失败',
    'submit.noDescription': '暂无描述',

    // Footer 相关
    'footer.acknowledgments': '特别鸣谢',
    'footer.legal': '法律信息',
    'footer.contact': '联系我们',
    'footer.email': '电子邮箱',
    'footer.feedback': '意见反馈',
    'footer.joinUs': '加入我们',
    'footer.join': '加入',
    'footer.disclaimer': '免责声明',
    'footer.notices': '注意事项',
    'footer.copyright': '版权所有',
    'footer.description': 'KiraAI 插件商店 - 发现和安装优质的开源插件',
    'footer.notice': '声明',
    'footer.supporters': '支持者',

    // Store 分类相关
    'store.category.utility': '实用工具',
    'store.category.efficiency': '效率工具',
    'store.category.entertainment': '娱乐',
    'store.category.developer': '开发者工具',
    'store.category.ai': 'AI 工具',

    // Plugin 相关
    'plugin.submitted': '已提交',
    'plugin.noDescription': '暂无描述',
    'plugin.author': '作者',
    'plugin.category': '分类',
    'plugin.viewRepo': '查看仓库',

    // Action 相关
    'action.viewRepo': '查看仓库',
    'action.withdraw': '撤回',
    'action.unpublish': '下架',

    // 导航
    'nav.browse_store': '浏览商店',

    // 通用
    'common.loading': '加载中...',
    'common.loadError': '加载失败',
    'common.actionError': '操作失败',
    'common.cancel': '取消',
    'common.languageSwitch': '切换语言',
  },
  
  'en': {
    // Sidebar
    'sidebar.devCenter': 'Developer Center',
    'sidebar.dashboard': 'Dashboard',
    'sidebar.myPlugins': 'My Plugins',
    'sidebar.submit': 'Submit Plugin',

    // Site Name
    'site.name': 'KiraAI Plugins',
    'site.tagline': 'Discover and install quality open-source plugins',
    
    // Navigation
    'nav.browse': 'Browse Store',
    'nav.browseStore': 'Browse Store',
    'nav.login': 'Login',
    'nav.logout': 'Logout',
    'nav.developer': 'Developer Center',
    'nav.review': 'Review Plugins',
    'nav.admin': 'Admin',
    'nav.myPlugins': 'My Plugins',
    'nav.submit': 'Submit Plugin',
    'nav.dashboard': 'Dashboard',
    'nav.browse_store': 'Browse Store',
    
    // Home
    'hero.title': 'Discover Quality Open Source Plugins',
    'hero.subtitle': 'GitHub-based plugin marketplace with strict review process. A high-quality plugin discovery platform for developers.',
    'hero.browseBtn': 'Browse Plugins',
    'hero.publishBtn': 'Publish Plugin',
    'featured.title': 'Featured Plugins',
    'featured.badge': '{current} / {total}',
    'featured.viewAll': 'View All',
    'creators.title': 'Active Creators',
    'creators.viewAll': 'View All',
    'footer.thanks': 'Special Thanks',
    'footer.github': 'GitHub',
    'footer.contributors': 'Open Source Contributors',
    'footer.community': 'Community Supporters',
    'footer.docs': 'Documentation',
    'footer.terms': 'Terms of Service',
    'footer.privacy': 'Privacy Policy',
    'footer.contact': 'Contact Us',
    
    // Plugin Store
    'store.title': 'KiraAI Plugins',
    'store.searchPlaceholder': 'Search plugins...',
    'store.sortBy': 'Sort by:',
    'store.sort.stars': 'Most Stars',
    'store.sort.updated': 'Recently Updated',
    'store.sort.name': 'Name',
    'store.category': 'Category:',
    'store.category.all': 'All Categories',
    'store.category.productivity': 'Productivity',
    'store.category.developerTools': 'Developer Tools',
    'store.category.design': 'Design',
    'store.category.communication': 'Communication',
    'store.category.utilities': 'Utilities',
    'store.results.count': '{count} plugins found',
    'store.empty': 'No matching plugins found',
    'store.loadMore': 'Load More',
    'store.loading': 'Loading...',
    
    // Plugin Card
    'plugin.by': 'by',
    'plugin.install': 'Install',
    'plugin.detail': 'Details',
    'plugin.github': 'GitHub',
    'plugin.stars': 'stars',
    'plugin.updated': 'updated',
    'plugin.version': 'version',
    
    // Plugin Detail
    'detail.title': 'Plugin Details',
    'detail.back': 'Back to Store',
    'detail.overview': 'Overview',
    'detail.readme': 'README',
    'detail.releases': 'Releases',
    'detail.install': 'Install',
    'detail.github': 'View Source',
    'detail.report': 'Report',
    'detail.author.plugins': 'plugins',
    'detail.tabs.overview': 'Overview',
    'detail.tabs.files': 'Files',
    'detail.tabs.versions': 'Version History',
    'detail.lastUpdated': 'Last Updated',
    'detail.license': 'License',
    'detail.loading': 'Loading plugin details...',
    'detail.noDescription': 'No description',
    'detail.uncategorized': 'Uncategorized',
    'detail.loadFailed': 'Load Failed',
    'detail.loadFailedDesc': 'Failed to load plugin details, please try again later',
    'detail.visitRepo': 'Visit Repository',
    'detail.download': 'Download',
    'detail.stats.stars': 'Stars',
    'detail.stats.forks': 'Forks',
    'detail.stats.issues': 'Issues',
    'detail.stats.language': 'Language',
    'detail.pluginInfo': 'Plugin Info',
    'detail.manifest.display_name': 'Name',
    'detail.manifest.version': 'Version',
    'detail.manifest.author': 'Author',
    'detail.emptyId': 'Plugin ID cannot be empty',
    
    // 登录
    'login.title': 'Welcome Back',
    'login.subtitle': 'Sign in with your GitHub account to continue',
    'login.githubBtn': 'Sign in with GitHub',
    'login.terms': 'By signing in, you agree to our Terms of Service',
    'login.noAccount': "Don't have an account?",
    'login.register': 'Sign up for GitHub',
    'login.error': 'Login failed, please try again',
    'login.error.accessDenied': 'You denied the authorization request',
    'login.error.invalidRequest': 'Invalid request parameters',
    'login.error.invalidScope': 'Invalid scope',
    'login.error.authFailed': 'Authentication failed, please try again',
    'login.error.tokenExchangeFailed': 'Failed to get access token',
    'login.error.userFetchFailed': 'Failed to get user information',
    'login.error.default': 'An error occurred during login, please try again',
    
    // Developer Center
    'dev.title': 'Developer Dashboard',
    'dev.center': 'Developer Center',
    'dev.welcome': 'Welcome back! Manage your plugin submissions.',
    'dev.stats.total': 'Total Plugins',
    'dev.stats.pending': 'Pending',
    'dev.stats.approved': 'Approved',
    'dev.stats.rejected': 'Rejected',
    'dev.quickActions': 'Quick Actions',
    'dev.action.submit': 'Submit New Plugin',
    'dev.action.myPlugins': 'My Plugins',
    'dev.action.docs': 'Documentation',
    'dev.recent': 'Recent Submissions',
    'dev.viewAll': 'View All',
    'dev.submitted': 'Submitted at',
    'dev.reviewed': 'Reviewed at',
    'dev.dashboard': 'Dashboard',
    'dev.myPlugins': 'My Plugins',

    // My Plugins
    'myPlugins.title': 'My Plugins',
    'myPlugins.subtitle': 'Manage all your submitted plugins',
    'myPlugins.new': 'Submit New Plugin',
    'myPlugins.empty': "You haven't submitted any plugins yet",
    'myPlugins.emptyAction': 'Submit your first plugin now',
    'myPlugins.edit': 'Edit',
    'myPlugins.delete': 'Delete',
    'myPlugins.withdraw': 'Withdraw',
    'myPlugins.resubmit': 'Resubmit',
    'myPlugins.viewRepo': 'View Repository',
    'myPlugins.submittedAt': 'Submitted at',
    'myPlugins.withdrawConfirm': 'Are you sure you want to withdraw this plugin?',
    'myPlugins.withdrawSuccess': 'Withdrawn successfully',
    'myPlugins.withdrawError400': 'Can only withdraw pending plugins',
    'myPlugins.unpublishConfirm': 'Are you sure you want to unpublish "{name}"? Other users will no longer be able to install it.',
    'myPlugins.unpublishSuccess': 'Unpublished successfully',
    'myPlugins.unpublishError400': 'Can only unpublish approved plugins',

    // Submit Plugin
    'submit.title': 'Submit Plugin',
    'submit.editTitle': 'Edit Plugin',
    'submit.subtitle': 'Submit your plugin to KiraAI Plugins Store',
    'submit.githubUrl': 'GitHub Repository URL',
    'submit.githubUrlPlaceholder': 'https://github.com/username/repo',
    'submit.category': 'Plugin Category',
    'submit.selectCategory': 'Please select a category',
    'submit.description': 'Plugin Description',
    'submit.descriptionPlaceholder': 'Briefly describe your plugin functionality and purpose...',
    'submit.submitBtn': 'Submit for Review',
    'submit.saveBtn': 'Save Changes',
    'submit.cancel': 'Cancel',
    'submit.fetching': 'Fetching repository info...',
    'submit.rules.title': 'Submission Guidelines',
    'submit.rules.validRepo': 'GitHub repository must be accessible',
    'submit.rules.hasReadme': 'Repository must include README.md',
    'submit.rules.unique': 'Plugin must not duplicate existing plugins',
    'submit.rules.safe': 'Plugin content must comply with community guidelines',
    'submit.validateBtn': 'Validate Repository',
    'submit.githubUrlHint': 'Please enter a valid GitHub repository URL',
    'submit.tags': 'Tags',
    'submit.tagsPlaceholder': 'Enter tags, separated by commas',
    'submit.submitting': 'Submitting...',
    
    // Review Plugins
    'review.title': 'Plugin Review',
    'review.subtitle': 'Review pending plugin submissions',
    'review.pending': 'Pending Review',
    'review.reviewed': 'Reviewed',
    'review.empty.pending': 'No plugins pending review',
    'review.empty.reviewed': 'No review history yet',
    'review.approve': 'Approve',
    'review.reject': 'Reject',
    'review.reason': 'Rejection Reason',
    'review.reasonPlaceholder': 'Please enter rejection reason...',
    'review.history': 'Review History',
    'review.pendingPlugins': 'Pending Plugins',
    'review.reviewHistory': 'Review History',
    'review.modalTitle': 'Review Plugin',
    'review.rejectTitle': 'Reject Plugin',
    'review.confirmReject': 'Confirm Rejection',
    'review.pendingStats': 'Pending',
    'review.approvedStats': 'Approved',
    'review.rejectedStats': 'Rejected',
    'review.audit': 'Review',
    
    // Admin Dashboard
    'admin.title': 'Admin Dashboard',
    'admin.subtitle': 'System overview and management access',
    'admin.stats.plugins': 'Plugin Statistics',
    'admin.stats.users': 'User Statistics',
    'admin.stats.pending': 'Pending Review',
    'admin.stats.approved': 'Approved',
    'admin.menu.plugins': 'Plugin Management',
    'admin.menu.categories': 'Category Management',
    'admin.menu.users': 'User Management',
    'admin.menu.reviewers': 'Reviewer Management',
    'admin.menu.stats': 'Statistics',
    'admin.managementCenter': 'Management Center',
    'admin.welcome_back': 'Welcome back, {username}',
    'admin.no_activity': 'No activity records',
    'admin.sidebar.managementCenter': 'Management Center',
    'admin.sidebar.dashboard': 'Dashboard',
    'admin.sidebar.userManagement': 'User Management',
    'admin.sidebar.pluginManagement': 'Plugin Management',
    'admin.sidebar.reviewerManagement': 'Reviewer Management',
    'admin.sidebar.categoryManagement': 'Category Management',
    'admin.sidebar.statistics': 'Statistics',
    
    // Plugin Management
    'adminPlugins.title': 'Plugin Management',
    'adminPlugins.subtitle': 'Manage review status for all plugins',
    'adminPlugins.tab.all': 'All',
    'adminPlugins.tab.pending': 'Pending',
    'adminPlugins.tab.approved': 'Approved',
    'adminPlugins.tab.rejected': 'Rejected',
    'adminPlugins.tab.removed': 'Removed',
    'adminPlugins.search': 'Search plugins...',
    'adminPlugins.filterStatus': 'Filter by Status',
    'adminPlugins.bulkActions': 'Bulk Actions',
    'adminPlugins.actions.approve': 'Bulk Approve',
    'adminPlugins.actions.reject': 'Bulk Reject',
    'adminPlugins.actions.delete': 'Bulk Delete',
    'adminPlugins.search.label': 'Search',
    'adminPlugins.search.placeholder': 'Search plugins...',
    'adminPlugins.pluginList.title': 'Plugin List',
    'adminPlugins.table.name': 'Plugin Name',
    'adminPlugins.table.author': 'Author',
    'adminPlugins.table.category': 'Category',
    'adminPlugins.table.status': 'Status',
    'adminPlugins.table.submitted': 'Submitted',
    'adminPlugins.table.actions': 'Actions',
    'adminPlugins.actions.viewRepo': 'View Repository',
    'adminPlugins.actions.ban': 'Remove',
    'adminPlugins.confirmBan': 'Are you sure you want to remove this plugin?',
    'adminPlugins.banSuccess': 'Removed successfully',
    'adminPlugins.banFailed': 'Failed to remove',
    'adminPlugins.stats.totalPlugins': 'Total Plugins',
    'adminPlugins.stats.pendingReview': 'Pending Review',
    
    // User Management
    'admin.users.title': 'User Management',
    'admin.users.subtitle': 'Manage system users and permissions',
    
    // Category Management
    'admin.categories.title': 'Category Management',
    'admin.categories.subtitle': 'Manage plugin categories',
    
    // Reviewer Management
    'admin.reviewers.title': 'Reviewer Management',
    'admin.reviewers.subtitle': 'Manage plugin reviewers',
    
    // Statistics
    'admin.stats.title': 'Statistics',
    'admin.stats.subtitle': 'View system statistics',
    
    // Status Labels
    'status.pending': 'Pending',
    'status.approved': 'Approved',
    'status.rejected': 'Rejected',
    'status.removed': 'Removed',
    'status.draft': 'Draft',
    
    // Common Buttons
    'btn.save': 'Save',
    'btn.cancel': 'Cancel',
    'btn.confirm': 'Confirm',
    'btn.delete': 'Delete',
    'btn.edit': 'Edit',
    'btn.close': 'Close',
    'btn.retry': 'Retry',
    'btn.back': 'Back',
    'btn.backToStore': '← Back to Store',
    'btn.next': 'Next',
    'btn.previous': 'Previous',
    'btn.submit': 'Submit',
    'btn.search': 'Search',
    'btn.filter': 'Filter',
    'btn.reset': 'Reset',
    'btn.view': 'View',
    'btn.more': 'More',
    
    // Messages
    'msg.loading': 'Loading...',
    'msg.loadingPlugins': 'Loading plugins...',
    'msg.error': 'Error',
    'msg.error.load': 'Failed to load, please try again',
    'msg.error.action': 'Action failed, please try again',
    'msg.empty': 'No data',
    'msg.empty.plugins': 'No plugins yet',
    'msg.empty.search': 'No matching plugins found',
    'msg.success.save': 'Saved successfully',
    'msg.success.submit': 'Submitted successfully',
    'msg.success.delete': 'Deleted successfully',
    'msg.confirm.delete': 'Are you sure you want to delete? This action cannot be undone.',
    'msg.confirm.logout': 'Are you sure you want to logout?',
    
    // Language Switch
    'lang.switch': 'Switch Language',
    'lang.zh': '中文',
    'lang.en': 'English',
    
    // Pagination
    'pagination.prev': 'Previous',
    'pagination.next': 'Next',
    'pagination.page': 'Page {page}',
    'pagination.total': 'of {total}',
    
    // Date & Time
    'date.today': 'Today',
    'date.yesterday': 'Yesterday',
    'date.daysAgo': '{n} days ago',
    'date.weeksAgo': '{n} weeks ago',
    'date.monthsAgo': '{n} months ago',
    'time.justNow': 'Just now',
    'time.minutesAgo': '{n} minutes ago',
    'time.hoursAgo': '{n} hours ago',
    'time.daysAgo': '{n} days ago',
    
    // Callback Page
    'callback.title': 'Authorization Callback',
    'callback.loading.title': 'Signing in...',
    'callback.loading.processing': 'Processing GitHub authorization',
    'callback.error.title': 'Login Failed',
    'callback.error.defaultMessage': 'An error occurred during authorization',
    'callback.error.backToLogin': 'Back to Login',
    'callback.error.githubDenied': 'GitHub authorization denied: {error}',
    'callback.error.noAuthCode': 'No authorization code received',
    'callback.error.loginFailed': 'Login failed',
    'callback.error.genericError': 'An error occurred during login',
    
    // Contributors Page
    'contributors.title': 'Open Source Contributors',
    'contributors.subtitle': 'Thanks to all developers who contributed to the KiraAI plugin ecosystem',
    'contributors.totalDevelopers': 'Contributors',
    'contributors.totalPlugins': 'Plugins',
    'contributors.totalStars': 'Stars',
    'contributors.empty': 'No developers have contributed plugins yet',
    'contributors.viewPlugins': 'View Plugins',

    // Roles
    'roles.user': 'User',
    'roles.developer': 'Developer',
    'roles.reviewer': 'Reviewer',
    'roles.admin': 'Admin',
    
    // Author Page
    'author.title': 'Author Profile',
    'author.plugins': 'plugins',
    'author.backToStore': 'Back to Store',
    'author.publishedPlugins': 'Published Plugins',
    'author.noPlugins': 'This author has no plugins yet',
    'author.loadError': 'Failed to load author information',

    // Activity
    'activity.plugin_submit': 'Submit Plugin',
    'activity.desc_submit': 'submitted a new plugin',
    'activity.plugin_approve': 'Approve Plugin',
    'activity.desc_approve': 'approved the plugin',
    'activity.plugin_reject': 'Reject Plugin',
    'activity.desc_reject': 'rejected the plugin',
    'activity.plugin_ban': 'Ban Plugin',
    'activity.desc_ban': 'banned the plugin',
    'activity.role_assign': 'Assign Role',
    'activity.desc_assign_role': 'assigned a role',
    'activity.role_revoke': 'Revoke Role',
    'activity.desc_revoke_role': 'revoked a role',
    'activity.operation': 'Operation',
    'activity.desc_default': 'performed an operation',

    // Admin
    'admin.management_center': 'Management Center',
    'admin.dashboard': 'Dashboard',
    'admin.user_management': 'User Management',
    'admin.plugin_management': 'Plugin Management',
    'admin.reviewer_management': 'Reviewer Management',
    'admin.category_management': 'Category Management',
    'admin.statistics': 'Statistics',
    'admin.quick_actions': 'Quick Actions',
    'admin.recent_activity': 'Recent Activity',
    'admin.no_activity': 'No activity',
    'admin.welcome_back': 'Welcome back',
    'admin.stats.total_plugins': 'Total Plugins',
    'admin.stats.total_users': 'Total Users',
    'admin.stats.pending': 'Pending',
    'admin.stats.approved': 'Approved',

    // Review
    'review.noPermission': 'No Permission',
    'review.emptyPendingTitle': 'No Pending Plugins',
    'review.emptyPendingDesc': 'There are no plugins pending review',
    'review.pendingBadge': 'Pending',
    'review.emptyHistoryTitle': 'No Review History',
    'review.emptyHistoryDesc': 'No review records yet',
    'review.review': 'Review',
    'review.pluginName': 'Plugin Name',
    'review.action': 'Action',
    'review.comment': 'Comment',
    'review.reviewTime': 'Review Time',
    'review.approved': 'Approved',
    'review.rejected': 'Rejected',
    'review.confirmApprove': 'Are you sure you want to approve this plugin?',
    'review.approvedSuccess': 'Approved successfully',
    'review.statusChanged': 'Status changed',
    'review.enterReason': 'Please enter reason',
    'review.rejectedSuccess': 'Rejected successfully',
    'review.loadDetailError': 'Failed to load details',
    'review.repoInfo': 'Repository Info',
    'review.repoUrl': 'Repository URL',
    'review.info': 'Info',
    'review.githubData': 'GitHub Data',
    'review.reasonHelp': 'Please enter review comment or rejection reason',

    // Submit
    'submit.rulesTitle': 'Submission Guidelines',
    'submit.rule1': 'GitHub repository must be accessible',
    'submit.rule2': 'Repository must include README.md',
    'submit.rule3': 'Plugin must not duplicate existing plugins',
    'submit.rule4': 'Plugin content must comply with community guidelines',
    'submit.errorNoUrl': 'Please enter GitHub repository URL',
    'submit.validationFailed': 'Validation failed',
    'submit.validationError': 'Validation error',
    'submit.errorValidateFirst': 'Please validate repository first',
    'submit.errorSelectCategory': 'Please select a category',
    'submit.submitting': 'Submitting...',
    'submit.submitFailed': 'Submission failed',
    'submit.noDescription': 'No description',

    // Footer
    'footer.acknowledgments': 'Acknowledgments',
    'footer.legal': 'Legal',
    'footer.contact': 'Contact Us',
    'footer.email': 'Email',
    'footer.feedback': 'Feedback',
    'footer.joinUs': 'Join Us',
    'footer.join': 'Join',
    'footer.disclaimer': 'Disclaimer',
    'footer.notices': 'Notices',
    'footer.copyright': 'Copyright',
    'footer.description': 'KiraAI Plugins - Discover and install quality open-source plugins',
    'footer.notice': 'Notice',
    'footer.supporters': 'Supporters',

    // Store Categories
    'store.category.utility': 'Utility',
    'store.category.efficiency': 'Efficiency',
    'store.category.entertainment': 'Entertainment',
    'store.category.developer': 'Developer Tools',
    'store.category.ai': 'AI Tools',

    // Plugin
    'plugin.submitted': 'Submitted',
    'plugin.noDescription': 'No description',
    'plugin.author': 'Author',
    'plugin.category': 'Category',
    'plugin.viewRepo': 'View Repository',

    // Action
    'action.viewRepo': 'View Repository',
    'action.withdraw': 'Withdraw',
    'action.unpublish': 'Unpublish',

    // Navigation
    'nav.browse_store': 'Browse Store',

    // Common
    'common.loading': 'Loading...',
    'common.loadError': 'Load failed',
    'common.actionError': 'Action failed',
    'common.cancel': 'Cancel',
    'common.languageSwitch': 'Switch Language',
  }
};

/**
 * i18n 管理器
 */
const i18n = {
  currentLang: 'zh-CN',
  STORAGE_KEY: 'kiraai_language',
  
  /**
   * 初始化
   */
  init() {
    // 从 localStorage 读取语言设置
    const savedLang = localStorage.getItem(this.STORAGE_KEY);
    // 检测浏览器语言
    const browserLang = navigator.language.startsWith('zh') ? 'zh-CN' : 'en';
    // 使用保存的语言或浏览器语言
    this.currentLang = savedLang || browserLang;
    
    // 应用语言
    this.applyLanguage();
    
    // 监听语言切换按钮
    this._initLangSwitch();
  },
  
  /**
   * 设置语言
   */
  setLanguage(lang) {
    if (!translations[lang]) return;
    
    this.currentLang = lang;
    localStorage.setItem(this.STORAGE_KEY, lang);
    
    // 更新 html lang 属性
    document.documentElement.lang = lang === 'zh-CN' ? 'zh-CN' : 'en';
    
    // 应用翻译
    this.applyLanguage();
    
    // 更新语言切换按钮显示
    this._updateLangSwitchButton();
  },
  
  /**
   * 切换语言
   */
  toggleLanguage() {
    const newLang = this.currentLang === 'zh-CN' ? 'en' : 'zh-CN';
    this.setLanguage(newLang);
  },
  
  /**
   * 获取翻译文本
   */
  t(key, params = {}) {
    let text = translations[this.currentLang]?.[key] || translations['en']?.[key] || key;
    
    // 替换参数
    Object.keys(params).forEach(param => {
      text = text.replace(new RegExp(`{${param}}`, 'g'), params[param]);
    });
    
    return text;
  },
  
  /**
   * 应用翻译到 DOM
   */
  applyLanguage() {
    // 翻译所有带有 data-i18n 属性的元素
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (key) {
        // 检查是否有 data-i18n-params 属性
        const paramsAttr = el.getAttribute('data-i18n-params');
        let params = {};
        if (paramsAttr) {
          try {
            params = JSON.parse(paramsAttr);
          } catch (e) {
            // 如果解析失败，尝试简单替换
            const match = paramsAttr.match(/\{count:(\d+)\}/);
            if (match) {
              params = { count: match[1] };
            }
          }
        }
        el.textContent = this.t(key, params);
      }
    });
    
    // 翻译带有 data-i18n-placeholder 的输入框
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (key) {
        el.placeholder = this.t(key);
      }
    });
    
    // 更新页面标题
    const titleEl = document.querySelector('title[data-i18n-title]');
    if (titleEl) {
      const key = titleEl.getAttribute('data-i18n-title');
      if (key) {
        titleEl.textContent = this.t(key);
      }
    }
    
    // 触发语言变更事件，供其他脚本监听
    window.dispatchEvent(new CustomEvent('languagechange', { 
      detail: { language: this.currentLang } 
    }));
  },
  
  /**
   * 获取当前语言
   */
  getCurrentLanguage() {
    return this.currentLang;
  },
  
  /**
   * 初始化语言切换按钮
   */
  _initLangSwitch() {
    // 查找或创建语言切换按钮
    let langSwitch = document.querySelector('.lang-switch');
    if (!langSwitch) {
      // 如果页面中没有预置的按钮，创建一个
      const navLinks = document.querySelector('.nav-links');
      if (navLinks) {
        langSwitch = document.createElement('button');
        langSwitch.className = 'lang-switch';
        langSwitch.setAttribute('title', this.t('lang.switch'));
        langSwitch.onclick = () => this.toggleLanguage();
        navLinks.appendChild(langSwitch);
      }
    }
    
    if (langSwitch) {
      this._updateLangSwitchButton();
    }
  },
  
  /**
   * 更新语言切换按钮显示
   */
  _updateLangSwitchButton() {
    const langSwitch = document.querySelector('.lang-switch');
    if (langSwitch) {
      const displayText = this.currentLang === 'zh-CN' ? '中/EN' : 'EN/中';
      langSwitch.innerHTML = `<span class="lang-current">${displayText}</span>`;
      langSwitch.setAttribute('title', this.t('lang.switch'));
    }
  }
};

// 导出到全局
window.i18n = i18n;
