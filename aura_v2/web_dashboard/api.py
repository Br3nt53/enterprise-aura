# aura_v2/web_dashboard/api.py
"""
AURA Dashboard API with defensive imports
Gracefully handles missing dependencies during setup
"""

import asyncio
from typing import Any, cast

# Defensive imports - handle missing dependencies gracefully

FASTAPI_AVAILABLE = False
APIRouter: Any = None  # type: ignore
HTTPException: Any = None  # type: ignore
BaseModel: Any = None  # type: ignore

try:
    from fastapi import APIRouter as RealAPIRouter
    from fastapi import HTTPException as RealHTTPException
    from pydantic import BaseModel as RealBaseModel

    APIRouter = cast(Any, RealAPIRouter)
    HTTPException = cast(Any, RealHTTPException)
    BaseModel = cast(Any, RealBaseModel)
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for when FastAPI isn't available
    class DummyBaseModel:
        pass

    class DummyAPIRouter:
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

    class DummyHTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

    APIRouter = cast(Any, DummyAPIRouter)  # type: ignore
    HTTPException = cast(Any, DummyHTTPException)  # type: ignore
    BaseModel = cast(Any, DummyBaseModel)  # type: ignore


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
        # Provide dummy router for fallback
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

    return router


# Create the router (will be None if dependencies not available)
router = create_router()


# Compatibility function for main.py import
def get_router():
    """Get the dashboard router, with fallback handling"""
    return router
