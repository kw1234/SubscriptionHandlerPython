"""
Business logic services for subscription management
"""

import json
import logging
import os
import random
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from models import User, SubscriptionState, PaymentResult, ServiceResponse

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for handling payment processing"""
    
    @staticmethod
    def process_payment(user_id: str, amount: float) -> PaymentResult:
        """
        Process a payment for a user
        In production, this would integrate with a real payment processor
        """
        # Simulate payment processing with 90% success rate
        success = random.random() < 0.9
        
        if success:
            message = f"Payment of ${amount} processed successfully for user {user_id}"
            logger.info(message)
        else:
            message = f"Payment of ${amount} failed for user {user_id}"
            logger.warning(message)
        
        return PaymentResult(success, amount, message)


class DataService:
    """Service for data persistence operations"""
    
    def __init__(self, data_file: str = 'subscription_data.json'):
        self.data_file = data_file
    
    def save_users(self, users: Dict[str, User]) -> bool:
        """Save all user data to file"""
        try:
            data = {user_id: user.to_dict() for user_id, user in users.items()}
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Data saved to {self.data_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def load_users(self) -> Dict[str, User]:
        """Load user data from file"""
        users = {}
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                for user_id, user_data in data.items():
                    users[user_id] = User.from_dict(user_data)
                
                logger.info(f"Data loaded from {self.data_file}")
            except Exception as e:
                logger.error(f"Error loading data: {e}")
        else:
            logger.info(f"No existing data file found at {self.data_file}")
        
        return users


class CoverageService:
    """Service for handling coverage calculations and reporting"""
    
    @staticmethod
    def calculate_coverage_report(user: User, start_date: datetime, end_date: datetime) -> Dict:
        """Generate detailed coverage report for a user over a date range"""
        covered_periods = []
        uncovered_periods = []
        
        current_time = start_date
        while current_time <= end_date:
            is_covered = user.is_covered_at(current_time)
            
            if is_covered:
                covered_periods.append(current_time)
            else:
                uncovered_periods.append(current_time)
            
            current_time += timedelta(hours=1)
        
        total_hours = len(covered_periods) + len(uncovered_periods)
        coverage_percentage = (len(covered_periods) / total_hours * 100) if total_hours > 0 else 0
        
        return {
            'user_id': user.user_id,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'coverage_percentage': round(coverage_percentage, 2),
            'covered_hours': len(covered_periods),
            'total_hours': total_hours,
            'payment_count': len(user.payment_history),
            'successful_payments': len([p for p in user.payment_history if p['status'] == 'success']),
            'failed_payments': len([p for p in user.payment_history if p['status'] == 'failed'])
        }


class SubscriptionService:
    """Main service for subscription management operations"""
    
    def __init__(self, data_service: DataService = None, payment_service: PaymentService = None):
        self.users: Dict[str, User] = {}
        self.renewal_interval = timedelta(hours=24)
        self.running = False
        self.renewal_thread = None
        
        # Initialize services
        self.data_service = data_service or DataService()
        self.payment_service = payment_service or PaymentService()
        self.coverage_service = CoverageService()
        
        # Load existing data
        self.users = self.data_service.load_users()
    
    def start_service(self) -> ServiceResponse:
        """Start the background renewal service"""
        if not self.running:
            self.running = True
            self.renewal_thread = threading.Thread(target=self._renewal_worker, daemon=True)
            self.renewal_thread.start()
            logger.info("Subscription service started")
            return ServiceResponse(True, "Subscription service started")
        else:
            return ServiceResponse(False, "Service is already running")
    
    def stop_service(self) -> ServiceResponse:
        """Stop the background renewal service"""
        if self.running:
            self.running = False
            if self.renewal_thread:
                self.renewal_thread.join()
            self._save_data()
            logger.info("Subscription service stopped")
            return ServiceResponse(True, "Subscription service stopped")
        else:
            return ServiceResponse(False, "Service is not running")
    
    def purchase_subscription(self, user_id: str) -> ServiceResponse:
        """Handle subscription purchase for a user"""
        if not self._validate_user_id(user_id):
            return ServiceResponse(False, "Invalid user ID")
        
        now = datetime.now()
        
        # Get or create user
        if user_id not in self.users:
            self.users[user_id] = User(user_id)
        
        user = self.users[user_id]
        
        # Process payment
        payment_result = self.payment_service.process_payment(user_id, 10.0)
        user.add_payment(payment_result.amount, 'success' if payment_result.success else 'failed')
        
        if payment_result.success:
            user.state = SubscriptionState.ACTIVE
            user.subscription_start = now
            user.last_renewal = now
            user.off_command_time = None  # Clear any pending off command
            
            # Start coverage period
            user.start_coverage_period()
            
            self._save_data()
            
            message = f"Subscription activated for user {user_id}"
            logger.info(message)
            return ServiceResponse(True, message, {'user_state': self._get_user_state_dict(user)})
        else:
            message = f"Payment failed for user {user_id}"
            logger.error(message)
            return ServiceResponse(False, message)
    
    def issue_off_command(self, user_id: str) -> ServiceResponse:
        """Handle off command from user"""
        if not self._validate_user_id(user_id):
            return ServiceResponse(False, "Invalid user ID")
        
        if user_id not in self.users:
            return ServiceResponse(False, "User not found")
        
        user = self.users[user_id]
        now = datetime.now()
        
        if user.state == SubscriptionState.ACTIVE:
            user.state = SubscriptionState.PENDING_OFF
            user.off_command_time = now
            self._save_data()
            
            message = f"Off command processed for user {user_id}. Subscription will end after 24 hours."
            logger.info(message)
            return ServiceResponse(True, message, {'user_state': self._get_user_state_dict(user)})
        else:
            message = f"User {user_id} is not in active state"
            return ServiceResponse(False, message)
    
    def get_user_state(self, user_id: str) -> Optional[Dict]:
        """Get current state of user subscription"""
        if not self._validate_user_id(user_id) or user_id not in self.users:
            return None
        
        user = self.users[user_id]
        return self._get_user_state_dict(user)
    
    def get_coverage_report(self, user_id: str, start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """Generate coverage report for a user over a date range"""
        if not self._validate_user_id(user_id) or user_id not in self.users:
            return None
        
        user = self.users[user_id]
        return self.coverage_service.calculate_coverage_report(user, start_date, end_date)
    
    def get_all_users(self) -> List[Dict]:
        """Get state of all users"""
        return [self._get_user_state_dict(user) for user in self.users.values()]
    
    def get_service_status(self) -> Dict:
        """Get current service status"""
        return {
            'service_running': self.running,
            'total_users': len(self.users),
            'active_users': len([u for u in self.users.values() if u.state == SubscriptionState.ACTIVE]),
            'pending_off_users': len([u for u in self.users.values() if u.state == SubscriptionState.PENDING_OFF]),
            'inactive_users': len([u for u in self.users.values() if u.state == SubscriptionState.OFF]),
            'renewal_interval_hours': self.renewal_interval.total_seconds() / 3600
        }
    
    def _get_user_state_dict(self, user: User) -> Dict:
        """Convert user state to dictionary format"""
        now = datetime.now()
        is_covered = user.is_covered_at(now)
        
        return {
            'user_id': user.user_id,
            'state': user.state.value,
            'is_covered': is_covered,
            'subscription_start': user.subscription_start.isoformat() if user.subscription_start else None,
            'last_renewal': user.last_renewal.isoformat() if user.last_renewal else None,
            'off_command_time': user.off_command_time.isoformat() if user.off_command_time else None,
            'next_renewal': (user.last_renewal + self.renewal_interval).isoformat() if user.last_renewal else None,
            'payment_history_count': len(user.payment_history),
            'coverage_periods_count': len(user.coverage_history)
        }
    
    def _validate_user_id(self, user_id: str) -> bool:
        """Validate user ID format"""
        return bool(user_id and isinstance(user_id, str) and len(user_id.strip()) > 0)
    
    def _save_data(self) -> None:
        """Save user data using data service"""
        self.data_service.save_users(self.users)
    
    def _renewal_worker(self) -> None:
        """Background worker that handles automatic renewals"""
        while self.running:
            try:
                self._process_renewals()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in renewal worker: {e}")
    
    def _process_renewals(self) -> None:
        """Process automatic renewals for all users"""
        now = datetime.now()
        
        for user in self.users.values():
            if user.state == SubscriptionState.ACTIVE and user.last_renewal:
                # Check if 24 hours have passed since last renewal
                if now >= user.last_renewal + self.renewal_interval:
                    self._attempt_renewal(user, now)
            
            elif user.state == SubscriptionState.PENDING_OFF and user.off_command_time:
                # Check if 24 hours have passed since off command
                if now >= user.off_command_time + self.renewal_interval:
                    self._turn_off_subscription(user, now)
    
    def _attempt_renewal(self, user: User, now: datetime) -> None:
        """Attempt to renew subscription for a user"""
        payment_result = self.payment_service.process_payment(user.user_id, 10.0)
        user.add_payment(payment_result.amount, 'success' if payment_result.success else 'failed')
        
        if payment_result.success:
            user.last_renewal = now
            logger.info(f"Successfully renewed subscription for user {user.user_id}")
            
            # Coverage continues seamlessly - no need to end/start new period
        else:
            # Payment failed, turn off subscription
            user.state = SubscriptionState.OFF
            user.end_coverage_period(now)
            logger.info(f"Payment failed for user {user.user_id}. Subscription turned off.")
        
        self._save_data()
    
    def _turn_off_subscription(self, user: User, now: datetime) -> None:
        """Turn off subscription after off command grace period"""
        user.state = SubscriptionState.OFF
        user.end_coverage_period(now)
        self._save_data()
        logger.info(f"Subscription turned off for user {user.user_id} after 24hr grace period")