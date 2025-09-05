# aura_v2/tests/architecture/test_dependencies.py
import ast
import os
from pathlib import Path

def test_no_outward_dependencies_from_domain():
    """Domain should not depend on application or infrastructure"""
    domain_files = Path('aura_v2/domain').rglob('*.py')
    
    for file in domain_files:
        with open(file) as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith('aura_v2.application')
                    assert not alias.name.startswith('aura_v2.infrastructure')
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith('aura_v2.application')
                    assert not node.module.startswith('aura_v2.infrastructure')

def test_application_depends_only_on_domain():
    """Application should only depend on domain, not infrastructure"""
    app_files = Path('aura_v2/application').rglob('*.py')
    
    for file in app_files:
        with open(file) as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('aura_v2'):
                    # Should only import from domain or application itself
                    assert node.module.startswith(('aura_v2.domain', 'aura_v2.application'))