"""
Configuration management for subscription management API
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Application Configuration
    DATA_FILE = os.getenv('DATA_FILE', 'subscription_data.json')
    RENEWAL_INTERVAL_HOURS = int(os.getenv('RENEWAL_INTERVAL_HOURS', '24'))
    PAYMENT_SUCCESS_RATE = float(os.getenv('PAYMENT_SUCCESS_RATE', '0.9'))
    SUBSCRIPTION_PRICE = float(os.getenv('SUBSCRIPTION_PRICE', '10.0'))
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5013'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'subscription_api.log')
    
    # Security Configuration
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))
    
    @classmethod
    def get_renewal_interval(cls) -> timedelta:
        """Get renewal interval as timedelta object"""
        return timedelta(hours=cls.RENEWAL_INTERVAL_HOURS)
    
    @classmethod
    def validate_config(cls) -> list:
        """Validate configuration and return list of errors"""
        errors = []
        
        if cls.RENEWAL_INTERVAL_HOURS <= 0:
            errors.append("RENEWAL_INTERVAL_HOURS must be positive")
        
        if not 0 <= cls.PAYMENT_SUCCESS_RATE <= 1:
            errors.append("PAYMENT_SUCCESS_RATE must be between 0 and 1")
        
        if cls.SUBSCRIPTION_PRICE <= 0:
            errors.append("SUBSCRIPTION_PRICE must be positive")
        
        if cls.PORT <= 0 or cls.PORT > 65535:
            errors.append("PORT must be between 1 and 65535")
        
        if cls.MAX_REQUESTS_PER_MINUTE <= 0:
            errors.append("MAX_REQUESTS_PER_MINUTE must be positive")
        
        return errors


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    DATA_FILE = 'dev_subscription_data.json'
    RENEWAL_INTERVAL_HOURS = 1  # Faster renewals for testing
    LOG_LEVEL = 'DEBUG'
    RATE_LIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    DATA_FILE = os.getenv('DATA_FILE', '/app/data/subscription_data.json')
    LOG_LEVEL = 'INFO'
    RATE_LIMIT_ENABLED = True
    
    @classmethod
    def validate_config(cls) -> list:
        """Additional validation for production"""
        errors = super().validate_config()
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append("SECRET_KEY must be set for production")
        
        return errors


class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    DEBUG = True
    DATA_FILE = 'test_subscription_data.json'
    RENEWAL_INTERVAL_HOURS = 1
    PAYMENT_SUCCESS_RATE = 1.0  # Always succeed in tests
    LOG_LEVEL = 'DEBUG'
    RATE_LIMIT_ENABLED = False


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name: str = None) -> Config:
    """
    Get configuration class based on environment name
    
    Args:
        env_name: Environment name (development, production, testing)
        
    Returns:
        Configuration class instance
    """
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'default')
    
    config_class = config_map.get(env_name.lower(), DevelopmentConfig)
    return config_class


def validate_environment() -> tuple[bool, list]:
    """
    Validate current environment configuration
    
    Returns:
        Tuple of (is_valid, error_list)
    """
    env_name = os.getenv('FLASK_ENV', 'default')
    config_class = get_config(env_name)
    
    errors = config_class.validate_config()
    
    return len(errors) == 0, errors


if __name__ == '__main__':
    # Configuration validation utility
    print("=== Configuration Validation ===")
    
    for env_name, config_class in config_map.items():
        if env_name == 'default':
            continue
            
        print(f"\n{env_name.upper()} Configuration:")
        errors = config_class.validate_config()
        
        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ Validation passed")
            
        # Show key config values
        print(f"  Data file: {config_class.DATA_FILE}")
        print(f"  Renewal interval: {config_class.RENEWAL_INTERVAL_HOURS}h")
        print(f"  Payment success rate: {config_class.PAYMENT_SUCCESS_RATE}")
        print(f"  Debug mode: {config_class.DEBUG}")
    
    print(f"\nCurrent environment: {os.getenv('FLASK_ENV', 'default')}")
    is_valid, current_errors = validate_environment()
    
    if is_valid:
        print("✅ Current environment configuration is valid")
    else:
        print("❌ Current environment configuration has errors:")
        for error in current_errors:
            print(f"  - {error}")