from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import json
import threading
import time

class SubscriptionState(Enum):
    ACTIVE = "active"
    PENDING_OFF = "pending_off"
    OFF = "off"

class User:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.state = SubscriptionState.OFF
        self.subscription_start = None
        self.last_renewal = None
        self.off_command_time = None
        self.payment_history = []
        self.coverage_history = []
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'state': self.state.value,
            'subscription_start': self.subscription_start.isoformat() if self.subscription_start else None,
            'last_renewal': self.last_renewal.isoformat() if self.last_renewal else None,
            'off_command_time': self.off_command_time.isoformat() if self.off_command_time else None,
            'payment_history': [
                {
                    'timestamp': p['timestamp'].isoformat(),
                    'amount': p['amount'],
                    'status': p['status']
                } for p in self.payment_history
            ],
            'coverage_history': [
                {
                    'start': c['start'].isoformat(),
                    'end': c['end'].isoformat() if c['end'] else None,
                    'covered': c['covered']
                } for c in self.coverage_history
            ]
        }

class SubscriptionManager:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.renewal_interval = timedelta(minutes=2)
        self.running = False
        self.renewal_thread = None
    
    def start_service(self):
        """Start the background renewal service"""
        self.running = True
        self.renewal_thread = threading.Thread(target=self._renewal_worker, daemon=True)
        self.renewal_thread.start()
        print("Subscription service started")
    
    def stop_service(self):
        """Stop the background renewal service"""
        self.running = False
        if self.renewal_thread:
            self.renewal_thread.join()
        print("Subscription service stopped")
    
    def purchase_subscription(self, user_id: str) -> bool:
        """Handle subscription purchase"""
        now = datetime.now()
        
        if user_id not in self.users:
            self.users[user_id] = User(user_id)
        
        user = self.users[user_id]
        
        # Process payment
        payment_success = self._process_payment(user_id, 10.0)  # $10 subscription
        
        if payment_success:
            user.state = SubscriptionState.ACTIVE
            user.subscription_start = now
            user.last_renewal = now
            user.off_command_time = None  # Clear any pending off command
            
            # Start coverage period
            self._start_coverage_period(user)
            
            print(f"Subscription activated for user {user_id}")
            return True
        else:
            print(f"Payment failed for user {user_id}")
            return False
    
    def issue_off_command(self, user_id: str) -> bool:
        """Handle off command from user"""
        if user_id not in self.users:
            print(f"User {user_id} not found")
            return False
        
        user = self.users[user_id]
        now = datetime.now()
        
        if user.state == SubscriptionState.ACTIVE:
            user.state = SubscriptionState.PENDING_OFF
            user.off_command_time = now
            print(f"Off command issued for user {user_id}. Will turn off after 24hr period.")
            return True
        else:
            print(f"User {user_id} is not in active state")
            return False
    
    def get_user_state(self, user_id: str) -> Optional[Dict]:
        """Get current state of user subscription"""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        now = datetime.now()
        
        is_covered = self._is_user_covered(user_id, now)
        
        return {
            'user_id': user_id,
            'state': user.state.value,
            'is_covered': is_covered,
            'subscription_start': user.subscription_start,
            'last_renewal': user.last_renewal,
            'off_command_time': user.off_command_time,
            'next_renewal': user.last_renewal + self.renewal_interval if user.last_renewal else None
        }
    
    def _renewal_worker(self):
        """Background worker that handles automatic renewals"""
        while self.running:
            try:
                self._process_renewals()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in renewal worker: {e}")
    
    def _process_renewals(self):
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
    
    def _attempt_renewal(self, user: User, now: datetime):
        """Attempt to renew subscription for a user"""
        payment_success = self._process_payment(user.user_id, 10.0)
        
        if payment_success:
            user.last_renewal = now
            print(f"Successfully renewed subscription for user {user.user_id}")
            
            # Continue coverage period
            if user.coverage_history and not user.coverage_history[-1]['end']:
                # Coverage continues seamlessly
                pass
            else:
                # Start new coverage period
                self._start_coverage_period(user)
        else:
            # Payment failed, turn off subscription
            user.state = SubscriptionState.OFF
            self._end_coverage_period(user, now)
            print(f"Payment failed for user {user.user_id}. Subscription turned off.")
    
    def _turn_off_subscription(self, user: User, now: datetime):
        """Turn off subscription after off command grace period"""
        user.state = SubscriptionState.OFF
        self._end_coverage_period(user, now)
        print(f"Subscription turned off for user {user.user_id} after 24hr grace period")
    
    def _process_payment(self, user_id: str, amount: float) -> bool:
        """Simulate payment processing"""
        # In real implementation, this would integrate with payment processor
        user = self.users[user_id]
        
        # Simulate 90% success rate
        import random
        success = random.random() < 0.9
        
        payment_record = {
            'timestamp': datetime.now(),
            'amount': amount,
            'status': 'success' if success else 'failed'
        }
        user.payment_history.append(payment_record)
        
        return success
    
    def _start_coverage_period(self, user: User):
        """Start a new coverage period"""
        now = datetime.now()
        coverage_record = {
            'start': now,
            'end': None,
            'covered': True
        }
        user.coverage_history.append(coverage_record)
    
    def _end_coverage_period(self, user: User, end_time: datetime):
        """End the current coverage period"""
        if user.coverage_history and not user.coverage_history[-1]['end']:
            user.coverage_history[-1]['end'] = end_time
    
    def _is_user_covered(self, user_id: str, timestamp: datetime) -> bool:
        """Check if user is covered at a specific timestamp"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # Check if there's an active coverage period
        for coverage in user.coverage_history:
            if coverage['start'] <= timestamp:
                if coverage['end'] is None or timestamp <= coverage['end']:
                    return coverage['covered']
        
        return False
    
    def get_coverage_report(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Generate coverage report for a user over a date range"""
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        user = self.users[user_id]
        covered_periods = []
        uncovered_periods = []
        
        current_time = start_date
        while current_time <= end_date:
            is_covered = self._is_user_covered(user_id, current_time)
            
            # This is a simplified approach - in practice you'd want more sophisticated period tracking
            if is_covered:
                covered_periods.append(current_time)
            else:
                uncovered_periods.append(current_time)
            
            current_time += timedelta(hours=1)  # Check hourly
        
        total_hours = len(covered_periods) + len(uncovered_periods)
        coverage_percentage = (len(covered_periods) / total_hours * 100) if total_hours > 0 else 0
        
        return {
            'user_id': user_id,
            'period': f"{start_date.isoformat()} to {end_date.isoformat()}",
            'coverage_percentage': coverage_percentage,
            'covered_hours': len(covered_periods),
            'total_hours': total_hours,
            'payment_history': user.payment_history
        }
    
    def save_data(self, filename: str):
        """Save all user data to file"""
        data = {user_id: user.to_dict() for user_id, user in self.users.items()}
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {filename}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize subscription manager
    manager = SubscriptionManager()
    manager.start_service()
    
    try:
        # Test scenario 1: Normal subscription flow
        print("=== Test 1: Normal Subscription ===")
        manager.purchase_subscription("user123")
        print(manager.get_user_state("user123"))
        
        # Test scenario 2: Off command
        print("\n=== Test 2: Off Command ===")
        time.sleep(2)  # Wait a bit
        manager.issue_off_command("user123")
        print(manager.get_user_state("user123"))
        
        # Test scenario 3: Check coverage
        print("\n=== Test 3: Coverage Check ===")
        now = datetime.now()
        is_covered = manager._is_user_covered("user123", now)
        print(f"User is currently covered: {is_covered}")
        
        # Test scenario 4: Coverage report
        print("\n=== Test 4: Coverage Report ===")
        start_date = datetime.now() - timedelta(hours=2)
        end_date = datetime.now()
        report = manager.get_coverage_report("user123", start_date, end_date)
        print(f"Coverage report: {report}")
        
        # Keep running for a bit to see renewals (in real scenario)
        print("\n=== System running... (Press Ctrl+C to stop) ===")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        manager.stop_service()
        manager.save_data("subscription_data.json")