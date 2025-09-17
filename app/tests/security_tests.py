"""
Comprehensive security testing suite.
"""

import pytest
import time

from shared.security.authentication import (
    AuthenticationService, 
    AuthorizationService, 
    Permission, 
    Role
)
from shared.security.encryption import EncryptionService, PasswordHasher
from shared.security.attack_protection import AttackDetector, AttackType
from shared.security.monitoring import SecurityMonitor, SecurityLevel
from shared.security.blocking import BlockingService, BlockReason, BlockType


class TestAuthenticationSecurity:
    """Test authentication security."""
    
    def test_password_hashing(self):
        """Test password hashing security."""
        hasher = PasswordHasher()
        password = "test_password_123"
        
        # Hash password
        hashed = hasher.hash_password(password)
        
        # Verify password
        assert hasher.verify_password(password, hashed)
        assert not hasher.verify_password("wrong_password", hashed)
        
        # Ensure different salts produce different hashes
        hashed2 = hasher.hash_password(password)
        assert hashed != hashed2
        
    def test_session_security(self):
        """Test session security."""
        auth_service = AuthenticationService("test_secret")
        
        # Create session
        session = auth_service.create_session(123, "192.168.1.1")
        assert session.user_id == 123
        assert session.is_active
        
        # Validate session
        validated_session = auth_service.validate_session(session.session_id)
        assert validated_session is not None
        assert validated_session.user_id == 123
        
        # Revoke session
        auth_service.revoke_session(session.session_id)
        assert auth_service.validate_session(session.session_id) is None
        
    def test_failed_attempt_blocking(self):
        """Test failed attempt blocking."""
        auth_service = AuthenticationService("test_secret")
        
        # Record failed attempts
        for _ in range(4):
            auth_service.record_failed_attempt(123)
            
        assert not auth_service.is_user_blocked(123)
        
        # 5th attempt should block user
        auth_service.record_failed_attempt(123)
        assert auth_service.is_user_blocked(123)
        
    def test_token_security(self):
        """Test token security."""
        auth_service = AuthenticationService("test_secret")
        
        # Create token
        token = auth_service.create_access_token(123, [Permission.READ_MESSAGES])
        assert token.user_id == 123
        
        # Validate token
        validated_token = auth_service.validate_token(token.token)
        assert validated_token is not None
        assert validated_token.user_id == 123
        
        # Revoke token
        auth_service.revoke_token(token.token)
        assert auth_service.validate_token(token.token) is None


class TestEncryptionSecurity:
    """Test encryption security."""
    
    def test_string_encryption(self):
        """Test string encryption/decryption."""
        encryption_service = EncryptionService()
        plaintext = "sensitive_data_123"
        
        # Encrypt
        encrypted = encryption_service.encrypt_string(plaintext)
        assert encrypted != plaintext
        assert len(encrypted) > len(plaintext)
        
        # Decrypt
        decrypted = encryption_service.decrypt_string(encrypted)
        assert decrypted == plaintext
        
    def test_dict_encryption(self):
        """Test dictionary encryption/decryption."""
        encryption_service = EncryptionService()
        data = {"user_id": 123, "email": "test@example.com"}
        
        # Encrypt
        encrypted = encryption_service.encrypt_dict(data)
        assert isinstance(encrypted, str)
        
        # Decrypt
        decrypted = encryption_service.decrypt_dict(encrypted)
        assert decrypted == data
        
    def test_encryption_consistency(self):
        """Test encryption consistency."""
        encryption_service = EncryptionService()
        plaintext = "test_data"
        
        # Same input should produce different encrypted output (due to random IV)
        encrypted1 = encryption_service.encrypt_string(plaintext)
        encrypted2 = encryption_service.encrypt_string(plaintext)
        assert encrypted1 != encrypted2
        
        # But both should decrypt to same plaintext
        assert encryption_service.decrypt_string(encrypted1) == plaintext
        assert encryption_service.decrypt_string(encrypted2) == plaintext


class TestAttackProtection:
    """Test attack protection."""
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        detector = AttackDetector()
        
        # Test SQL injection patterns
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        for malicious_input in malicious_inputs:
            attacks = detector.detect_attacks(malicious_input)
            assert len(attacks) > 0
            assert any(attack.attack_type == AttackType.SQL_INJECTION for attack in attacks)
            
    def test_xss_detection(self):
        """Test XSS detection."""
        detector = AttackDetector()
        
        # Test XSS patterns
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>"
        ]
        
        for malicious_input in malicious_inputs:
            attacks = detector.detect_attacks(malicious_input)
            assert len(attacks) > 0
            assert any(attack.attack_type == AttackType.XSS for attack in attacks)
            
    def test_input_sanitization(self):
        """Test input sanitization."""
        detector = AttackDetector()
        
        malicious_input = "<script>alert('XSS')</script>'; DROP TABLE users; --"
        sanitized = detector.sanitize_input(malicious_input)
        
        # Should remove dangerous content
        assert "<script>" not in sanitized
        assert "DROP TABLE" not in sanitized
        assert "alert" not in sanitized


class TestSecurityMonitoring:
    """Test security monitoring."""
    
    def test_alert_creation(self):
        """Test security alert creation."""
        monitor = SecurityMonitor()
        
        alert = monitor.create_alert(
            level=SecurityLevel.HIGH,
            category="Attack Detection",
            description="SQL injection attempt detected",
            user_id=123,
            ip_address="192.168.1.1"
        )
        
        assert alert.level == SecurityLevel.HIGH
        assert alert.category == "Attack Detection"
        assert alert.user_id == 123
        
    def test_metrics_collection(self):
        """Test security metrics collection."""
        monitor = SecurityMonitor()
        
        # Record some metrics
        monitor.metrics.record_attack("sql_injection")
        monitor.metrics.record_attack("xss")
        monitor.metrics.record_blocked_user()
        
        metrics = monitor.metrics.get_metrics()
        assert metrics['total_attacks'] == 2
        assert metrics['blocked_users'] == 1
        assert 'sql_injection' in metrics['attacks_by_type']
        
    def test_security_score_calculation(self):
        """Test security score calculation."""
        monitor = SecurityMonitor()
        
        # Initial score should be 100
        assert monitor.metrics.calculate_security_score() == 100
        
        # Record attacks to lower score
        for _ in range(10):
            monitor.metrics.record_attack("test_attack")
            
        score = monitor.metrics.calculate_security_score()
        assert score < 100
        assert score >= 0


class TestBlockingSystem:
    """Test blocking system."""
    
    def test_user_blocking(self):
        """Test user blocking."""
        blocking_service = BlockingService()
        
        # Block user
        block_record = blocking_service.block_user(
            user_id=123,
            reason=BlockReason.SUSPICIOUS_ACTIVITY,
            block_type=BlockType.TEMPORARY,
            duration_hours=1
        )
        
        assert blocking_service.is_user_blocked(123)
        assert block_record.user_id == 123
        
        # Unblock user
        blocking_service.unblock_user(123)
        assert not blocking_service.is_user_blocked(123)
        
    def test_ip_blocking(self):
        """Test IP blocking."""
        blocking_service = BlockingService()
        
        # Block IP
        block_record = blocking_service.block_ip(
            ip_address="192.168.1.1",
            reason=BlockReason.ATTACK_ATTEMPT,
            block_type=BlockType.TEMPORARY,
            duration_hours=1
        )
        
        assert blocking_service.is_ip_blocked("192.168.1.1")
        assert block_record.ip_address == "192.168.1.1"
        
        # Unblock IP
        blocking_service.unblock_ip("192.168.1.1")
        assert not blocking_service.is_ip_blocked("192.168.1.1")
        
    def test_violation_tracking(self):
        """Test violation tracking."""
        blocking_service = BlockingService()
        
        # Record violations
        for _ in range(3):
            blocking_service.record_violation(123, "spam")
            
        assert blocking_service.get_user_violations(123) == 3
        
        # Clear violations
        blocking_service.clear_violations(123)
        assert blocking_service.get_user_violations(123) == 0


class TestAuthorizationSecurity:
    """Test authorization security."""
    
    def test_permission_checking(self):
        """Test permission checking."""
        authz_service = AuthorizationService()
        
        # Test user permissions
        assert authz_service.has_permission(Role.USER, Permission.READ_MESSAGES)
        assert authz_service.has_permission(Role.USER, Permission.SEND_MESSAGES)
        assert not authz_service.has_permission(Role.USER, Permission.ADMIN_ACCESS)
        
        # Test admin permissions
        assert authz_service.has_permission(Role.ADMIN, Permission.ADMIN_ACCESS)
        assert authz_service.has_permission(Role.ADMIN, Permission.MODERATE_USERS)
        
    def test_resource_access(self):
        """Test resource access control."""
        authz_service = AuthorizationService()
        
        # Test resource access
        assert authz_service.can_access_resource(Role.USER, "messages")
        assert authz_service.can_access_resource(Role.USER, "send_message")
        assert not authz_service.can_access_resource(Role.USER, "admin")
        
        assert authz_service.can_access_resource(Role.ADMIN, "admin")
        assert authz_service.can_access_resource(Role.ADMIN, "moderate")


class TestSecurityIntegration:
    """Test security system integration."""
    
    def test_end_to_end_security_flow(self):
        """Test end-to-end security flow."""
        # Initialize services
        auth_service = AuthenticationService("test_secret")
        detector = AttackDetector()
        monitor = SecurityMonitor()
        blocking_service = BlockingService()
        
        # Simulate attack attempt
        malicious_input = "<script>alert('XSS')</script>"
        attacks = detector.detect_attacks(malicious_input, user_id=123)
        
        # Should detect attack
        assert len(attacks) > 0
        
        # Create security alert
        alert = monitor.create_alert(
            level=SecurityLevel.HIGH,
            category="XSS Attack",
            description="XSS attack detected",
            user_id=123
        )
        
        # Block user
        blocking_service.block_user(
            user_id=123,
            reason=BlockReason.ATTACK_ATTEMPT,
            block_type=BlockType.TEMPORARY,
            duration_hours=1
        )
        
        # Verify user is blocked
        assert blocking_service.is_user_blocked(123)
        
    def test_security_metrics_integration(self):
        """Test security metrics integration."""
        monitor = SecurityMonitor()
        
        # Simulate various security events
        monitor.metrics.record_attack("sql_injection")
        monitor.metrics.record_attack("xss")
        monitor.metrics.record_blocked_user()
        monitor.metrics.record_failed_login()
        
        # Get dashboard data
        dashboard_data = monitor.get_security_dashboard_data()
        
        assert dashboard_data['metrics']['total_attacks'] == 2
        assert dashboard_data['metrics']['blocked_users'] == 1
        assert dashboard_data['metrics']['failed_logins'] == 1
        assert 'security_score' in dashboard_data['metrics']


# Performance tests
class TestSecurityPerformance:
    """Test security system performance."""
    
    def test_encryption_performance(self):
        """Test encryption performance."""
        encryption_service = EncryptionService()
        
        start_time = time.time()
        
        # Encrypt/decrypt multiple strings
        for i in range(100):
            plaintext = f"test_data_{i}"
            encrypted = encryption_service.encrypt_string(plaintext)
            decrypted = encryption_service.decrypt_string(encrypted)
            assert decrypted == plaintext
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time
        assert duration < 1.0  # Less than 1 second for 100 operations
        
    def test_attack_detection_performance(self):
        """Test attack detection performance."""
        detector = AttackDetector()
        
        start_time = time.time()
        
        # Test multiple attack patterns
        test_inputs = [
            "<script>alert('XSS')</script>",
            "'; DROP TABLE users; --",
            "javascript:alert('XSS')",
            "UNION SELECT * FROM users",
            "normal_text_without_attacks"
        ] * 20  # 100 total tests
        
        for test_input in test_inputs:
            detector.detect_attacks(test_input)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time
        assert duration < 0.5  # Less than 0.5 seconds for 100 detections


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
