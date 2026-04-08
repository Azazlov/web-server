"""
FileShare Local v2.1 - Configuration Module
Handles loading and saving application configuration.
"""
import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')

DEFAULT_CONFIG = {
    'server_port': 80,
    'max_upload_size_mb': 100,
    'allow_registration': True,
    'debug_mode': False,
    'production_mode': False
}


class Config:
    """Application configuration manager."""
    
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Load configuration from JSON file. Create it if missing."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    self._config.update(loaded)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                self.save()
        else:
            print("Config file not found. Creating config.json with default settings...")
            self.save()
            print(f"  Created: {CONFIG_FILE}")
        return self._config
    
    def save(self):
        """Save configuration to JSON file."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value."""
        self._config[key] = value
    
    @property
    def server_port(self):
        return self._config.get('server_port', DEFAULT_CONFIG['server_port'])
    
    @property
    def max_upload_size_mb(self):
        return self._config.get('max_upload_size_mb', DEFAULT_CONFIG['max_upload_size_mb'])
    
    @property
    def max_upload_size_bytes(self):
        return self.max_upload_size_mb * 1024 * 1024
    
    @property
    def allow_registration(self):
        return self._config.get('allow_registration', DEFAULT_CONFIG['allow_registration'])
    
    @property
    def debug_mode(self):
        return self._config.get('debug_mode', DEFAULT_CONFIG['debug_mode'])

    @property
    def production_mode(self):
        return self._config.get('production_mode', DEFAULT_CONFIG['production_mode'])

    def toggle_registration(self):
        """Toggle registration setting and save."""
        self._config['allow_registration'] = not self._config['allow_registration']
        self.save()
        return self._config['allow_registration']
    
    def to_dict(self):
        """Return configuration as dictionary."""
        return self._config.copy()


# Global configuration instance
config = Config()
