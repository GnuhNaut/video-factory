"""
main.py - Entry point cho StickmanFactory

Cung cấp CLI để test các module và chạy pipeline.
"""

import argparse
import sys
import os
import json

# Thêm project root vào path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def test_config():
    """Test: Load và hiển thị config."""
    from src.core.config_loader import load_config, print_config, validate_required_keys

    print("\n🔧 Testing Config Loader...")
    try:
        config = load_config()
        print_config(config)
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_timekeeper():
    """Test: Chạy bộ tính toán thời gian."""
    from src.timekeeper.calculator import _run_tests

    print("\n⏱️  Testing Timekeeper Calculator...")
    try:
        _run_tests()
        return True
    except Exception as e:
        print(f"❌ Timekeeper test failed: {e}")
        return False


def test_stickman():
    """Test: Sinh nhân vật Stickman."""
    from src.visual.stickman_gen import _run_tests

    print("\n🎨 Testing Stickman Generator...")
    try:
        _run_tests()
        return True
    except Exception as e:
        print(f"❌ Stickman test failed: {e}")
        return False


def test_validator():
    """Test: Validate sample_project.json."""
    from src.core.validator import validate_project_file, print_validation_result

    print("\n📋 Testing JSON Validator...")
    sample_path = os.path.join(PROJECT_ROOT, "sample_project.json")
    try:
        is_valid, errors = validate_project_file(sample_path)
        print_validation_result(is_valid, errors)
        return is_valid
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False


def test_kokoro(text: str = "Hello world"):
    """Test: Sinh audio bằng Kokoro."""
    from src.audio.kokoro_wrapper import _run_test

    print("\n🎤 Testing Kokoro TTS...")
    try:
        _run_test(text)
        return True
    except Exception as e:
        print(f"❌ Kokoro test failed: {e}")
        return False


def run_all_tests():
    """Chạy tất cả các test."""
    print("=" * 60)
    print("  STICKMAN FACTORY - Phase 1 Test Suite")
    print("=" * 60)

    results = {}

    results["Config"] = test_config()
    results["Timekeeper"] = test_timekeeper()
    results["Stickman"] = test_stickman()
    results["Validator"] = test_validator()

    # Kokoro test - có thể skip nếu chưa cài
    try:
        results["Kokoro"] = test_kokoro()
    except Exception:
        results["Kokoro"] = None  # Skipped

    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    for name, passed in results.items():
        if passed is None:
            status = "⏭️  SKIPPED"
        elif passed:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"  {name:15s} {status}")

    total = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)
    print(f"\n  Total: {total} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="StickmanFactory - AI Video Factory CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py --test-config          Test config loading
  python src/main.py --test-timekeeper      Test time calculator
  python src/main.py --test-stickman        Test stickman generator
  python src/main.py --test-validator       Test JSON validator
  python src/main.py --test-kokoro          Test Kokoro TTS
  python src/main.py --test-all             Run all tests
        """
    )

    parser.add_argument("--test-config", action="store_true",
                        help="Test config loading")
    parser.add_argument("--test-timekeeper", action="store_true",
                        help="Test timekeeper calculator")
    parser.add_argument("--test-stickman", action="store_true",
                        help="Test stickman SVG generator")
    parser.add_argument("--test-validator", action="store_true",
                        help="Test JSON schema validator")
    parser.add_argument("--test-kokoro", action="store_true",
                        help="Test Kokoro TTS audio generation")
    parser.add_argument("--test-all", action="store_true",
                        help="Run all tests")

    args = parser.parse_args()

    if args.test_all:
        run_all_tests()
    elif args.test_config:
        test_config()
    elif args.test_timekeeper:
        test_timekeeper()
    elif args.test_stickman:
        test_stickman()
    elif args.test_validator:
        test_validator()
    elif args.test_kokoro:
        test_kokoro()
    else:
        parser.print_help()
        print("\n💡 Tip: Use --test-all to run all Phase 1 tests.")


if __name__ == "__main__":
    main()
