import sys
import pytest

def main():
    print("==================================================")
    print("  Automation Exercise Playwright Python Test Suite ")
    print("==================================================")

    args = ["-v", "-s", "test_cases"]
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
