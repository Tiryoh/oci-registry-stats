from registry_stats.parsing.numbers import parse_compact_int


def test_parse_compact_int() -> None:
    assert parse_compact_int("25") == 25
    assert parse_compact_int("1,234") == 1234
    assert parse_compact_int("10.3K") == 10300
    assert parse_compact_int("1.2M") == 1200000
    assert parse_compact_int("0") == 0
