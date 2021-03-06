"""
Django settings for ChallengeHub project.

Generated by 'django-admin startproject' using Django 1.9.13.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import json
import pymongo
import sys

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

travis = os.getenv('BUILD_ON_TRAVIS', None)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if travis:
    configFileName = 'config.travis.json'
else:
    configFileName = 'config.json'

configFilePath = os.getenv(
    'DJANGO_CONFIG_PATH', os.path.join(BASE_DIR, configFileName))

CONFIGS = json.loads(open(configFilePath).read())

MONGO_CLIENT = pymongo.MongoClient(
    CONFIGS['MONGO_HOST'], CONFIGS['MONGO_PORT'])
    
MONGO_CLIENT.db = MONGO_CLIENT.test if TESTING else MONGO_CLIENT.normal

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend", "dist", "static"),
    os.path.join(BASE_DIR, "submit"),
]

CORS_ORIGIN_ALLOW_ALL = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wl7lznjp**r&dsn(8stzhbsb&3&1rq!yly#*2lnk987a)wdqc+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIGS['DEBUG']

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'basic',
    'useraction',
    'match',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend']

ROOT_URLCONF = 'ChallengeHub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['frontend/dist'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ChallengeHub.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': CONFIGS['DB_NAME'],
        'USER': CONFIGS['DB_USER'],
        'PASSWORD': CONFIGS['DB_PASS'],
        'HOST': CONFIGS['DB_HOST'],
        'PORT': CONFIGS['DB_PORT']
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = 'static'

AUTH_USER_MODEL = 'useraction.User'

SITE_URL = CONFIGS['SITE_URL']

VALIDATE_SALT = CONFIGS['VALIDATE_SALT']

USE_MAIL_VALIDATE = CONFIGS['USE_MAIL_VALIDATE']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.163.com'

EMAIL_USE_SSL = True

EMAIL_PORT = 465

EMAIL_HOST_USER = CONFIGS['EMAIL_ACCOUNT']

EMAIL_HOST_PASSWORD = CONFIGS['EMAIL_PASSWORD']

EMAIL_FROM = f'admin<{EMAIL_HOST_USER}>'
