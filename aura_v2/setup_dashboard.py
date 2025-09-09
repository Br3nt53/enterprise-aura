# aura_v2/setup_dashboard.py
"""
Setup script to install the AURA v2 Development Dashboard
Run: python -m aura_v2.setup_dashboard
"""

import os
import shutil
from pathlib import Path

def setup_dashboard():
    """Install the development dashboard files"""
    
    print("🚀 Setting up AURA v2 Development Dashboard...")
    
    # Get the current directory structure
    aura_dir = Path(__file__).parent
    dashboard_dir = aura_dir / "web_dashboard"
    
    # Create dashboard directory
    dashboard_dir.mkdir(exist_ok=True)
    print(f"✅ Created directory: {dashboard_dir}")
    
    # Create __init__.py
    init_file = dashboard_dir / "__init__.py"
    init_file.write_text('"""AURA v2 Web Dashboard"""\n')
    print(f"✅ Created: {init_file}")
    
    # Create api.py with the backend code
    api_file = dashboard_dir / "api.py"
    api_content = '''# Auto-generated AURA Dashboard API
# This file was created by setup_dashboard.py

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
'''
    
    api_file.write_text(api_content)
    print(f"✅ Created: {api_file}")
    
    # Create dashboard.html (you'll need to copy the HTML content here)
    dashboard_html = dashboard_dir / "dashboard.html"
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA v2 Development Dashboard</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { margin: 0; padding: 0; }</style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        // The full React component code would go here
        // For brevity, I'm showing a simple placeholder
        const AURADashboard = () => (
            <div className="min-h-screen bg-gray-900 text-white p-6">
                <h1 className="text-4xl font-bold mb-2 text-blue-400">AURA v2 Development Dashboard</h1>
                <p className="text-gray-400">Dashboard successfully installed!</p>
                <div className="mt-4 bg-gray-800 p-4 rounded">
                    <p>To get the full dashboard, replace this file with the complete HTML from the React artifact.</p>
                </div>
            </div>
        );
        ReactDOM.render(<AURADashboard />, document.getElementById('root'));
    </script>
</body>
</html>'''
    
    dashboard_html.write_text(html_content)
    print(f"✅ Created: {dashboard_html}")
    
    print("\n🎉 Dashboard setup complete!")
    print("\n📋 Next steps:")
    print("1. Copy the full HTML content from the React artifact to:")
    print(f"   {dashboard_html}")
    print("\n2. Start your development server:")
    print("   python -m aura_v2.main dev-server --host 0.0.0.0 --port 8000")
    print("\n3. Open your browser to:")
    print("   http://localhost:8000")
    print("\n4. The dashboard will be available with real command execution!")

if __name__ == "__main__":
    setup_dashboard()
