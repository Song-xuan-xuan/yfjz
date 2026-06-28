def test_provider_config_api_never_returns_raw_api_key(client) -> None:
    payload = {
        "name": "OpenAI Official",
        "base_url": "https://api.openai.com/v1",
        "api_key": "sk-secretabcd",
        "default_model": "gpt-4o-mini",
        "timeout_seconds": 60,
        "max_retries": 2,
    }

    created = client.post("/api/provider-configs", json=payload)
    assert created.status_code == 200
    body = created.json()
    assert "api_key" not in body
    assert body["api_key_masked"] == "sk-****abcd"

    listed = client.get("/api/provider-configs")
    assert listed.status_code == 200
    serialized = str(listed.json())
    assert "sk-secretabcd" not in serialized
    assert "api_key_masked" in serialized
