import app.modules.analytics as analytics


def test_analytics_module_is_importable_without_runtime_dependencies() -> None:
    """Analytics currently exposes no service implementation or external integration."""

    assert analytics.__package__ == "app.modules.analytics"
