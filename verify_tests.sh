#!/bin/bash
# Verify test structure is correct after cleanup

echo "🔍 Verifying test structure..."

# 1. Check directory structure
echo "📁 Directory structure:"
if [ -d "tests" ]; then
    echo "✅ tests/ directory exists"
    tree tests/ 2>/dev/null || find tests -type f -name "*.py" | sort
else
    echo "❌ tests/ directory missing"
    exit 1
fi

# 2. Check no duplicate test directories
if [ -d "aura_v2/tests" ]; then
    echo "❌ Found duplicate aura_v2/tests/ - should be removed"
    exit 1
else
    echo "✅ No duplicate test directories"
fi

# 3. Check pytest configuration
echo ""
echo "⚙️ Pytest configuration:"
if [ -f "pytest.ini" ]; then
    if grep -q "testpaths = \[\"tests\"\]" pytest.ini; then
        echo "✅ pytest.ini has correct testpaths"
    else
        echo "❌ pytest.ini testpaths incorrect"
        grep testpaths pytest.ini || echo "❌ No testpaths found"
    fi
else
    echo "❌ pytest.ini missing"
fi

# 4. Check CI workflow
echo ""
echo "🔄 CI workflow:"
if grep -q "pytest tests/" .github/workflows/ci-cd-pipeline.yml; then
    echo "✅ CI uses correct test path"
else
    echo "❌ CI still references old test path"
    grep pytest .github/workflows/ci-cd-pipeline.yml
fi

# 5. Test imports work
echo ""
echo "🧪 Testing imports:"
python -c "
import sys
sys.path.insert(0, '.')
try:
    import aura_v2
    print('✅ aura_v2 package imports successfully')
except ImportError as e:
    print(f'❌ aura_v2 import failed: {e}')
    sys.exit(1)
"

# 6. Test pytest discovery
echo ""
echo "🔍 Test discovery:"
if command -v pytest >/dev/null 2>&1; then
    test_count=$(pytest --collect-only -q tests/ 2>/dev/null | grep -c "test session starts" || echo "0")
    if [ "$test_count" -gt 0 ]; then
        echo "✅ pytest can discover tests"
        pytest --collect-only tests/ 2>/dev/null | tail -5
    else
        echo "⚠️  pytest test discovery issues"
    fi
else
    echo "ℹ️  pytest not installed - skipping discovery test"
fi

# 7. Check for common issues
echo ""
echo "🔍 Checking for common issues:"

# Check for missing __init__.py files
missing_init=$(find tests -type d -not -path tests -exec test -f {}/__init__.py \; -print 2>/dev/null | wc -l)
if [ "$missing_init" -eq 0 ]; then
    echo "✅ All test directories have __init__.py"
else
    echo "⚠️  Some test directories missing __init__.py"
fi

# Check for import statements that might be broken
if grep -r "from aura_v2.tests" tests/ 2>/dev/null; then
    echo "❌ Found old import statements referencing aura_v2.tests"
else
    echo "✅ No old import references found"
fi

echo ""
echo "🎯 Next steps:"
echo "  1. Run: pytest tests/test_imports.py -v"
echo "  2. Run: pytest tests/test_health.py -v" 
echo "  3. Run: pytest tests/ --collect-only"
echo "  4. If all pass, proceed with Phase 1 critical fixes"