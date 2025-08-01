"""
Flask application factory for subscription management API
"""

import logging
import os
from flask import Flask
from flask.logging import default_handler

from services import SubscriptionService, DataService, PaymentService
from routes import api_bp, admin_bp, init_routes, register_error_handlers


def setup_logging(app: Flask) -> None:
    """Configure application logging"""
    # Remove default Flask handler
    app.logger.removeHandler(default_handler)
    
    # Set up custom logging
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('subscription_api.log')
        ]
    )
    
    # Set specific loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    app.logger.setLevel(getattr(logging, log_level))


def create_app(config: dict = None) -> tuple[Flask, SubscriptionService]:
    """
    Application factory function
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Tuple of (Flask app, SubscriptionService instance)
    """
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    else:
        # Default configuration
        app.config.update({
            'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            'DATA_FILE': os.getenv('DATA_FILE', 'subscription_data.json'),
            'RENEWAL_INTERVAL_HOURS': int(os.getenv('RENEWAL_INTERVAL_HOURS', '24')),
            'PAYMENT_SUCCESS_RATE': float(os.getenv('PAYMENT_SUCCESS_RATE', '0.9'))
        })
    
    # Setup logging
    setup_logging(app)
    app.logger.info("Starting Subscription Management API")
    
    # Initialize services
    data_service = DataService(app.config['DATA_FILE'])
    payment_service = PaymentService()
    subscription_service = SubscriptionService(data_service, payment_service)
    
    # Configure renewal interval if specified
    if 'RENEWAL_INTERVAL_HOURS' in app.config:
        from datetime import timedelta
        subscription_service.renewal_interval = timedelta(hours=app.config['RENEWAL_INTERVAL_HOURS'])
    
    # Initialize routes with services
    init_routes(subscription_service)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add request logging middleware
    @app.before_request
    def log_request_info():
        from flask import request
        if not app.config.get('DEBUG'):
            app.logger.info(f"{request.method} {request.url}")
    
    @app.after_request
    def log_response_info(response):
        if not app.config.get('DEBUG'):
            app.logger.info(f"Response: {response.status_code}")
        return response
    
    app.logger.info("Application initialization complete")
    
    return app, subscription_service


def create_production_app() -> tuple[Flask, SubscriptionService]:
    """Create app with production configuration"""
    config = {
        'DEBUG': False,
        'DATA_FILE': os.getenv('DATA_FILE', 'subscription_data.json'),
        'RENEWAL_INTERVAL_HOURS': int(os.getenv('RENEWAL_INTERVAL_HOURS', '24')),
        'PAYMENT_SUCCESS_RATE': float(os.getenv('PAYMENT_SUCCESS_RATE', '0.9'))
    }
    return create_app(config)


def create_development_app() -> tuple[Flask, SubscriptionService]:
    """Create app with development configuration"""
    config = {
        'DEBUG': True,
        'DATA_FILE': 'dev_subscription_data.json',
        'RENEWAL_INTERVAL_HOURS': 1,  # Faster renewals for testing
        'PAYMENT_SUCCESS_RATE': 0.9
    }
    return create_app(config)


def create_test_app() -> tuple[Flask, SubscriptionService]:
    """Create app with test configuration"""
    config = {
        'DEBUG': True,
        'TESTING': True,
        'DATA_FILE': 'test_subscription_data.json',
        'RENEWAL_INTERVAL_HOURS': 1,
        'PAYMENT_SUCCESS_RATE': 1.0  # Always succeed in tests
    }
    return create_app(config)