"""Unit tests for the tools module."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools


class TestTools(unittest.TestCase):
    """Test cases for tool functions."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_text_file(self):
        """Test text file creation."""
        file_path = str(self.temp_path / "test.txt")
        content = "Hello, World!"
        
        result = tools.create_text_file(file_path, content)
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "ok")
        self.assertTrue(Path(file_path).exists())
        self.assertEqual(Path(file_path).read_text(), content)

    def test_create_python_file(self):
        """Test Python file creation."""
        file_path = str(self.temp_path / "test")
        code = "print('Hello, World!')"
        
        result = tools.create_python_file(file_path, code)
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "ok")
        expected_path = self.temp_path / "test.py"
        self.assertTrue(expected_path.exists())
        self.assertEqual(expected_path.read_text(), code)

    def test_get_directory_structure(self):
        """Test directory structure retrieval."""
        # Create test files
        (self.temp_path / "file1.txt").write_text("content1")
        (self.temp_path / "subdir").mkdir()
        (self.temp_path / "subdir" / "file2.txt").write_text("content2")
        
        result = tools.get_directory_structure(str(self.temp_path))
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "ok")
        self.assertEqual(result_data["type"], "dir")
        self.assertEqual(result_data["name"], self.temp_path.name)

    def test_rename_file(self):
        """Test file renaming."""
        original_path = self.temp_path / "original.txt"
        original_path.write_text("content")
        
        new_path = str(self.temp_path / "renamed.txt")
        result = tools.rename_file(str(original_path), new_path)
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "ok")
        self.assertFalse(original_path.exists())
        self.assertTrue(Path(new_path).exists())

    def test_list_files(self):
        """Test file listing."""
        # Create test files
        (self.temp_path / "file1.txt").write_text("content1")
        (self.temp_path / "file2.py").write_text("content2")
        (self.temp_path / "subdir").mkdir()
        (self.temp_path / "subdir" / "file3.txt").write_text("content3")
        
        result = tools.list_files(str(self.temp_path), "*.txt", recursive=True)
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "ok")
        self.assertEqual(result_data["count"], 2)  # file1.txt and subdir/file3.txt

    def test_read_file_content(self):
        """Test file content reading."""
        file_path = self.temp_path / "test.txt"
        content = "Hello, World!"
        file_path.write_text(content)
        
        result = tools.read_file_content(str(file_path))
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "ok")
        self.assertEqual(result_data["content"], content)

    def test_create_directory(self):
        """Test directory creation."""
        dir_path = str(self.temp_path / "new_dir" / "nested")
        
        result = tools.create_directory(dir_path)
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "ok")
        self.assertTrue(Path(dir_path).exists())
        self.assertTrue(Path(dir_path).is_dir())

    def test_delete_file(self):
        """Test file deletion."""
        file_path = self.temp_path / "test.txt"
        file_path.write_text("content")
        
        result = tools.delete_file(str(file_path))
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "ok")
        self.assertFalse(file_path.exists())

    def test_get_host_info(self):
        """Test host information retrieval."""
        result = tools.get_host_info()
        result_data = json.loads(result)
        
        self.assertIn("system", result_data)
        self.assertIn("memory_gb", result_data)
        self.assertIn("cpu_count", result_data)

    @patch('tools.platform.system')
    def test_execute_command_windows(self, mock_system):
        """Test command execution on Windows."""
        mock_system.return_value = "Windows"
        
        # This should work on Windows, but we'll mock it
        with patch('tools.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "output"
            mock_run.return_value.stderr = ""
            
            result = tools.execute_command("echo hello")
            result_data = json.loads(result)
            
            self.assertEqual(result_data["status"], "ok")

    def test_error_handling(self):
        """Test error handling in tools."""
        # Test non-existent file
        result = tools.read_file_content("/non/existent/file.txt")
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "error")
        self.assertIn("file does not exist", result_data["message"])


if __name__ == "__main__":
    unittest.main()