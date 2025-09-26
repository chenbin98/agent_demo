"""Unit tests for the config module."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import config


class TestConfig(unittest.TestCase):
    """Test cases for configuration management."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_config_success(self):
        """Test successful configuration loading."""
        with patch.dict(os.environ, {
            'DEEPSEEK_API_KEY': 'test-key',
            'DEEPSEEK_BASE_URL': 'https://test.api.com',
            'MODEL_NAME': 'test-model'
        }):
            config_obj = config.load_config()
            
            self.assertEqual(config_obj.api_key, 'test-key')
            self.assertEqual(config_obj.base_url, 'https://test.api.com')
            self.assertEqual(config_obj.model_name, 'test-model')

    def test_load_config_missing_key(self):
        """Test configuration loading with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError) as context:
                config.load_config()
            
            self.assertIn("Missing API key", str(context.exception))

    def test_load_config_defaults(self):
        """Test configuration loading with defaults."""
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key'}):
            config_obj = config.load_config()
            
            self.assertEqual(config_obj.base_url, "https://api.deepseek.com")
            self.assertEqual(config_obj.model_name, "deepseek-chat")
            self.assertEqual(config_obj.max_tokens, 4000)
            self.assertEqual(config_obj.temperature, 0.7)

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        config_obj = config.AgentConfig(
            api_key="test-key",
            base_url="https://test.api.com",
            model_name="test-model",
            max_tokens=1000,
            temperature=0.5,
            timeout_seconds=30,
            max_file_size_mb=5
        )
        
        # Should not raise any exception
        config.validate_config(config_obj)

    def test_validate_config_invalid_tokens(self):
        """Test configuration validation with invalid max_tokens."""
        config_obj = config.AgentConfig(
            api_key="test-key",
            max_tokens=0  # Invalid
        )
        
        with self.assertRaises(ValueError) as context:
            config.validate_config(config_obj)
        
        self.assertIn("max_tokens must be positive", str(context.exception))

    def test_validate_config_invalid_temperature(self):
        """Test configuration validation with invalid temperature."""
        config_obj = config.AgentConfig(
            api_key="test-key",
            temperature=3.0  # Invalid
        )
        
        with self.assertRaises(ValueError) as context:
            config.validate_config(config_obj)
        
        self.assertIn("temperature must be between 0 and 2", str(context.exception))

    def test_load_env_from_file(self):
        """Test loading environment variables from .env file."""
        env_file = self.temp_path / ".env"
        env_file.write_text("TEST_VAR=test_value\nANOTHER_VAR=another_value")
        
        with patch('config.Path.cwd', return_value=self.temp_path):
            config.load_env()
            
            self.assertEqual(os.environ.get("TEST_VAR"), "test_value")
            self.assertEqual(os.environ.get("ANOTHER_VAR"), "another_value")

    def test_load_env_with_comments(self):
        """Test loading environment variables with comments."""
        env_file = self.temp_path / ".env"
        env_file.write_text("# This is a comment\nTEST_VAR=test_value\n# Another comment")
        
        with patch('config.Path.cwd', return_value=self.temp_path):
            config.load_env()
            
            self.assertEqual(os.environ.get("TEST_VAR"), "test_value")

    def test_load_env_with_quotes(self):
        """Test loading environment variables with quoted values."""
        env_file = self.temp_path / ".env"
        env_file.write_text('TEST_VAR="quoted value"\nANOTHER_VAR=\'single quoted\'')
        
        with patch('config.Path.cwd', return_value=self.temp_path):
            config.load_env()
            
            self.assertEqual(os.environ.get("TEST_VAR"), "quoted value")
            self.assertEqual(os.environ.get("ANOTHER_VAR"), "single quoted")


if __name__ == "__main__":
    unittest.main()