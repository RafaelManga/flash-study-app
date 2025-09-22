#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações da aplicação FlashStudy
"""

import os
from datetime import timedelta

class Config:
    """Configurações base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'flashstudy_secret_key_2024'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de upload
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configurações de IA
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'SUA_CHAVE_GEMINI_AQUI'
    
    # Configurações de badges
    BADGE_CHECK_INTERVAL = 300  # 5 minutos

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://flashstudy:flashstudy123@localhost:5432/flashstudy_dev'

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://flashstudy:flashstudy123@localhost:5432/flashstudy_prod'

class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://flashstudy:flashstudy123@localhost:5432/flashstudy_test'

# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}



