# aura_v2/web_dashboard/api.py
"""
AURA Dashboard API with defensive imports
Gracefully handles missing dependencies during setup
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Defensive imports - handle missing dependencies gracefully
FASTAPI_AVAILABLE = False
APIRouter = None
HTTPException = None

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for when FastAPI isn't available
    class BaseModel:
        pass

    class APIRouter:
        def __init__(self, *args, **kwargs):
            pass

        def post(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def get(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


class CommandRequest(BaseModel):
    command: str = ""
    working_directory: str = "."


class CommandResponse(BaseModel):
    success: bool = False
    output: str = ""
    error: str = ""
    exit_code: int = -1
    duration_ms: float = 0.0


class SystemStatusResponse(BaseModel):
    python: str = "unknown"
    pytest: str = "unknown"
    dependencies: str = "unknown"
    server: str = "unknown"
    aura_imports: str = "unknown"


def create_router():
    """Create dashboard router only if dependencies are available"""
    if not FASTAPI_AVAILABLE:
        return None

    router = APIRouter(prefix="/dashboard", tags=["dashboard"])

    @router.post("/execute", response_model=CommandResponse)
    async def execute_command(request: CommandRequest):
        """Execute a shell command and return the result"""
        import time

        start_time = time.time()

        try:
            # Security: Only allow safe commands for development
            safe_commands = [
                "python",
                "pytest",
                "pip",
                "uv",
                "curl",
                "ruff",
                "black",
                "mypy",
                "docker",
                "git",
                "npm",
                "node",
                "yarn",
                "poetry",
                "ls",
                "cat",
                "which",
            ]

            command_parts = request.command.split()
            if not command_parts:
                raise HTTPException(status_code=400, detail="Empty command")

            if command_parts[0] not in safe_commands:
                raise HTTPException(
                    status_code=400,
                    detail=f"Command '{command_parts[0]}' not allowed. Allowed: {safe_commands}",
                )

            # Execute the command
            process = await asyncio.create_subprocess_shell(
                request.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=request.working_directory,
            )

            stdout, stderr = await process.communicate()
            duration_ms = (time.time() - start_time) * 1000

            return CommandResponse(
                success=process.returncode == 0,
                output=stdout.decode("utf-8") if stdout else "",
                error=stderr.decode("utf-8") if stderr else "",
                exit_code=process.returncode or 0,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CommandResponse(
                success=False,
                output="",
                error=str(e),
                exit_code=-1,
                duration_ms=duration_ms,
            )

    @router.get("/system-status", response_model=SystemStatusResponse)
    async def get_system_status():
        """Check system status for various components"""

        async def check_command(cmd: str) -> str:
            try:
                process = await asyncio.create_subprocess_shell(
                    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    output = stdout.decode().strip() if stdout else "ok"
                    # Get first word for version info
                    first_word = output.split()[0] if output.split() else "ok"
                    return f"available: {first_word}"
                else:
                    error_msg = stderr.decode().strip() if stderr else "command failed"
                    return f"error: {error_msg[:50]}..."  # Truncate long errors
            except Exception as e:
                return f"unavailable: {str(e)[:50]}..."

        # Check various system components
        status = SystemStatusResponse(
            python=await check_command("python --version"),
            pytest=await check_command("pytest --version"),
            dependencies=await check_command("pip show fastapi"),
            server=await check_command(
                "curl -f http://localhost:8000/health --connect-timeout 2 --max-time 5"
            ),
            aura_imports=await check_command(
                "python -c \"import aura_v2; print('v' + aura_v2.__version__)\""
            ),
        )

        return status

    @router.get("/file-structure")
    async def get_file_structure():
        """Get the current file structure for verification"""

        def scan_directory(
            path: Path, max_depth: int = 3, current_depth: int = 0
        ) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {}

            structure = {}
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith("."):
                        continue

                    if item.is_file() and item.suffix in [
                        ".py",
                        ".toml",
                        ".yml",
                        ".yaml",
                        ".md",
                    ]:
                        try:
                            structure[str(item)] = {
                                "type": "file",
                                "size": item.stat().st_size,
                                "modified": item.stat().st_mtime,
                            }
                        except (OSError, PermissionError):
                            pass
                    elif item.is_dir() and item.name not in [
                        "__pycache__",
                        ".git",
                        "node_modules",
                        ".pytest_cache",
                    ]:
                        try:
                            structure[str(item)] = {
                                "type": "directory",
                                "children": scan_directory(item, max_depth, current_depth + 1),
                            }
                        except (OSError, PermissionError):
                            pass
            except (OSError, PermissionError):
                pass

            return structure

        try:
            project_root = Path.cwd()
            return scan_directory(project_root)
        except Exception as e:
            return {"error": f"Failed to scan directory: {e}"}

    @router.post("/run-tests")
    async def run_specific_tests(test_path: str):
        """Run specific test files or directories"""

        if not test_path.startswith("tests/"):
            raise HTTPException(status_code=400, detail="Test path must start with 'tests/'")

        test_file = Path(test_path)
        if not test_file.exists():
            raise HTTPException(status_code=404, detail=f"Test file not found: {test_path}")

        command = f"pytest {test_path} -v --tb=short"

        request = CommandRequest(command=command)
        return await execute_command(request)

    return router


# Create the router (will be None if dependencies not available)
router = create_router()


# Compatibility function for main.py import
def get_router():
    """Get the dashboard router, with fallback handling"""
    return router
