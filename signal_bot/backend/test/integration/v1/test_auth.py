def test_auth(client):
    response = client.post("/api/v1/auth")
    assert response.status_code == 307
