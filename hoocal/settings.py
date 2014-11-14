"""
Django settings for hoocal project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wi@)*nm#o$&wni+nvk5!n1nd=%t)s@kkwjt_(&ehp3+dc=h*i3'

# SECURITY WARNING: don't run with debug turned on in production!
if os.environ['HEROKU_ENV'] == 'TRUE':
    DEBUG = False
else:
    DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (BASE_DIR+"/../test/templates/",)

ALLOWED_HOSTS = []

#https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-user
AUTH_USER_MODEL = 'hocalen.User'


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hocalen',
    'tastypie',
    'south',
)



MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'hoocal.urls'

WSGI_APPLICATION = 'hoocal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hoocal',
        'HOST': 'localhost',
        'USER': 'hoocal',
        'PASSWORD': 'hoocal',
        'PORT': 5432,
    }
}

DATABASES['default'] =  dj_database_url.config()

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '../static'),
)


# Tastypie Settings
TASTYPIE_DEFAULT_FORMATS = ('json',)
TASTYPIE_ABSTRACT_APIKEY = True

# TODO: not use now
"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/logs/hoocal.debug.log'
        }
    },
    'loggers': {
        'hoocal': {
            'handlers': ['file'],
            'level': DEBUG,
            'propagate': False
        }
    }
}
"""
