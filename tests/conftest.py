import pytest

from app.core.rate_limit import demo_limiter, login_limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiters():
    # Rate limiters are module-level singletons; isolate tests from each other.
    login_limiter.reset()
    demo_limiter.reset()
    yield
    login_limiter.reset()
    demo_limiter.reset()
