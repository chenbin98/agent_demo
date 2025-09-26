"""Mac-specific tools and utilities."""

import json
import subprocess
import platform
from pathlib import Path
from typing import Any, Dict, List

from logger import get_logger, log_function_call, log_error


def _ok(message: str, **extra: Any) -> str:
    """Create success response."""
    payload: Dict[str, Any] = {"status": "ok", "message": message}
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _err(message: str, **extra: Any) -> str:
    """Create error response."""
    payload: Dict[str, Any] = {"status": "error", "message": message}
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def get_mac_info() -> str:
    """Get detailed Mac system information."""
    logger = get_logger()
    log_function_call("get_mac_info", {})
    
    if platform.system() != "Darwin":
        return _err("not running on macOS")
    
    try:
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
        
        # Get macOS version
        try:
            version_output = subprocess.check_output(
                ["sw_vers"], text=True, stderr=subprocess.DEVNULL
            )
            for line in version_output.split('\n'):
                if 'ProductVersion:' in line:
                    info["macos_version"] = line.split(':')[1].strip()
                elif 'ProductName:' in line:
                    info["macos_name"] = line.split(':')[1].strip()
        except Exception:
            info["macos_version"] = "Unknown"
            info["macos_name"] = "macOS"
        
        # Get CPU info
        try:
            cpu_info = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            info["cpu_model"] = cpu_info
        except Exception:
            info["cpu_model"] = "Unknown"
        
        # Get memory info
        try:
            memory_info = subprocess.check_output(
                ["sysctl", "-n", "hw.memsize"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            memory_bytes = int(memory_info)
            info["memory_gb"] = round(memory_bytes / (1024**3), 2)
        except Exception:
            info["memory_gb"] = "Unknown"
        
        logger.info("Retrieved Mac system information")
        return _ok("mac info retrieved", info=info)
        
    except Exception as e:
        log_error(e, "get_mac_info")
        return _err("failed to get mac info", error=str(e))


def get_installed_apps() -> str:
    """Get list of installed applications."""
    logger = get_logger()
    log_function_call("get_installed_apps", {})
    
    if platform.system() != "Darwin":
        return _err("not running on macOS")
    
    try:
        apps = []
        
        # Get applications from /Applications
        apps_dir = Path("/Applications")
        if apps_dir.exists():
            for app in apps_dir.iterdir():
                if app.suffix == ".app":
                    apps.append({
                        "name": app.stem,
                        "path": str(app),
                        "bundle_id": _get_bundle_id(app)
                    })
        
        # Sort by name
        apps.sort(key=lambda x: x["name"])
        
        logger.info(f"Found {len(apps)} installed applications")
        return _ok("installed apps retrieved", apps=apps, count=len(apps))
        
    except Exception as e:
        log_error(e, "get_installed_apps")
        return _err("failed to get installed apps", error=str(e))


def _get_bundle_id(app_path: Path) -> str:
    """Get bundle ID for an application."""
    try:
        plist_path = app_path / "Contents" / "Info.plist"
        if plist_path.exists():
            result = subprocess.check_output(
                ["defaults", "read", str(plist_path), "CFBundleIdentifier"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            return result
    except Exception:
        pass
    return "Unknown"


def get_brew_packages() -> str:
    """Get list of Homebrew packages."""
    logger = get_logger()
    log_function_call("get_brew_packages", {})
    
    if platform.system() != "Darwin":
        return _err("not running on macOS")
    
    try:
        # Check if brew is installed
        brew_check = subprocess.run(
            ["which", "brew"], 
            capture_output=True, text=True
        )
        if brew_check.returncode != 0:
            return _err("Homebrew not installed")
        
        # Get installed packages
        result = subprocess.check_output(
            ["brew", "list", "--formula"], 
            text=True, stderr=subprocess.DEVNULL
        )
        
        packages = [line.strip() for line in result.split('\n') if line.strip()]
        
        logger.info(f"Found {len(packages)} Homebrew packages")
        return _ok("brew packages retrieved", packages=packages, count=len(packages))
        
    except Exception as e:
        log_error(e, "get_brew_packages")
        return _err("failed to get brew packages", error=str(e))


def execute_mac_command(command: str, timeout_sec: int = 60) -> str:
    """Execute a macOS-specific command."""
    logger = get_logger()
    log_function_call("execute_mac_command", {"command": command})
    
    if platform.system() != "Darwin":
        return _err("not running on macOS")
    
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
        
        logger.info(f"Executed Mac command: {command[:50]}...")
        return json.dumps(
            {
                "status": "ok" if completed.returncode == 0 else "error",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "platform": "macOS",
            },
            ensure_ascii=False,
            indent=2,
        )
    except subprocess.TimeoutExpired:
        log_error(Exception("Command timeout"), f"execute_mac_command({command})")
        return _err("command timed out", command=command, timeout_sec=timeout_sec)
    except Exception as e:
        log_error(e, f"execute_mac_command({command})")
        return _err("failed to execute command", error=str(e), command=command)


def get_mac_permissions() -> str:
    """Get macOS permission status for common operations."""
    logger = get_logger()
    log_function_call("get_mac_permissions", {})
    
    if platform.system() != "Darwin":
        return _err("not running on macOS")
    
    try:
        permissions = {}
        
        # Check file system permissions
        try:
            test_file = Path("/tmp/agent_test_permissions")
            test_file.write_text("test")
            test_file.unlink()
            permissions["file_system_write"] = True
        except Exception:
            permissions["file_system_write"] = False
        
        # Check network permissions (simplified)
        try:
            subprocess.run(
                ["ping", "-c", "1", "8.8.8.8"], 
                capture_output=True, timeout=5
            )
            permissions["network_access"] = True
        except Exception:
            permissions["network_access"] = False
        
        logger.info("Retrieved Mac permissions status")
        return _ok("mac permissions retrieved", permissions=permissions)
        
    except Exception as e:
        log_error(e, "get_mac_permissions")
        return _err("failed to get mac permissions", error=str(e))


def create_mac_shortcut(script_path: str, shortcut_name: str) -> str:
    """Create a macOS application shortcut for a script."""
    logger = get_logger()
    log_function_call("create_mac_shortcut", {"script_path": script_path, "shortcut_name": shortcut_name})
    
    if platform.system() != "Darwin":
        return _err("not running on macOS")
    
    try:
        script_file = Path(script_path)
        if not script_file.exists():
            return _err("script file does not exist", script_path=script_path)
        
        # Create a simple .command file that can be double-clicked
        shortcut_path = Path.home() / "Desktop" / f"{shortcut_name}.command"
        
        # Make the script executable
        script_file.chmod(0o755)
        
        # Create the shortcut
        shortcut_content = f"""#!/bin/bash
cd "{script_file.parent}"
"{script_file}"
"""
        shortcut_path.write_text(shortcut_content)
        shortcut_path.chmod(0o755)
        
        logger.info(f"Created Mac shortcut: {shortcut_path}")
        return _ok("mac shortcut created", shortcut_path=str(shortcut_path))
        
    except Exception as e:
        log_error(e, f"create_mac_shortcut({script_path})")
        return _err("failed to create mac shortcut", error=str(e), script_path=script_path)


if __name__ == "__main__":
    print(get_mac_info())