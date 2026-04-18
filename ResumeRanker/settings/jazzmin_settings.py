JAZZMIN_SETTINGS = {

    # ========================
    # Branding
    # ========================
    "site_title": "ResumeRanker ATS",
    "site_header": "ATS Admin Dashboard",
    "site_brand": "ResumeRanker",
    "welcome_sign": "Welcome to ResumeRanker ATS Dashboard",

    # ========================
    # UI
    # ========================
    "show_sidebar": True,
    "navigation_expanded": True,
    "sidebar_fixed": True,
    "navbar_fixed": True,
    "footer_fixed": True,

    # ========================
    # Menu
    # ========================
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index"},
        {"name": "Frontend", "url": "http://localhost:5173", "new_window": True},
    ],

    "order_with_respect_to": [
        "user",
        "auth",
    ],

    # ========================
    # Icons (ATS Feel 🔥)
    # ========================
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",

        "user.User": "fas fa-user-tie",
        # "user.Resume": "fas fa-file-pdf",
        "user.Job": "fas fa-briefcase",
        "user.Application": "fas fa-paper-plane",
        "user.Score": "fas fa-chart-line",
    },

    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # ========================
    # Dashboard Cards
    # ========================
    "dashboard": {
        "widgets": [
            {
                "type": "small_box",
                "title": "Users",
                "icon": "fas fa-users",
                "color": "info",
            },
            {
                "type": "small_box",
                "title": "Resumes",
                "icon": "fas fa-file-alt",
                "color": "success",
            },
            {
                "type": "small_box",
                "title": "Jobs",
                "icon": "fas fa-briefcase",
                "color": "warning",
            },
            {
                "type": "small_box",
                "title": "Matches",
                "icon": "fas fa-robot",
                "color": "danger",
            },
        ]
    },

    # ========================
    # Forms UI
    # ========================
    "changeform_format": "horizontal_tabs",

    "changeform_format_overrides": {
        "user.User": "collapsible",
        # "user.Resume": "vertical_tabs",
    },

    # ========================
    # Search
    # ========================
    "search_model": ["user.User"],

    # ========================
    # Custom Styling
    # ========================
    "custom_css": "css/admin.css",
}