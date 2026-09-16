from bot.summary import TELEGRAM_SAFE_LIMIT, split_message, utf16_len


def test_short_text_single_chunk():
    assert split_message("hello") == ["hello"]


def test_default_limit_has_margin_below_telegram():
    assert TELEGRAM_SAFE_LIMIT < 4096


def test_long_text_split_on_newlines_without_loss():
    text = "\n".join(f"line {i} " + "x" * 50 for i in range(300))
    chunks = split_message(text, limit=4096)
    assert len(chunks) > 1
    assert all(utf16_len(c) <= 4096 for c in chunks)
    assert "\n".join(chunks) == text


def test_single_huge_line_hard_split():
    text = "y" * 10000
    chunks = split_message(text, limit=4096)
    assert all(utf16_len(c) <= 4096 for c in chunks)
    assert "".join(chunks) == text


def test_emoji_counted_in_utf16_units_and_pairs_not_broken():
    text = "😀" * 3000  # 6000 UTF-16 units, 3000 code points
    assert utf16_len(text) == 6000
    chunks = split_message(text, limit=4096)
    assert len(chunks) == 2
    assert all(utf16_len(c) <= 4096 for c in chunks)
    assert "".join(chunks) == text
