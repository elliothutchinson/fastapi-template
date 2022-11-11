from app.core.api import router as uut


def test_router():
    expected = {
        "/api/v1/health/",
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
        "/api/v1/auth/refresh",
        "/api/v1/user/",
    }

    actual = uut.router

    for route in actual.routes:

        assert route.path in expected
