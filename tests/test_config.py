import os
from src.config import DATABASE_URL, SECRET_KEY, JWT_SECRET, REDIS_URL, DEBUG

def test_database_url_default():
    assert "sfmshop" in DATABASE_URL

def test_secret_key_has_value():
    assert len(SECRET_KEY) > 0

def test_jwt_secret_has_value():
    assert len(JWT_SECRET) > 0

def test_redis_url_default():
    assert "redis" in REDIS_URL

def test_debug_is_bool():
    assert isinstance(DEBUG, bool)

def test_env_variables(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("REDIS_URL", "redis://test:6379")
    monkeypatch.setenv("DEBUG", "true")
    
    from importlib import reload
    import src.config
    reload(src.config)
    
    assert src.config.DATABASE_URL == "postgresql://test:test@localhost/test"
    assert src.config.SECRET_KEY == "test-secret"
    assert src.config.REDIS_URL == "redis://test:6379"
    assert src.config.DEBUG == True
