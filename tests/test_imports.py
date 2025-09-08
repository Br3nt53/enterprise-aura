def test_imports():
    import aura_v2

    app = aura_v2.get_app()
    assert app is not None
