"""
Advanced authentication and authorization system.
"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

import jwt
from cryptography.fernet import Fernet


class Permission(Enum):
    """User permissions."""
    READ_MESSAGES = "read_messages"
    SEND_MESSAGES = "send_messages"
    MANAGE_SUBSCRIPTION = "manage_subscription"
    VIEW_ANALYTICS = "view_analytics"
    ADMIN_ACCESS = "admin_access"
    MODERATE_USERS = "moderate_users"


class Role(Enum):
    """User roles."""
    USER = "user"
    PREMIUM_USER = "premium_user"
    MODERATOR = "moderator"
    ADMIN = "admin"


@dataclass
class UserSession:
    """User session data."""
    user_id: int
    session_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


@dataclass
class SecurityToken:
    """Security token data."""
    token: str
    user_id: int
    token_type: str  # access, refresh, api
    created_at: datetime
    expires_at: datetime
    permissions: List[Permission]
    is_revoked: bool = False


class AuthenticationService:
    """Advanced authentication service."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.sessions: Dict[str, UserSession] = {}
        self.tokens: Dict[str, SecurityToken] = {}
        self.failed_attempts: Dict[int, List[datetime]] = {}
        self.blocked_users: Set[int] = set()
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.session_timeout = timedelta(hours=24)
        self.token_timeout = timedelta(hours=1)
        
    def create_session(
        self, 
        user_id: int, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create new user session."""
        if user_id in self.blocked_users:
            raise SecurityException("User is blocked")
            
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            created_at=now,
            expires_at=now + self.session_timeout,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session
        return session
        
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """Validate user session."""
        session = self.sessions.get(session_id)
        
        if not session:
            return None
            
        if not session.is_active:
            return None
            
        if datetime.utcnow() > session.expires_at:
            self.revoke_session(session_id)
            return None
            
        # Update last activity
        session.last_activity = datetime.utcnow()
        return session
        
    def revoke_session(self, session_id: str) -> bool:
        """Revoke user session."""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            return True
        return False
        
    def create_access_token(
        self, 
        user_id: int, 
        permissions: List[Permission]
    ) -> SecurityToken:
        """Create access token."""
        now = datetime.utcnow()
        token = jwt.encode({
            'user_id': user_id,
            'permissions': [p.value for p in permissions],
            'iat': now.timestamp(),
            'exp': (now + self.token_timeout).timestamp(),
            'type': 'access'
        }, self.secret_key, algorithm='HS256')
        
        security_token = SecurityToken(
            token=token,
            user_id=user_id,
            token_type='access',
            created_at=now,
            expires_at=now + self.token_timeout,
            permissions=permissions
        )
        
        self.tokens[token] = security_token
        return security_token
        
    def validate_token(self, token: str) -> Optional[SecurityToken]:
        """Validate security token."""
        try:
            # Check if token is revoked
            if token in self.tokens and self.tokens[token].is_revoked:
                return None
                
            # Decode JWT
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check expiration
            if datetime.utcnow().timestamp() > payload['exp']:
                return None
                
            return self.tokens.get(token)
            
        except jwt.InvalidTokenError:
            return None
            
    def revoke_token(self, token: str) -> bool:
        """Revoke security token."""
        if token in self.tokens:
            self.tokens[token].is_revoked = True
            return True
        return False
        
    def record_failed_attempt(self, user_id: int) -> None:
        """Record failed authentication attempt."""
        now = datetime.utcnow()
        
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
            
        self.failed_attempts[user_id].append(now)
        
        # Clean old attempts
        cutoff = now - self.lockout_duration
        self.failed_attempts[user_id] = [
            attempt for attempt in self.failed_attempts[user_id]
            if attempt > cutoff
        ]
        
        # Check if user should be blocked
        if len(self.failed_attempts[user_id]) >= self.max_failed_attempts:
            self.blocked_users.add(user_id)
            
    def clear_failed_attempts(self, user_id: int) -> None:
        """Clear failed attempts for user."""
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
            
    def unblock_user(self, user_id: int) -> None:
        """Unblock user."""
        self.blocked_users.discard(user_id)
        self.clear_failed_attempts(user_id)
        
    def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is blocked."""
        return user_id in self.blocked_users


class AuthorizationService:
    """Authorization service for permission checking."""
    
    def __init__(self):
        self.role_permissions: Dict[Role, Set[Permission]] = {
            Role.USER: {
                Permission.READ_MESSAGES,
                Permission.SEND_MESSAGES
            },
            Role.PREMIUM_USER: {
                Permission.READ_MESSAGES,
                Permission.SEND_MESSAGES,
                Permission.MANAGE_SUBSCRIPTION,
                Permission.VIEW_ANALYTICS
            },
            Role.MODERATOR: {
                Permission.READ_MESSAGES,
                Permission.SEND_MESSAGES,
                Permission.MANAGE_SUBSCRIPTION,
                Permission.VIEW_ANALYTICS,
                Permission.MODERATE_USERS
            },
            Role.ADMIN: {
                Permission.READ_MESSAGES,
                Permission.SEND_MESSAGES,
                Permission.MANAGE_SUBSCRIPTION,
                Permission.VIEW_ANALYTICS,
                Permission.ADMIN_ACCESS,
                Permission.MODERATE_USERS
            }
        }
        
    def has_permission(
        self, 
        user_role: Role, 
        permission: Permission
    ) -> bool:
        """Check if user role has permission."""
        role_permissions = self.role_permissions.get(user_role, set())
        return permission in role_permissions
        
    def get_user_permissions(self, user_role: Role) -> Set[Permission]:
        """Get all permissions for user role."""
        return self.role_permissions.get(user_role, set())
        
    def can_access_resource(
        self, 
        user_role: Role, 
        resource: str
    ) -> bool:
        """Check if user can access specific resource."""
        # Map resources to permissions
        resource_permissions = {
            'messages': Permission.READ_MESSAGES,
            'send_message': Permission.SEND_MESSAGES,
            'subscription': Permission.MANAGE_SUBSCRIPTION,
            'analytics': Permission.VIEW_ANALYTICS,
            'admin': Permission.ADMIN_ACCESS,
            'moderate': Permission.MODERATE_USERS
        }
        
        required_permission = resource_permissions.get(resource)
        if not required_permission:
            return False
            
        return self.has_permission(user_role, required_permission)


class SecurityException(Exception):
    """Security-related exception."""
    pass


class AuthenticationException(SecurityException):
    """Authentication exception."""
    pass


class AuthorizationException(SecurityException):
    """Authorization exception."""
    pass


# Global instances
auth_service = AuthenticationService("your-secret-key")
authz_service = AuthorizationService()
