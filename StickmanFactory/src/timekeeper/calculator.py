"""
calculator.py - Bộ tính toán Thời gian & Số từ

Đảm bảo video dài chính xác 10-12 phút bằng cách tính toán
số từ mục tiêu, ước lượng thời lượng, và điều chỉnh tốc độ đọc.
"""

import sys
import os

# Thêm project root vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def calculate_target_words(duration_min: float, wpm: int = 150) -> int:
    """
    Tính tổng số từ cần thiết cho thời lượng mục tiêu.

    Args:
        duration_min: Thời gian mục tiêu (phút). Ví dụ: 11.
        wpm: Words Per Minute (tốc độ đọc). Mặc định: 150.

    Returns:
        Tổng số từ cần thiết (int).

    Ví dụ:
        calculate_target_words(11, 150) → 1650
    """
    if duration_min <= 0:
        raise ValueError("duration_min must be positive")
    if wpm <= 0:
        raise ValueError("wpm must be positive")

    return int(duration_min * wpm)


def estimate_duration(text: str, wpm: int = 150) -> float:
    """
    Ước lượng thời lượng (giây) dựa trên văn bản kịch bản.

    Args:
        text: Văn bản kịch bản.
        wpm: Words Per Minute. Mặc định: 150.

    Returns:
        Thời lượng dự kiến (giây).

    Ví dụ:
        estimate_duration("Hello world this is a test", 150)
        → 6 words / 150 wpm * 60 = 2.4 giây
    """
    if not text or not text.strip():
        return 0.0
    if wpm <= 0:
        raise ValueError("wpm must be positive")

    word_count = len(text.split())
    duration_seconds = (word_count / wpm) * 60.0
    return round(duration_seconds, 2)


def count_words(text: str) -> int:
    """
    Đếm số từ trong văn bản.

    Args:
        text: Văn bản cần đếm.

    Returns:
        Số từ (int).
    """
    if not text or not text.strip():
        return 0
    return len(text.split())


def validate_script_length(text: str, target_words: int, tolerance: float = 0.05) -> tuple:
    """
    Kiểm tra xem số từ thực tế có nằm trong khoảng ±tolerance so với mục tiêu.

    Args:
        text: Văn bản kịch bản.
        target_words: Số từ mục tiêu.
        tolerance: Sai số cho phép (mặc định 5% = 0.05).

    Returns:
        Tuple (is_valid: bool, actual_words: int, message: str)

    Ví dụ:
        validate_script_length(long_text, 1650, 0.05)
        → (True, 1640, "Word count 1640 is within ±5% of target 1650")
    """
    if target_words <= 0:
        raise ValueError("target_words must be positive")

    actual_words = count_words(text)
    lower_bound = int(target_words * (1 - tolerance))
    upper_bound = int(target_words * (1 + tolerance))

    is_valid = lower_bound <= actual_words <= upper_bound

    if is_valid:
        message = (
            f"✅ Word count {actual_words} is within ±{int(tolerance*100)}% "
            f"of target {target_words} (range: {lower_bound}-{upper_bound})"
        )
    else:
        diff = actual_words - target_words
        direction = "over" if diff > 0 else "under"
        message = (
            f"❌ Word count {actual_words} is {abs(diff)} words {direction} target {target_words} "
            f"(allowed range: {lower_bound}-{upper_bound})"
        )

    return is_valid, actual_words, message


def adjust_speed_factor(actual_duration: float, target_duration: float) -> float:
    """
    Tính hệ số tốc độ (speed factor) để truyền vào Kokoro TTS.

    Nếu audio thực tế dài hơn mục tiêu → cần đọc nhanh hơn (speed > 1.0).
    Nếu audio ngắn hơn mục tiêu → cần đọc chậm hơn (speed < 1.0).

    Args:
        actual_duration: Thời lượng thực tế (giây).
        target_duration: Thời lượng mục tiêu (giây).

    Returns:
        Speed factor (float). Giới hạn trong khoảng [0.5, 2.0] để tránh
        chất lượng âm thanh quá kém.

    Ví dụ:
        adjust_speed_factor(700, 660) → 1.06 (cần đọc nhanh hơn 6%)
    """
    if actual_duration <= 0 or target_duration <= 0:
        raise ValueError("Durations must be positive")

    speed = actual_duration / target_duration

    # Giới hạn speed factor trong khoảng an toàn
    speed = max(0.5, min(2.0, speed))

    return round(speed, 3)


def _run_tests():
    """Chạy các test nội bộ khi gọi với flag --test."""
    print("=" * 60)
    print("  TIMEKEEPER CALCULATOR - Test Results")
    print("=" * 60)

    # Test 1: calculate_target_words
    target_words = calculate_target_words(11, 150)
    print(f"\n📊 Target words for 11 min at 150 WPM: {target_words}")
    assert target_words == 1650, f"Expected 1650, got {target_words}"
    print("   ✅ PASSED")

    # Test 2: estimate_duration
    sample_text = " ".join(["word"] * 150)  # 150 từ = 1 phút = 60 giây
    duration = estimate_duration(sample_text, 150)
    print(f"\n⏱️  Estimated duration for 150 words at 150 WPM: {duration}s")
    assert duration == 60.0, f"Expected 60.0, got {duration}"
    print("   ✅ PASSED")

    # Test 3: validate_script_length
    valid_text = " ".join(["word"] * 1650)
    is_valid, actual, msg = validate_script_length(valid_text, 1650)
    print(f"\n📝 Validate 1650 words vs target 1650:")
    print(f"   {msg}")
    assert is_valid, "Expected valid"
    print("   ✅ PASSED")

    # Test 4: validate_script_length - out of range
    short_text = " ".join(["word"] * 1500)
    is_valid, actual, msg = validate_script_length(short_text, 1650)
    print(f"\n📝 Validate 1500 words vs target 1650:")
    print(f"   {msg}")
    assert not is_valid, "Expected invalid"
    print("   ✅ PASSED")

    # Test 5: adjust_speed_factor
    speed = adjust_speed_factor(700, 660)
    print(f"\n🎚️  Speed factor for 700s actual / 660s target: {speed}x")
    assert 1.0 < speed < 1.1, f"Expected ~1.06, got {speed}"
    print("   ✅ PASSED")

    # Test 6: count_words
    wc = count_words("Hello world this is a simple test string")
    print(f"\n🔢 Word count for 'Hello world this is a simple test string': {wc}")
    assert wc == 8, f"Expected 8, got {wc}"
    print("   ✅ PASSED")

    print("\n" + "=" * 60)
    print("  All tests PASSED! ✅")
    print("=" * 60)


if __name__ == "__main__":
    if "--test" in sys.argv:
        _run_tests()
    else:
        print("Usage: python src/timekeeper/calculator.py --test")
        print("  Runs built-in tests for the time calculator module.")
