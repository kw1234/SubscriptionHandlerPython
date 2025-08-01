"""
Data models for the subscription management system
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class SubscriptionState(Enum):
    ACTIVE = "active"
    PENDING_OFF = "pending_off"
    OFF = "off"


class User:
    """User model representing a subscription user"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.state = SubscriptionState.OFF
        self.subscription_start = None
        self.last_renewal = None
        self.off_command_time = None
        self.payment_history = []
        self.coverage_history = []
    
    def to_dict(self) -> Dict:
        """Convert user object to dictionary for serialization"""
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
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user object from dictionary"""
        user = cls(data['user_id'])
        user.state = SubscriptionState(data['state'])
        user.subscription_start = datetime.fromisoformat(data['subscription_start']) if data['subscription_start'] else None
        user.last_renewal = datetime.fromisoformat(data['last_renewal']) if data['last_renewal'] else None
        user.off_command_time = datetime.fromisoformat(data['off_command_time']) if data['off_command_time'] else None
        
        user.payment_history = [
            {
                'timestamp': datetime.fromisoformat(p['timestamp']),
                'amount': p['amount'],
                'status': p['status']
            } for p in data.get('payment_history', [])
        ]
        
        user.coverage_history = [
            {
                'start': datetime.fromisoformat(c['start']),
                'end': datetime.fromisoformat(c['end']) if c['end'] else None,
                'covered': c['covered']
            } for c in data.get('coverage_history', [])
        ]
        
        return user
    
    def add_payment(self, amount: float, status: str) -> None:
        """Add a payment record to the user's history"""
        payment_record = {
            'timestamp': datetime.now(),
            'amount': amount,
            'status': status
        }
        self.payment_history.append(payment_record)
    
    def start_coverage_period(self) -> None:
        """Start a new coverage period"""
        coverage_record = {
            'start': datetime.now(),
            'end': None,
            'covered': True
        }
        self.coverage_history.append(coverage_record)
    
    def end_coverage_period(self, end_time: datetime = None) -> None:
        """End the current coverage period"""
        if end_time is None:
            end_time = datetime.now()
            
        if self.coverage_history and not self.coverage_history[-1]['end']:
            self.coverage_history[-1]['end'] = end_time
    
    def is_covered_at(self, timestamp: datetime) -> bool:
        """Check if user is covered at a specific timestamp"""
        for coverage in self.coverage_history:
            if coverage['start'] <= timestamp:
                if coverage['end'] is None or timestamp <= coverage['end']:
                    return coverage['covered']
        return False


class PaymentResult:
    """Result of a payment processing attempt"""
    
    def __init__(self, success: bool, amount: float, message: str = ""):
        self.success = success
        self.amount = amount
        self.message = message
        self.timestamp = datetime.now()


class ServiceResponse:
    """Standard response format for service operations"""
    
    def __init__(self, success: bool, message: str, data: Dict = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert response to dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }