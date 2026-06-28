from yfjz.tools.cache import build_cache_key


def test_cache_key_changes_with_request_fingerprint() -> None:
    first = build_cache_key(1, "gpt-4o-mini", "hello", 0, 128)
    same = build_cache_key(1, "gpt-4o-mini", "hello", 0, 128)
    different = build_cache_key(1, "gpt-4o-mini", "hello", 0.2, 128)

    assert first == same
    assert first != different
