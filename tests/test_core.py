"""
Unit Tests for SearchCRT
Run with: pytest tests/

Instale: pip install pytest pytest-cov
"""

import unittest
from auth_manager import AuthenticationManager
from config_manager import ConfigManager


class TestAuthenticationManager(unittest.TestCase):
    """Test authentication functionality"""
    
    def setUp(self):
        self.auth = AuthenticationManager('./etc/test_users.json')
    
    def test_create_user(self):
        """Test user creation"""
        self.auth.create_user('testuser', 'testpass', 'test@example.com', 'user')
        self.assertIn('testuser', self.auth.users)
    
    def test_verify_user_valid(self):
        """Test valid user verification"""
        self.auth.create_user('testuser', 'testpass', 'test@example.com', 'user')
        self.assertTrue(self.auth.verify_user('testuser', 'testpass'))
    
    def test_verify_user_invalid(self):
        """Test invalid user verification"""
        self.auth.create_user('testuser', 'testpass', 'test@example.com', 'user')
        self.assertFalse(self.auth.verify_user('testuser', 'wrongpass'))
    
    def test_session_creation(self):
        """Test session creation"""
        session_id = self.auth.create_session('testuser')
        self.assertTrue(self.auth.validate_session(session_id))
    
    def test_get_user_role(self):
        """Test get user role"""
        self.auth.create_user('testuser', 'testpass', 'test@example.com', 'admin')
        role = self.auth.get_user_role('testuser')
        self.assertEqual(role, 'admin')


class TestConfigurationManager(unittest.TestCase):
    """Test configuration functionality"""
    
    def setUp(self):
        self.config = ConfigManager('./config.ini')
    
    def test_load_config(self):
        """Test configuration loading"""
        self.assertIsNotNone(self.config.config)
    
    def test_get_database_config(self):
        """Test getting database config"""
        db_config = self.config.get_database_config()
        self.assertIn('host', db_config)
        self.assertIn('port', db_config)
        self.assertIn('database', db_config)
    
    def test_get_ui_config(self):
        """Test getting UI config"""
        ui_config = self.config.get_ui_config()
        self.assertIn('theme', ui_config)
        self.assertIn('window_width', ui_config)
        self.assertIn('window_height', ui_config)
    
    def test_get_feature_config(self):
        """Test getting feature config"""
        feature_config = self.config.get_feature_config()
        self.assertIn('enable_logging', feature_config)
        self.assertIn('enable_threading', feature_config)


if __name__ == '__main__':
    unittest.main()
