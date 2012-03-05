import os.path

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Moscow'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'

SITE_ID = 1

USE_I18N = True
USE_L10N = False

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = ''
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    "django.core.context_processors.static",
    'django.contrib.messages.context_processors.messages',

    'grakon.context_processors.user_data',
    'grakon.context_processors.grakon_media',
    'grakon.context_processors.uni_form_media',
    'users.context_processors.message_form',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'grakon.middleware.ProfileMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'loginza',
    'tinymce',
    'south',
    'uni_form',

    'grakon',
    'locations',
    'maintenance',
    'navigation',
    'registration',
    'reports',
    'users',
    'links',
    'organizations',
    'search',
    'violations',
    'protocols',
)

try:
    import captcha
    INSTALLED_APPS = INSTALLED_APPS + ('captcha',)
except ImportError:
    pass

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'registration.backend.EmailAuthenticationBackend',
    'loginza.authentication.LoginzaBackend',
)

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 120

AUTH_PROFILE_MODULE = 'grakon.Profile'
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/profile'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
CAPTCHA_FONT_SIZE = 20
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Loginza settings
LOGINZA_AMNESIA_PATHS = ('/registration_completed',)
LOGINZA_DEFAULT_EMAIL = ""

TINYMCE_JS_URL = STATIC_URL + 'libs/tiny_mce/tiny_mce.js'
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, 'libs', 'tiny_mce')
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'relative_urls': False,
    'width': '100%',
    'height': 300,
    'theme_advanced_buttons3': ",fontselect,fontsizeselect,forecolor,backcolor,|,sub,sup,|,charmap,",
    'extended_valid_elements': "script[type|src],iframe[src|style|width|height|scrolling|marginwidth|marginheight|frameborder],",
}
TINYMCE_COMPRESSOR = False # TODO: compression doesn't work at the moment

# force removal of mysite.fcgi from URL:
# http://docs.djangoproject.com/en/dev/howto/deployment/fastcgi/#forcing-the-url-prefix-to-a-particular-value
FORCE_SCRIPT_NAME = ''

from site_settings import *

#if DEBUG:
#    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
#    INSTALLED_APPS += ('debug_toolbar',)
#    INTERNAL_IPS = ('127.0.0.1',)
