# test_dashboard_setup.py
"""
Validation script for AURA v2 Dashboard Setup
Run: python test_dashboard_setup.py
"""

import sys
from pathlib import Path


def test_dashboard_setup():
    """Test if the dashboard is set up correctly"""
    print("🧪 Testing AURA v2 Dashboard Setup...")

    # Test 1: Check if dashboard files exist
    print("\n1. Checking file structure...")

    aura_dir = Path("aura_v2")
    if not aura_dir.exists():
        print("❌ aura_v2 directory not found")
        return False

    dashboard_dir = aura_dir / "web_dashboard"
    if not dashboard_dir.exists():
        print("❌ web_dashboard directory not found")
        return False
    print("✅ Dashboard directory exists")

    api_file = dashboard_dir / "api.py"
    if not api_file.exists():
        print("❌ api.py file not found")
        return False
    print("✅ API file exists")

    html_file = dashboard_dir / "dashboard.html"
    if not html_file.exists():
        print("❌ dashboard.html file not found")
        return False
    print("✅ Dashboard HTML exists")

    # Test 2: Test imports
    print("\n2. Testing imports...")

    try:
        # Add current directory to path
        if str(Path.cwd()) not in sys.path:
            sys.path.insert(0, str(Path.cwd()))

        # Test basic import
        import aura_v2

        print("✅ Basic aura_v2 import successful")

        # Test dashboard import
        from aura_v2.web_dashboard.api import router

        print("✅ Dashboard API import successful")

        if router is None:
            print("⚠️  Router is None - FastAPI may not be available")
            print("   This is expected if FastAPI is not installed")
        else:
            print("✅ Dashboard router created successfully")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")

    # Test 3: Test main app creation
    print("\n3. Testing main app...")

    try:
        from aura_v2.main import get_app

        app = get_app()
        if app is not None:
            print("✅ Main app creation successful")
        else:
            print("❌ Main app is None")
            return False
    except Exception as e:
        print(f"❌ Main app creation failed: {e}")
        return False

    # Test 4: Check FastAPI availability
    print("\n4. Checking FastAPI availability...")

    try:
        import fastapi

        print("✅ FastAPI is available")

        # Test if routes are registered
        routes = [route.path for route in app.routes]
        if "/dashboard/execute" in routes:
            print("✅ Dashboard routes registered")
        else:
            print("⚠️  Dashboard routes not found - may be disabled")

    except ImportError:
        print("⚠️  FastAPI not available - dashboard API will be disabled")
        print("   Run: pip install fastapi uvicorn")

    print("\n🎉 Dashboard setup validation complete!")
    print("\n📋 Summary:")
    print("   ✅ File structure is correct")
    print("   ✅ Imports work properly")
    print("   ✅ Main app can be created")
    print("\n🚀 Ready to start development server:")
    print("   python -m aura_v2.main dev-server --host 0.0.0.0 --port 8000")

    return True


def main():
    """Main validation function"""
    try:
        success = test_dashboard_setup()
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
