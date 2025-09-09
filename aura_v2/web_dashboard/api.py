# aura_v2/web_dashboard/api.py
import asyncio
import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class CommandRequest(BaseModel):
    command: str
    working_directory: str = "."

class CommandResponse(BaseModel):
    success: bool
    output: str
    error: str
    exit_code: int
    duration_ms: float

class SystemStatusResponse(BaseModel):
    python: str
    pytest: str
    dependencies: str
    server: str
    aura_imports: str

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Execute a shell command and return the result"""
    import time
    start_time = time.time()
    
    try:
        # Security: Only allow safe commands for development
        safe_commands = [
            'python', 'pytest', 'pip', 'uv', 'curl', 'ruff', 'black', 'mypy',
            'docker', 'git', 'npm', 'node', 'yarn', 'poetry'
        ]
        
        command_parts = request.command.split()
        if not command_parts or command_parts[0] not in safe_commands:
            raise HTTPException(
                status_code=400, 
                detail=f"Command not allowed. Allowed: {safe_commands}"
            )
        
        # Execute the command
        process = await asyncio.create_subprocess_shell(
            request.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=request.working_directory
        )
        
        stdout, stderr = await process.communicate()
        duration_ms = (time.time() - start_time) * 1000
        
        return CommandResponse(
            success=process.returncode == 0,
            output=stdout.decode('utf-8') if stdout else "",
            error=stderr.decode('utf-8') if stderr else "",
            exit_code=process.returncode or 0,
            duration_ms=duration_ms
        )
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return CommandResponse(
            success=False,
            output="",
            error=str(e),
            exit_code=-1,
            duration_ms=duration_ms
        )

@router.get("/system-status", response_model=SystemStatusResponse)
async def get_system_status():
    """Check system status for various components"""
    
    async def check_command(cmd: str) -> str:
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return f"available: {stdout.decode().strip().split()[0] if stdout else 'ok'}"
            else:
                return f"error: {stderr.decode().strip()}"
        except Exception as e:
            return f"unavailable: {str(e)}"
    
    # Check various system components
    status = SystemStatusResponse(
        python=await check_command("python --version"),
        pytest=await check_command("pytest --version"),
        dependencies=await check_command("pip show fastapi"),
        server=await check_command("curl -f http://localhost:8000/health --connect-timeout 2"),
        aura_imports=await check_command("python -c 'import aura_v2; print(aura_v2.__version__)'")
    )
    
    return status

@router.get("/file-structure")
async def get_file_structure():
    """Get the current file structure for verification"""
    
    def scan_directory(path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        if current_depth >= max_depth:
            return {}
        
        structure = {}
        try:
            for item in path.iterdir():
                if item.name.startswith('.'):
                    continue
                
                if item.is_file() and item.suffix in ['.py', '.toml', '.yml', '.yaml', '.md']:
                    structure[str(item)] = {
                        'type': 'file',
                        'size': item.stat().st_size,
                        'modified': item.stat().st_mtime
                    }
                elif item.is_dir() and item.name not in ['__pycache__', '.git', 'node_modules']:
                    structure[str(item)] = {
                        'type': 'directory',
                        'children': scan_directory(item, max_depth, current_depth + 1)
                    }
        except PermissionError:
            pass
            
        return structure
    
    project_root = Path.cwd()
    return scan_directory(project_root)

@router.post("/run-tests")
async def run_specific_tests(test_path: str):
    """Run specific test files or directories"""
    
    if not test_path.startswith('tests/'):
        raise HTTPException(status_code=400, detail="Test path must start with 'tests/'")
    
    test_file = Path(test_path)
    if not test_file.exists():
        raise HTTPException(status_code=404, detail=f"Test file not found: {test_path}")
    
    command = f"pytest {test_path} -v --tb=short"
    
    request = CommandRequest(command=command)
    return await execute_command(request)
