def test_service_health(client):
    actual = client.get("/api/v1/health")

    assert actual.status_code == 200
    assert actual.json() == {"message": "OK"}
