"""
API route handlers for subscription management
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from services import SubscriptionService

logger = logging.getLogger(__name__)

# Create blueprints for different route groups
api_bp = Blueprint('api', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Global subscription service instance (will be set by app initialization)
subscription_service: SubscriptionService = None


def init_routes(service: SubscriptionService):
    """Initialize routes with subscription service"""
    global subscription_service
    subscription_service = service


def require_json(f):
    """Decorator to ensure request contains JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        return f(*args, **kwargs)
    return decorated_function


def validate_user_id(user_id):
    """Validate user ID format"""
    if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
        return False
    return True


def parse_datetime_param(param_value, param_name):
    """Parse datetime parameter from request"""
    if not param_value:
        return None
    
    try:
        return datetime.fromisoformat(param_value)
    except ValueError:
        raise ValueError(f"Invalid {param_name} format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")


# Health and Status Routes
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    service_status = subscription_service.get_service_status()
    
    return jsonify({
        'status': 'healthy',
        'service': service_status,
        'timestamp': datetime.now().isoformat()
    })


# Subscription Management Routes
@api_bp.route('/subscription/purchase', methods=['POST'])
@require_json
def purchase_subscription():
    """Purchase a subscription"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user_id'}), 400
        
        result = subscription_service.purchase_subscription(user_id)
        status_code = 200 if result.success else 400
        
        response_data = {
            'success': result.success,
            'message': result.message,
            'timestamp': result.timestamp.isoformat()
        }
        
        if result.data:
            response_data['data'] = result.data
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Error in purchase_subscription: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/subscription/off', methods=['POST'])
@require_json
def issue_off_command():
    """Issue off command for a subscription"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user_id'}), 400
        
        result = subscription_service.issue_off_command(user_id)
        status_code = 200 if result.success else 400
        
        response_data = {
            'success': result.success,
            'message': result.message,
            'timestamp': result.timestamp.isoformat()
        }
        
        if result.data:
            response_data['data'] = result.data
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Error in issue_off_command: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/subscription/status/<user_id>', methods=['GET'])
def get_subscription_status(user_id):
    """Get subscription status for a user"""
    try:
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user_id'}), 400
        
        state = subscription_service.get_user_state(user_id)
        
        if state is None:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(state)
        
    except Exception as e:
        logger.error(f"Error in get_subscription_status: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/subscription/coverage/<user_id>', methods=['GET'])
def get_coverage_report(user_id):
    """Get coverage report for a user"""
    try:
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user_id'}), 400
        
        # Parse query parameters for date range
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        try:
            if start_date_str:
                start_date = parse_datetime_param(start_date_str, 'start_date')
            else:
                start_date = datetime.now() - timedelta(days=7)  # Default to last 7 days
            
            if end_date_str:
                end_date = parse_datetime_param(end_date_str, 'end_date')
            else:
                end_date = datetime.now()
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        if start_date >= end_date:
            return jsonify({'error': 'start_date must be before end_date'}), 400
        
        report = subscription_service.get_coverage_report(user_id, start_date, end_date)
        
        if report is None:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error in get_coverage_report: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Admin Routes
@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get status of all users (admin endpoint)"""
    try:
        users = subscription_service.get_all_users()
        service_status = subscription_service.get_service_status()
        
        return jsonify({
            'service_status': service_status,
            'users': users
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_users: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/service/start', methods=['POST'])
def start_service():
    """Start the renewal service (admin endpoint)"""
    try:
        result = subscription_service.start_service()
        status_code = 200 if result.success else 400
        
        return jsonify({
            'success': result.success,
            'message': result.message,
            'timestamp': result.timestamp.isoformat()
        }), status_code
        
    except Exception as e:
        logger.error(f"Error in start_service: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/service/stop', methods=['POST'])
def stop_service():
    """Stop the renewal service (admin endpoint)"""
    try:
        result = subscription_service.stop_service()
        status_code = 200 if result.success else 400
        
        return jsonify({
            'success': result.success,
            'message': result.message,
            'timestamp': result.timestamp.isoformat()
        }), status_code
        
    except Exception as e:
        logger.error(f"Error in stop_service: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/service/status', methods=['GET'])
def get_service_status():
    """Get detailed service status (admin endpoint)"""
    try:
        status = subscription_service.get_service_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error in get_service_status: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Error Handlers
def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}")
        return jsonify({'error': 'An unexpected error occurred'}), 500