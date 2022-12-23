def test_auth(client):
    response = client.post("/api/v1/auth")
