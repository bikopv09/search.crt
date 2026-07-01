"""
SearchCRT Configuration Manager
Manages all configuration settings from config.ini
"""

import configparser
import os
import logging
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config_path = config_file
        self.load_config()
        self.setup_logging()
    
    def load_config(self):
        """Load configuration from INI file"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
    
    def get(self, section, key, default=None):
        """Get configuration value"""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def get_int(self, section, key, default=None):
        """Get integer configuration value"""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def get_bool(self, section, key, default=None):
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def setup_logging(self):
        """Setup logging configuration"""
        if self.get_bool('Features', 'enable_logging', True):
            log_dir = Path('./logs')
            log_dir.mkdir(exist_ok=True)
            
            log_file = self.get('Features', 'log_file', './logs/searchcrt.log')
            log_level = self.get('Features', 'log_level', 'INFO')
            
            logging.basicConfig(
                level=getattr(logging, log_level),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
    
    def get_database_config(self):
        """Get MongoDB configuration"""
        return {
            'host': self.get('Database', 'mongodb_host', 'localhost'),
            'port': self.get_int('Database', 'mongodb_port', 27017),
            'database': self.get('Database', 'database_name', 'searchcrt'),
            'username': self.get('Database', 'mongodb_username', ''),
            'password': self.get('Database', 'mongodb_password', ''),
            'auth_source': self.get('Database', 'mongodb_auth_source', 'admin'),
        }
    
    def get_ui_config(self):
        """Get UI configuration"""
        return {
            'theme': self.get('UI', 'theme', 'dark'),
            'window_width': self.get_int('UI', 'window_width', 600),
            'window_height': self.get_int('UI', 'window_height', 400),
            'bg_color': self.get('UI', 'bg_color', '#0A1D3A'),
            'panel_bg': self.get('UI', 'panel_bg', '#102F4D'),
            'fg_color': self.get('UI', 'fg_color', '#4DD0E1'),
            'fg_text': self.get('UI', 'fg_text', '#FFFFFF'),
        }
    
    def get_feature_config(self):
        """Get feature configuration"""
        return {
            'enable_logging': self.get_bool('Features', 'enable_logging', True),
            'search_history_enabled': self.get_bool('Features', 'search_history_enabled', True),
            'enable_threading': self.get_bool('Features', 'enable_threading', True),
            'max_workers': self.get_int('Features', 'max_workers', 4),
            'result_limit': self.get_int('Features', 'result_limit', 500),
        }
    
    def get_auth_config(self):
        """Get authentication configuration"""
        return {
            'enable_auth': self.get_bool('Authentication', 'enable_auth', False),
            'auth_type': self.get('Authentication', 'auth_type', 'local'),
            'session_timeout': self.get_int('Authentication', 'session_timeout', 3600),
        }

# Global configuration instance
config_manager = ConfigManager()
