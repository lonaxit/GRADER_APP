from pathlib import Path
import dj_database_url
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# local
# SECRET_KEY = 'django-insecure-dfg=5b@%p+n0l23l2k2@k61j)bbwlw0gtl4$r!pt2q)(#z39@m'

# production
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# local
# DEBUG = True

# for production
DEBUG = env('DEBUG')

# production
# ALLOWED_HOSTS = ['skygiftedacademy.up.railway.app']

# dev
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'core',
     # config
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # for celery backend
    'django_celery_results'
    
]

CORS_ORIGIN_ALLOW_ALL = True



CORS_ALLOW_ALL_ORIGINS: False

# was present from production
CORS_ALLOWED_ORIGINS = [
    # "http://localhost:8080"
    "https://skygiftedacademyfrontend.onrender.com"
    # "https://www.skygiftedacademymkar.net",
  
]

# For Dev
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8080",
# ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gradebook.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'gradebook.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


# local
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME':'grader_api_db',
#         'USER': 'postgres',
#         'PASSWORD':'79_luper',
#     }
# }

# Prod
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': env('DB_NAME'),  # Replace with your database name env('DATABASE_URL')
#         'USER': env('DB_USER'),       # Replace with your username
#         'PASSWORD': env('DB_PASSWORD'),   # Replace with your password
#         'HOST': env('DB_HOST'),           # Replace with your host
#         'PORT': env('DB_PORT'),           # Replace with your port (default is 5432)
#     }
# }

# production
DATABASES={
    'default': dj_database_url.parse(env('DATABASE_PUBLIC_URL'))
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# custom user
AUTH_USER_MODEL='users.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
     'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'drf_excel.renderers.XLSXRenderer',
    ),
}

# Celery Settings
# railway
# comment out for now
# CELERY_BROKER_URL = 'redis://default:H4LI35FaK3Iap6pNIbkf51K2PLMHjFKk@roundhouse.proxy.rlwy.net:18044'

# CELERY_ACCEPT_CONTENT= ['application/json']
# CELERY_RESULT_SERIALIZER='json'
# CELERY_TASK_SERIALIZER ='json'
# CELERY_TIMEZONE='UTC'
# CELERY_RESULT_BACKEND = 'django-db'