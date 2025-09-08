#!/bin/bash
# Complete test directory cleanup script

echo "🔧 Fixing test directory structure..."

# 1. Remove any remaining tests in package
if [ -d "aura_v2/tests" ]; then
    echo "❌ Removing duplicate tests in package..."
    git rm -r aura_v2/tests/
fi

# 2. Fix nested tests/tests/ structure if it exists
if [ -d "tests/tests" ]; then
    echo "🔄 Flattening nested test structure..."
    # Move contents up one level
    find tests/tests -name "*.py" -exec git mv {} tests/ \;
    # Move any subdirectories
    find tests/tests -type d -not -path "tests/tests" -exec git mv {} tests/ \;
    # Remove empty nested directory
    [ -d "tests/tests" ] && rmdir tests/tests
fi

# 3. Ensure proper test file naming and structure
echo "📁 Ensuring proper test structure..."
mkdir -p tests/{unit,integration,architecture}

# Move test files to appropriate subdirectories if they're in root
find tests -maxdepth 1 -name "test_*.py" -type f | while read file; do
    case "$file" in
        *test_health* | *test_imports*)
            # These can stay at root level
            ;;
        *test_*_coordinator* | *test_multi_sensor* | *test_pipeline*)
            [ ! -d "tests/integration" ] && mkdir -p tests/integration
            git mv "$file" tests/integration/
            ;;
        *test_dependencies*)
            [ ! -d "tests/architecture" ] && mkdir -p tests/architecture  
            git mv "$file" tests/architecture/
            ;;
        *)
            [ ! -d "tests/unit" ] && mkdir -p tests/unit
            git mv "$file" tests/unit/
            ;;
    esac
done

# 4. Update pytest.ini
echo "⚙️ Updating pytest.ini..."
cat > pytest.ini << 'EOF'
[pytest]
testpaths = ["tests"]
addopts = "-q --tb=short --import-mode=importlib"
markers = [
    "asyncio: marks tests as async",
    "gpu: marks tests requiring GPU", 
    "slow: marks tests as slow-running",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "architecture: marks tests as architecture validation"
]
EOF

# 5. Update CI workflow
echo "🔄 Updating CI workflow..."
sed -i 's/uv run pytest aura_v2\/tests/uv run pytest tests/g' .github/workflows/ci-cd-pipeline.yml

# 6. Ensure all test directories have __init__.py
echo "📝 Adding __init__.py files..."
find tests -type d -exec touch {}/__init__.py \;

# 7. Create a simple tests conftest.py for shared fixtures
echo "🛠️ Creating tests/conftest.py..."
cat > tests/conftest.py << 'EOF'
"""Shared test configuration and fixtures."""
import pytest
from pathlib import Path
import sys

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
EOF

echo "✅ Test directory cleanup complete!"
echo ""
echo "📋 Summary of changes:"
echo "  • Removed duplicate aura_v2/tests/"
echo "  • Fixed nested tests/tests/ structure"
echo "  • Organized tests into unit/integration/architecture"
echo "  • Updated pytest.ini with correct testpaths"
echo "  • Updated CI workflow to use tests/ directory"
echo "  • Added __init__.py files"
echo "  • Created tests/conftest.py for shared fixtures"
echo ""
echo "🧪 Test the changes:"
echo "  pytest tests/test_imports.py -v"
echo "  pytest tests/test_health.py -v"