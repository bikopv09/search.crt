"""
Authentication Module
Handles user authentication and authorization for SearchCRT
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AuthenticationManager:
    def __init__(self, users_file='./etc/users.json'):
        self.users_file = users_file
        self.users = {}
        self.sessions = {}
        self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
                logger.info(f"Loaded {len(self.users)} users from {self.users_file}")
            except Exception as e:
                logger.error(f"Error loading users: {e}")
                self.users = {}
        else:
            logger.warning(f"Users file not found: {self.users_file}")
    
    def save_users(self):
        """Save users to JSON file"""
        try:
            Path(self.users_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=4)
            logger.info("Users saved successfully")
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email='', role='user'):
        """Create a new user"""
        if username in self.users:
            raise ValueError(f"User '{username}' already exists")
        
        self.users[username] = {
            'password': self.hash_password(password),
            'email': email,
            'role': role,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'active': True
        }
        self.save_users()
        logger.info(f"User '{username}' created successfully")
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        if username not in self.users:
            logger.warning(f"Login attempt for non-existent user: {username}")
            return False
        
        user = self.users[username]
        if not user.get('active', False):
            logger.warning(f"Login attempt for inactive user: {username}")
            return False
        
        if user['password'] == self.hash_password(password):
            user['last_login'] = datetime.now().isoformat()
            self.save_users()
            logger.info(f"User '{username}' authenticated successfully")
            return True
        
        logger.warning(f"Failed login attempt for user: {username}")
        return False
    
    def create_session(self, username, session_timeout=3600):
        """Create a user session"""
        session_id = hashlib.sha256(f"{username}{datetime.now()}".encode()).hexdigest()
        
        self.sessions[session_id] = {
            'username': username,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=session_timeout),
            'active': True
        }
        
        logger.info(f"Session created for user '{username}': {session_id}")
        return session_id
    
    def validate_session(self, session_id):
        """Validate a session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        if not session['active'] or datetime.now() > session['expires_at']:
            session['active'] = False
            return False
        
        return True
    
    def get_user_role(self, username):
        """Get user role"""
        if username in self.users:
            return self.users[username].get('role', 'user')
        return None
    
    def list_users(self):
        """List all users"""
        return list(self.users.keys())
    
    def delete_user(self, username):
        """Delete a user"""
        if username in self.users:
            del self.users[username]
            self.save_users()
            logger.info(f"User '{username}' deleted successfully")
        else:
            raise ValueError(f"User '{username}' not found")

# Global authentication instance
auth_manager = AuthenticationManager()
