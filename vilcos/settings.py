# -*- coding: utf-8 -*-
from datetime import timedelta

import bleach
import os
import redis
from dotenv import load_dotenv

os_env = os.environ
load_dotenv()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', '3nF3Rn0')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    DEBUG_TB_ENABLED = os.environ.get('DEBUG_TB_ENABLED')
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql:///enferno')
    # for postgres
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql:///enferno')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/2')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')



    SESSION_PROTECTION = "strong"

    SESSION_TYPE = 'redis'

    SESSION_REDIS = redis.from_url(os.environ.get('REDIS_SESSION', 'redis://localhost:6379/1'))
    PERMANENT_SESSION_LIFETIME = 3600

    # flask mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')