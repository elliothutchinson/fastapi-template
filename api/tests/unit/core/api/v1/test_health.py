from tests.factories.server_response_factory import ServerResponseFactory


def test_service_health(client):
    expected = ServerResponseFactory.build(message="OK")

    actual = client.get("/api/v1/health")

    assert actual.status_code == 200
    assert actual.json() == expected
