#!/bin/bash
# Manual test cleanup for macOS

echo "🔧 Manual test structure cleanup..."

# 1. Remove the nested tests/tests structure
echo "🗑️ Removing nested tests/tests structure..."
if [ -d "tests/tests" ]; then
    # Move any actual test files from nested structure to proper location
    find tests/tests -name "test_*.py" -type f | while read file; do
        basename_file=$(basename "$file")
        echo "Moving $file to tests/$basename_file"
        mv "$file" "tests/$basename_file" 2>/dev/null || echo "File already exists: $basename_file"
    done
    
    # Remove the nested directory structure
    rm -rf tests/tests
    echo "✅ Removed tests/tests/"
fi

# 2. Fix the CI workflow for macOS (using backup and replace)
echo "🔄 Fixing CI workflow..."
if [ -f ".github/workflows/ci-cd-pipeline.yml" ]; then
    # Create backup
    cp .github/workflows/ci-cd-pipeline.yml .github/workflows/ci-cd-pipeline.yml.bak
    
    # Replace using sed with macOS syntax
    sed -i '' 's/aura_v2\/tests/tests/g' .github/workflows/ci-cd-pipeline.yml
    echo "✅ Updated CI workflow"
else
    echo "⚠️ CI workflow file not found"
fi

# 3. Fix import statements in test files
echo "🔧 Fixing import statements..."
find tests -name "*.py" -type f -exec grep -l "from aura_v2.tests" {} \; | while read file; do
    echo "Fixing imports in: $file"
    # Create backup
    cp "$file" "$file.bak"
    # Fix the import (remove aura_v2.tests prefix)
    sed -i '' 's/from aura_v2\.tests\./from /g' "$file"
    sed -i '' 's/aura_v2\.tests\.//g' "$file"
done

# 4. Clean up any remaining __init__.py duplicates and ensure proper structure
echo "📁 Ensuring clean test structure..."
# Remove any duplicate __init__.py files and ensure proper ones exist
find tests -name "__init__.py" -delete
find tests -type d -exec touch {}/__init__.py \;

# 5. Create a proper pytest.ini
echo "⚙️ Creating proper pytest.ini..."
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

# 6. Organize test files into proper subdirectories
echo "📂 Organizing test files..."
mkdir -p tests/{unit,integration,architecture}

# Move files to appropriate directories based on content/name
if [ -f "tests/test_dependencies.py" ]; then
    mv tests/test_dependencies.py tests/architecture/
fi

if [ -f "tests/test_collision_predictor.py" ]; then
    mv tests/test_collision_predictor.py tests/unit/
fi

if [ -f "tests/test_threat_analyzer.py" ]; then
    mv tests/test_threat_analyzer.py tests/unit/
fi

if [ -f "tests/test_main_endpoints.py" ]; then
    mv tests/test_main_endpoints.py tests/integration/
fi

# Files that should stay at tests root
# test_health.py, test_imports.py - these are good at root

# 7. Create updated conftest.py
echo "🛠️ Creating tests/conftest.py..."
cat > tests/conftest.py << 'EOF'
"""Shared test configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Common fixtures can go here
@pytest.fixture
def sample_detection():
    """Sample detection for testing."""
    from aura_v2.domain.entities import Detection
    from aura_v2.domain.value_objects import Position3D, Confidence
    from datetime import datetime, timezone
    
    return Detection(
        sensor_id="test_sensor",
        timestamp=datetime.now(timezone.utc),
        position=Position3D(x=10.0, y=20.0, z=0.0),
        confidence=Confidence(0.9)
    )
EOF

echo "✅ Manual cleanup complete!"
echo ""
echo "🔍 Current test structure:"
find tests -type f -name "*.py" | sort