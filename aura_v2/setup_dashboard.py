# aura_v2/setup_dashboard.py
"""
Setup script to install the AURA v2 Development Dashboard
Run: python -m aura_v2.setup_dashboard
"""

import subprocess
import sys
from pathlib import Path


def check_fastapi():
    """Check if FastAPI is available"""
    try:
        import fastapi  # noqa: F401

        return True
    except ImportError:
        return False


def install_dashboard_dependencies():
    """Install required dependencies for the dashboard"""
    print("📦 Installing dashboard dependencies...")
    try:
        # Try to install FastAPI and uvicorn
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "fastapi>=0.100.0",
                "uvicorn[standard]>=0.23.0",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Dashboard dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def setup_dashboard():
    """Install the development dashboard files"""

    print("🚀 Setting up AURA v2 Development Dashboard...")

    # Check if FastAPI is available
    fastapi_available = check_fastapi()
    if not fastapi_available:
        print("⚠️  FastAPI not found. Attempting to install...")
        if not install_dashboard_dependencies():
            print("❌ Dashboard setup failed - could not install FastAPI")
            print("   Please run: pip install fastapi uvicorn")
            return False

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

    # Write the fixed API file
    api_file = dashboard_dir / "api.py"
    with open(api_file, "w") as f:
        f.write(get_api_content())
    print(f"✅ Created: {api_file}")

    # Create dashboard.html
    dashboard_html = dashboard_dir / "dashboard.html"
    with open(dashboard_html, "w") as f:
        f.write(get_dashboard_html())
    print(f"✅ Created: {dashboard_html}")

    # Test the installation
    print("\n🧪 Testing dashboard installation...")
    try:
        # Try importing the dashboard module
        sys.path.insert(0, str(aura_dir.parent))
        from aura_v2.web_dashboard.api import router

        if router is not None:
            print("✅ Dashboard API is functional")
        else:
            print("⚠️  Dashboard API created but FastAPI not fully available")
    except Exception as e:
        print(f"⚠️  Dashboard test failed: {e}")

    print("\n🎉 Dashboard setup complete!")
    print("\n📋 Next steps:")
    print("1. Start your development server:")
    print("   python -m aura_v2.main dev-server --host 0.0.0.0 --port 8000")
    print("\n2. Open your browser to:")
    print("   http://localhost:8000")
    print("\n3. The dashboard will be available with command execution!")
    return True


def get_api_content():
    """Return the API module content"""
    return '''# aura_v2/web_dashboard/api.py
"""
AURA Dashboard API with defensive imports
Gracefully handles missing dependencies during setup
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

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
                'python', 'pytest', 'pip', 'uv', 'curl', 'ruff', 'black', 'mypy',
                'docker', 'git', 'npm', 'node', 'yarn', 'poetry', 'ls', 'cat', 'which'
            ]

            command_parts = request.command.split()
            if not command_parts:
                raise HTTPException(status_code=400, detail="Empty command")

            if command_parts[0] not in safe_commands:
                raise HTTPException(
                    status_code=400,
                    detail=f"Command '{command_parts[0]}' not allowed. Allowed: {safe_commands}"
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
                    output = stdout.decode().strip() if stdout else 'ok'
                    # Get first word for version info
                    first_word = output.split()[0] if output.split() else 'ok'
                    return f"available: {first_word}"
                else:
                    error_msg = stderr.decode().strip() if stderr else 'command failed'
                    return f"error: {error_msg[:50]}..."  # Truncate long errors
            except Exception as e:
                return f"unavailable: {str(e)[:50]}..."

        # Check various system components
        status = SystemStatusResponse(
            python=await check_command("python --version"),
            pytest=await check_command("pytest --version"),
            dependencies=await check_command("pip show fastapi"),
            server=await check_command("curl -f http://localhost:8000/health --connect-timeout 2 --max-time 5"),
            aura_imports=await check_command("python -c \\"import aura_v2; print('v' + aura_v2.__version__)\\""')
        )

        return status

    return router


# Create the router (will be None if dependencies not available)
router = create_router()

# Compatibility function for main.py import
def get_router():
    """Get the dashboard router, with fallback handling"""
    return router
'''


def get_dashboard_html():
    """Return the dashboard HTML content"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA v2 Development Dashboard</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; padding: 0; }
        .console-output {
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            line-height: 1.4;
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        const AURADashboard = () => {
            const [consoleOutput, setConsoleOutput] = useState([]);
            const [consoleInput, setConsoleInput] = useState('');
            const [isConsoleRunning, setIsConsoleRunning] = useState(false);
            const [systemStatus, setSystemStatus] = useState({});
            const consoleRef = useRef(null);

            const quickCommands = [
                { name: 'Run All Tests', command: 'pytest -v', description: 'Execute full test suite' },
                { name: 'Start Dev Server', command: 'python -m aura_v2.main dev-server --host 0.0.0.0 --port 8000', description: 'Start development server' },
                { name: 'Health Check', command: 'curl -f http://localhost:8000/health', description: 'Check server health' },
                { name: 'Install Dependencies', command: 'pip install -e ".[test]"', description: 'Install dependencies' }
            ];

            useEffect(() => {
                fetchSystemStatus();
            }, []);

            const fetchSystemStatus = async () => {
                try {
                    const response = await fetch('/dashboard/system-status');
                    if (response.ok) {
                        const status = await response.json();
                        setSystemStatus(status);
                    }
                } catch (error) {
                    console.error('Failed to fetch system status:', error);
                }
            };

            const executeCommand = async (command) => {
                setIsConsoleRunning(true);
                addToConsole(`$ ${command}`, 'command');

                try {
                    const response = await fetch('/dashboard/execute', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command, working_directory: '.' })
                    });

                    const result = await response.json();

                    if (result.success) {
                        addToConsole(result.output, 'success');
                    } else {
                        addToConsole(result.error || 'Command failed', 'error');
                    }

                    addToConsole(`Completed in ${result.duration_ms.toFixed(0)}ms`, 'info');

                } catch (error) {
                    addToConsole(`Error: ${error.message}`, 'error');
                } finally {
                    setIsConsoleRunning(false);
                }
            };

            const addToConsole = (message, type = 'info') => {
                const timestamp = new Date().toLocaleTimeString();
                setConsoleOutput(prev => [...prev, { timestamp, message, type }]);
            };

            const handleConsoleSubmit = (e) => {
                e.preventDefault();
                if (consoleInput.trim() && !isConsoleRunning) {
                    executeCommand(consoleInput.trim());
                    setConsoleInput('');
                }
            };

            return (
                <div className="min-h-screen bg-gray-900 text-white">
                    <div className="max-w-7xl mx-auto p-6">
                        <div className="mb-8">
                            <h1 className="text-4xl font-bold mb-2 text-blue-400">AURA v2 Development Dashboard</h1>
                            <p className="text-gray-400">Real-time tracking system with integrated testing and debugging</p>
                        </div>

                        <div className="bg-gray-800 rounded-lg p-4 mb-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-6">
                                    {Object.entries(systemStatus).map(([key, value]) => (
                                        <div key={key} className="flex items-center space-x-2">
                                            <div className={`w-2 h-2 rounded-full ${value && value.includes('available') ? 'bg-green-400' : 'bg-red-400'}`}></div>
                                            <span className="text-sm text-gray-300 capitalize">{key}</span>
                                        </div>
                                    ))}
                                </div>
                                <button onClick={fetchSystemStatus} className="text-blue-400 hover:text-blue-300 text-sm">
                                    Refresh
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <div className="lg:col-span-1">
                                <h3 className="text-lg font-semibold mb-4">Quick Commands</h3>
                                <div className="space-y-2">
                                    {quickCommands.map((cmd, index) => (
                                        <button
                                            key={index}
                                            onClick={() => executeCommand(cmd.command)}
                                            disabled={isConsoleRunning}
                                            className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-900 rounded-lg transition-colors"
                                        >
                                            <div className="text-sm font-medium">{cmd.name}</div>
                                            <div className="text-xs text-gray-400 mt-1">{cmd.description}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="lg:col-span-2">
                                <h3 className="text-lg font-semibold mb-4">Debug Console</h3>
                                <div className="bg-black rounded-lg p-4 font-mono text-sm console-output">
                                    <div ref={consoleRef} className="h-96 overflow-y-auto mb-4 space-y-1">
                                        {consoleOutput.map((entry, index) => (
                                            <div key={index} className="flex">
                                                <span className="text-gray-500 mr-2 text-xs">{entry.timestamp}</span>
                                                <span className={
                                                    entry.type === 'command' ? 'text-yellow-400' :
                                                    entry.type === 'error' ? 'text-red-400' :
                                                    entry.type === 'success' ? 'text-green-400' :
                                                    'text-gray-300'
                                                }>
                                                    {entry.message}
                                                </span>
                                            </div>
                                        ))}
                                    </div>

                                    <form onSubmit={handleConsoleSubmit} className="flex">
                                        <span className="text-green-400 mr-2">$</span>
                                        <input
                                            type="text"
                                            value={consoleInput}
                                            onChange={(e) => setConsoleInput(e.target.value)}
                                            disabled={isConsoleRunning}
                                            className="flex-1 bg-transparent border-none outline-none text-white"
                                            placeholder="Enter command..."
                                        />
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };

        ReactDOM.render(<AURADashboard />, document.getElementById('root'));
    </script>
</body>
</html>"""


if __name__ == "__main__":
    setup_dashboard()
