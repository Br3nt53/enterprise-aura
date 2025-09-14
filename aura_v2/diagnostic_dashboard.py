# diagnostic_dashboard.py
"""
Diagnostic script for AURA Dashboard issues
Run: python diagnostic_dashboard.py
"""

import os
import sys
from pathlib import Path


def diagnose_dashboard():
    """Diagnose dashboard setup issues"""
    print("🔍 AURA Dashboard Diagnostic")
    print("=" * 50)

    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")

    # Check if aura_v2 exists
    aura_dir = current_dir / "aura_v2"
    if not aura_dir.exists():
        print("❌ aura_v2 directory not found!")
        print(f"   Looking in: {aura_dir}")
        return False
    else:
        print("✅ aura_v2 directory found")

    # Check web_dashboard directory
    dashboard_dir = aura_dir / "web_dashboard"
    if not dashboard_dir.exists():
        print("❌ web_dashboard directory not found!")
        print("   Creating directory...")
        dashboard_dir.mkdir(exist_ok=True)
        print("✅ web_dashboard directory created")
    else:
        print("✅ web_dashboard directory exists")

    # Check for dashboard files
    files_to_check = [
        ("__init__.py", '"""AURA v2 Web Dashboard"""\n'),
        ("api.py", None),  # Will be checked separately
        ("dashboard.html", None),  # Will be created
    ]

    for filename, default_content in files_to_check:
        file_path = dashboard_dir / filename
        if file_path.exists():
            print(f"✅ {filename} exists ({file_path.stat().st_size} bytes)")
        else:
            print(f"❌ {filename} missing!")
            if default_content:
                print(f"   Creating {filename}...")
                file_path.write_text(default_content)
                print(f"✅ {filename} created")

    # Create the dashboard.html file
    html_file = dashboard_dir / "dashboard.html"
    print("\n📝 Creating/updating dashboard.html...")

    # Get the HTML content from our diagnostic version
    html_content = get_dashboard_html()
    html_file.write_text(html_content)
    print(f"✅ dashboard.html created/updated ({len(html_content)} characters)")

    # Check main.py
    main_file = aura_dir / "main.py"
    if main_file.exists():
        print("✅ main.py exists")

        # Check if it has dashboard integration
        main_content = main_file.read_text()
        if "web_dashboard" in main_content:
            print("✅ main.py has dashboard integration")
        else:
            print("⚠️  main.py missing dashboard integration")
    else:
        print("❌ main.py not found!")

    # Test imports
    print("\n🧪 Testing imports...")
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(current_dir))

        import aura_v2

        print("✅ aura_v2 import successful")

        try:
            from aura_v2.web_dashboard.api import router

            if router:
                print("✅ Dashboard router created successfully")
            else:
                print("⚠️  Dashboard router is None (FastAPI may be missing)")
        except Exception as e:
            print(f"⚠️  Dashboard import issue: {e}")

        try:
            from aura_v2.main import get_app

            get_app()
            print("✅ Main app creation successful")
        except Exception as e:
            print(f"❌ Main app creation failed: {e}")

    except Exception as e:
        print(f"❌ Import failed: {e}")

    print("\n🚀 Diagnostic complete!")
    print("\n📋 Next steps:")
    print(
        "1. Start the server: python -m aura_v2.main dev-server --host 0.0.0.0 --port 8000"
    )
    print("2. Open browser to: http://localhost:8000")
    print("3. Check browser console (F12) for any JavaScript errors")

    return True


def get_dashboard_html():
    """Get the diagnostic dashboard HTML content"""
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
        body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        .console-output { 
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace; 
            line-height: 1.4;
        }
        .loading { text-align: center; padding: 40px; }
        .error { color: red; background: #fee; border: 1px solid #fcc; padding: 20px; margin: 20px; border-radius: 8px; }
    </style>
</head>
<body>
    <div id="loading" class="loading">
        <h2>Loading AURA Dashboard...</h2>
        <p>If this message persists, check the browser console for errors.</p>
    </div>
    <div id="root"></div>

    <script type="text/babel">
        console.log("🚀 Starting AURA Dashboard...");
        
        const { useState, useEffect, useRef } = React;
        
        // Error boundary
        class ErrorBoundary extends React.Component {
            constructor(props) {
                super(props);
                this.state = { hasError: false, error: null };
            }
            
            static getDerivedStateFromError(error) {
                return { hasError: true, error };
            }
            
            componentDidCatch(error, errorInfo) {
                console.error('Dashboard Error:', error, errorInfo);
            }
            
            render() {
                if (this.state.hasError) {
                    return (
                        <div className="error">
                            <h2>Dashboard Error</h2>
                            <p>Something went wrong: {this.state.error?.message}</p>
                            <p>Check the browser console for more details.</p>
                            <button onClick={() => window.location.reload()}>Reload Page</button>
                        </div>
                    );
                }
                
                return this.props.children;
            }
        }
        
        const AURADashboard = () => {
            const [consoleOutput, setConsoleOutput] = useState([]);
            const [consoleInput, setConsoleInput] = useState('');
            const [isConsoleRunning, setIsConsoleRunning] = useState(false);
            const [systemStatus, setSystemStatus] = useState({});
            const [dashboardReady, setDashboardReady] = useState(false);
            const consoleRef = useRef(null);

            const quickCommands = [
                { name: 'Health Check', command: 'curl -f http://localhost:8000/health', description: 'Check server health' },
                { name: 'Run Tests', command: 'pytest -v', description: 'Execute test suite' },
                { name: 'Python Version', command: 'python --version', description: 'Check Python version' },
                { name: 'List Files', command: 'ls -la', description: 'List current directory' }
            ];

            useEffect(() => {
                console.log("📡 Dashboard component mounted");
                
                // Hide loading message
                const loadingEl = document.getElementById('loading');
                if (loadingEl) {
                    loadingEl.style.display = 'none';
                    console.log("✅ Loading message hidden");
                }
                
                setDashboardReady(true);
                fetchSystemStatus();
                addToConsole('Dashboard loaded successfully', 'success');
            }, []);

            const fetchSystemStatus = async () => {
                console.log("📊 Fetching system status...");
                try {
                    const response = await fetch('/dashboard/system-status');
                    if (response.ok) {
                        const status = await response.json();
                        setSystemStatus(status);
                        addToConsole('System status loaded', 'info');
                        console.log("✅ System status:", status);
                    } else {
                        addToConsole('Dashboard API not available - basic mode active', 'warning');
                        console.warn("⚠️  Dashboard API response:", response.status);
                    }
                } catch (error) {
                    addToConsole('Dashboard API not available - basic mode active', 'warning');
                    console.warn('❌ Failed to fetch system status:', error);
                }
            };

            const executeCommand = async (command) => {
                console.log("🔧 Executing command:", command);
                setIsConsoleRunning(true);
                addToConsole(`$ ${command}`, 'command');

                try {
                    const response = await fetch('/dashboard/execute', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command, working_directory: '.' })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }

                    const result = await response.json();
                    console.log("📤 Command result:", result);
                    
                    if (result.success) {
                        addToConsole(result.output || 'Command completed successfully', 'success');
                    } else {
                        addToConsole(result.error || 'Command failed', 'error');
                    }
                    
                    addToConsole(`Completed in ${result.duration_ms?.toFixed(0) || 0}ms`, 'info');
                    
                } catch (error) {
                    addToConsole(`Error: ${error.message}`, 'error');
                    console.error("❌ Command execution error:", error);
                } finally {
                    setIsConsoleRunning(false);
                }
            };

            const addToConsole = (message, type = 'info') => {
                const timestamp = new Date().toLocaleTimeString();
                setConsoleOutput(prev => [...prev.slice(-50), { timestamp, message, type }]);
                console.log(`[${type.toUpperCase()}] ${message}`);
            };

            const handleConsoleSubmit = (e) => {
                e.preventDefault();
                if (consoleInput.trim() && !isConsoleRunning) {
                    executeCommand(consoleInput.trim());
                    setConsoleInput('');
                }
            };

            const testTrackingAPI = async () => {
                addToConsole('Testing /track endpoint...', 'info');
                try {
                    const response = await fetch('/track', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            radar_detections: [],
                            camera_detections: [{
                                timestamp: new Date().toISOString(),
                                position: { x: 10, y: 20, z: 0 },
                                confidence: 0.9,
                                sensor_id: 'test_sensor'
                            }],
                            lidar_detections: [],
                            timestamp: new Date().toISOString()
                        })
                    });
                    
                    const result = await response.json();
                    addToConsole(`✅ /track working: ${result.active_tracks?.length || 0} tracks`, 'success');
                } catch (error) {
                    addToConsole(`❌ /track error: ${error.message}`, 'error');
                }
            };

            if (!dashboardReady) {
                return <div className="loading">Initializing...</div>;
            }

            console.log("🎨 Rendering dashboard UI");

            return (
                <div className="min-h-screen bg-gray-900 text-white">
                    <div className="max-w-7xl mx-auto p-6">
                        <div className="mb-8">
                            <h1 className="text-4xl font-bold mb-2 text-blue-400">AURA v2 Development Dashboard</h1>
                            <p className="text-gray-400">Real-time tracking system with integrated testing and debugging</p>
                            <p className="text-xs text-gray-500 mt-2">Dashboard loaded at {new Date().toLocaleString()}</p>
                        </div>

                        {/* System Status */}
                        <div className="bg-gray-800 rounded-lg p-4 mb-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-6">
                                    {Object.entries(systemStatus).map(([key, value]) => (
                                        <div key={key} className="flex items-center space-x-2">
                                            <div className={`w-2 h-2 rounded-full ${value && value.includes('available') ? 'bg-green-400' : 'bg-red-400'}`}></div>
                                            <span className="text-sm text-gray-300 capitalize">{key}</span>
                                        </div>
                                    ))}
                                    {Object.keys(systemStatus).length === 0 && (
                                        <span className="text-gray-400 text-sm">System status loading...</span>
                                    )}
                                </div>
                                <div className="space-x-2">
                                    <button onClick={fetchSystemStatus} className="text-blue-400 hover:text-blue-300 text-sm px-3 py-1 bg-blue-900 rounded">
                                        Refresh
                                    </button>
                                    <button onClick={testTrackingAPI} className="text-green-400 hover:text-green-300 text-sm px-3 py-1 bg-green-900 rounded">
                                        Test API
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Quick Commands */}
                            <div className="lg:col-span-1">
                                <h3 className="text-lg font-semibold mb-4">Quick Commands</h3>
                                <div className="space-y-2">
                                    {quickCommands.map((cmd, index) => (
                                        <button
                                            key={index}
                                            onClick={() => executeCommand(cmd.command)}
                                            disabled={isConsoleRunning}
                                            className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-900 disabled:cursor-not-allowed rounded-lg transition-colors"
                                        >
                                            <div className="text-sm font-medium">{cmd.name}</div>
                                            <div className="text-xs text-gray-400 mt-1">{cmd.description}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Console */}
                            <div className="lg:col-span-2">
                                <h3 className="text-lg font-semibold mb-4">Debug Console</h3>
                                <div className="bg-black rounded-lg p-4 font-mono text-sm console-output">
                                    <div ref={consoleRef} className="h-96 overflow-y-auto mb-4 space-y-1">
                                        {consoleOutput.map((entry, index) => (
                                            <div key={index} className="flex">
                                                <span className="text-gray-500 mr-2 text-xs flex-shrink-0">{entry.timestamp}</span>
                                                <span className={
                                                    entry.type === 'command' ? 'text-yellow-400' :
                                                    entry.type === 'error' ? 'text-red-400' :
                                                    entry.type === 'success' ? 'text-green-400' :
                                                    entry.type === 'warning' ? 'text-orange-400' :
                                                    'text-gray-300'
                                                }>
                                                    {entry.message}
                                                </span>
                                            </div>
                                        ))}
                                        {isConsoleRunning && (
                                            <div className="flex">
                                                <span className="text-gray-500 mr-2 text-xs">Running</span>
                                                <span className="text-yellow-400 animate-pulse">...</span>
                                            </div>
                                        )}
                                    </div>

                                    <form onSubmit={handleConsoleSubmit} className="flex">
                                        <span className="text-green-400 mr-2 flex-shrink-0">$</span>
                                        <input
                                            type="text"
                                            value={consoleInput}
                                            onChange={(e) => setConsoleInput(e.target.value)}
                                            disabled={isConsoleRunning}
                                            className="flex-1 bg-transparent border-none outline-none text-white disabled:cursor-not-allowed"
                                            placeholder="Enter command..."
                                            autoComplete="off"
                                        />
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };

        try {
            console.log("🎯 Attempting to render React app...");
            ReactDOM.render(
                <ErrorBoundary>
                    <AURADashboard />
                </ErrorBoundary>, 
                document.getElementById('root')
            );
            console.log("✅ React app rendered successfully");
        } catch (error) {
            console.error("❌ Failed to render React app:", error);
            document.getElementById('root').innerHTML = `
                <div class="error" style="padding: 20px; background: #fee; color: red; margin: 20px; border-radius: 8px;">
                    <h2>Render Error</h2>
                    <p>Failed to render React dashboard: ${error.message}</p>
                    <p>This might be a browser compatibility issue.</p>
                </div>
            `;
        }
    </script>
</body>
</html>"""


if __name__ == "__main__":
    diagnose_dashboard()
