import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import psutil
from logger import get_logger, log_function_call, log_error


def _ok(message: str, **extra: Any) -> str:
    payload: Dict[str, Any] = {"status": "ok", "message": message}
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _err(message: str, **extra: Any) -> str:
    payload: Dict[str, Any] = {"status": "error", "message": message}
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def create_text_file(file_path: str, content: str) -> str:
    """Create or overwrite a text file with UTF-8 content.

    Args:
      file_path: Target file path, directories created as needed.
      content: Text content to write.

    Returns a JSON string indicating status and path.
    """
    logger = get_logger()
    log_function_call("create_text_file", {"file_path": file_path, "content_length": len(content)})
    
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        
        logger.info(f"Created text file: {path}")
        return _ok("text file written", path=str(path.resolve()))
    except Exception as e:
        log_error(e, f"create_text_file({file_path})")
        return _err("failed to write text file", error=str(e), path=file_path)


def create_python_file(file_path: str, code: str) -> str:
    """Create or overwrite a Python file with UTF-8 code.

    If the path has no `.py` suffix, it will be added.
    """
    try:
        path = Path(file_path)
        if path.suffix != ".py":
            path = path.with_suffix(".py")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")
        return _ok("python file written", path=str(path.resolve()))
    except Exception as e:
        return _err("failed to write python file", error=str(e), path=file_path)


def get_directory_structure(root: str = ".") -> str:
    """Return a JSON tree of the directory structure.

    Args:
      root: Root directory to inspect.
    """
    root_path = Path(root)
    if not root_path.exists():
        return _err("root does not exist", root=str(root_path))

    def walk(p: Path) -> Dict[str, Any]:
        if p.is_dir():
            children: List[Dict[str, Any]] = []
            for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                # Skip common noisy directories
                if child.name in {".git", "__pycache__", "node_modules"}:
                    continue
                children.append(walk(child))
            return {"type": "dir", "name": p.name, "path": str(p), "children": children}
        else:
            return {"type": "file", "name": p.name, "path": str(p)}

    try:
        tree = walk(root_path)
        return json.dumps(tree, ensure_ascii=False, indent=2)
    except Exception as e:
        return _err("failed to build structure", error=str(e), root=str(root_path))


def rename_file(old_path: str, new_path: str) -> str:
    """Rename or move a file or directory."""
    try:
        src = Path(old_path)
        dst = Path(new_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        return _ok("renamed", src=str(src), dst=str(dst))
    except Exception as e:
        return _err("failed to rename", error=str(e), src=old_path, dst=new_path)


def execute_command(command: str, timeout_sec: int = 60) -> str:
    """Execute a shell command and return output.
    
    Supports both Unix/macOS and Windows systems.
    """
    try:
        # Use appropriate shell based on platform
        shell_cmd = command
        if platform.system().lower() == "windows":
            shell_cmd = f"cmd /c {command}"
        
        completed = subprocess.run(
            shell_cmd,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            encoding="utf-8",
            errors="replace",
        )
        return json.dumps(
            {
                "status": "ok" if completed.returncode == 0 else "error",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "platform": platform.system(),
            },
            ensure_ascii=False,
            indent=2,
        )
    except subprocess.TimeoutExpired:
        return _err("command timed out", command=command, timeout_sec=timeout_sec)
    except Exception as e:
        return _err("failed to execute command", error=str(e), command=command)


def execute_windows_command(command: str, timeout_sec: int = 60) -> str:
    """Execute a Windows CMD command and return output.

    On non-Windows systems, returns an error message.
    """
    if platform.system().lower() != "windows":
        return _err("not running on windows", command=command)

    try:
        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            encoding="utf-8",
            errors="replace",
        )
        return json.dumps(
            {
                "status": "ok" if completed.returncode == 0 else "error",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            ensure_ascii=False,
            indent=2,
        )
    except subprocess.TimeoutExpired:
        return _err("command timed out", command=command, timeout_sec=timeout_sec)
    except Exception as e:
        return _err("failed to execute command", error=str(e), command=command)


def get_host_info() -> str:
    """Get host information as a JSON string."""
    info: Dict[str, Any] = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
    }

    cpu_count = psutil.cpu_count(logical=True)
    info["cpu_count"] = cpu_count if cpu_count is not None else -1

    # Best-effort CPU model on macOS; ignore failures on other OSes
    try:
        cpu_model = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"]
        ).decode().strip()
        info["cpu_model"] = cpu_model
    except Exception:
        info["cpu_model"] = "Unknown"

    return json.dumps(info, ensure_ascii=False, indent=2)


def list_files(directory: str = ".", pattern: str = "*", recursive: bool = True) -> str:
    """List files in a directory with optional pattern matching."""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return _err("directory does not exist", directory=directory)
        
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))
        
        file_list = []
        for file_path in sorted(files):
            if file_path.is_file():
                stat = file_path.stat()
                file_list.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime,
                    "extension": file_path.suffix
                })
        
        return _ok("files listed", files=file_list, count=len(file_list))
    except Exception as e:
        return _err("failed to list files", error=str(e), directory=directory)


def read_file_content(file_path: str, max_size_mb: int = 10) -> str:
    """Read file content with size limit protection."""
    try:
        path = Path(file_path)
        if not path.exists():
            return _err("file does not exist", file_path=file_path)
        
        if not path.is_file():
            return _err("path is not a file", file_path=file_path)
        
        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return _err(f"file too large ({size_mb:.1f}MB > {max_size_mb}MB)", file_path=file_path)
        
        content = path.read_text(encoding="utf-8", errors="replace")
        return _ok("file read", content=content, size_mb=round(size_mb, 2))
    except Exception as e:
        return _err("failed to read file", error=str(e), file_path=file_path)


def create_directory(dir_path: str) -> str:
    """Create a directory and all parent directories."""
    try:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return _ok("directory created", path=str(path.resolve()))
    except Exception as e:
        return _err("failed to create directory", error=str(e), dir_path=dir_path)


def delete_file(file_path: str) -> str:
    """Delete a file or empty directory."""
    try:
        path = Path(file_path)
        if not path.exists():
            return _err("file does not exist", file_path=file_path)
        
        if path.is_file():
            path.unlink()
            return _ok("file deleted", path=str(path))
        elif path.is_dir():
            if any(path.iterdir()):
                return _err("directory is not empty", file_path=file_path)
            path.rmdir()
            return _ok("directory deleted", path=str(path))
        else:
            return _err("unknown file type", file_path=file_path)
    except Exception as e:
        return _err("failed to delete file", error=str(e), file_path=file_path)


def get_system_resources() -> str:
    """Get current system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": round((disk.used / disk.total) * 100, 2)
            }
        }
        
        return _ok("system resources", resources=resources)
    except Exception as e:
        return _err("failed to get system resources", error=str(e))


if __name__ == "__main__":
    print(get_host_info())
