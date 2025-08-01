#!/usr/bin/env python3
"""
Main server entry point for subscription management API
"""

import os
import signal
import sys
import logging
from app import create_app, create_production_app, create_development_app

logger = logging.getLogger(__name__)


def handle_shutdown(signum, frame):
    """Handle graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    if subscription_service:
        subscription_service.stop_service()
    sys.exit(0)


def main():
    """Main function to start the server"""
    global subscription_service
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Determine environment
    env = os.getenv('FLASK_ENV', 'production').lower()
    
    if env == 'development':
        app, subscription_service = create_development_app()
        print("🚀 Starting development server...")
    else:
        app, subscription_service = create_production_app()
        print("🚀 Starting production server...")
    
    # Start the subscription service
    start_result = subscription_service.start_service()
    if start_result.success:
        print(f"✅ {start_result.message}")
    else:
        print(f"❌ Failed to start subscription service: {start_result.message}")
        return 1
    
    # Get server configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    debug = env == 'development'
    
    print(f"🌐 Server starting on http://{host}:{port}")
    print(f"📝 Environment: {env}")
    print(f"🔧 Debug mode: {debug}")
    print(f"💾 Data file: {app.config['DATA_FILE']}")
    print(f"⏰ Renewal interval: {app.config['RENEWAL_INTERVAL_HOURS']} hours")
    print("\n📚 API Documentation:")
    print("  Health Check:      GET  /health")
    print("  Purchase Sub:      POST /subscription/purchase")
    print("  Turn Off Sub:      POST /subscription/off") 
    print("  Check Status:      GET  /subscription/status/{user_id}")
    print("  Coverage Report:   GET  /subscription/coverage/{user_id}")
    print("  Admin - All Users: GET  /admin/users")
    print("  Admin - Start:     POST /admin/service/start")
    print("  Admin - Stop:      POST /admin/service/stop")
    print("  Admin - Status:    GET  /admin/service/status")
    print("\n🔗 Quick test: curl http://localhost:5000/health")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        # Run the Flask application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False  # Disable reloader to avoid double service start
        )
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
    finally:
        print("🔄 Stopping subscription service...")
        if subscription_service:
            stop_result = subscription_service.stop_service()
            print(f"✅ {stop_result.message}")
        print("👋 Server shutdown complete")
    
    return 0


if __name__ == '__main__':
    # Global variable to hold service reference for signal handler
    subscription_service = None
    
    # Exit with the return code from main
    sys.exit(main())