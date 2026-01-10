#!/usr/bin/env python3
"""
Error Handling Tests - Verify error handling mechanisms.
Tests custom exceptions, error utilities, and retry logic.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test results tracking
passed = 0
failed = 0
errors = []


def test(name, condition, error_msg=""):
    """Record test result."""
    global passed, failed, errors
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
        return True
    else:
        print(f"  [FAIL] {name}: {error_msg}")
        failed += 1
        errors.append((name, error_msg))
        return False


# ============================================================
# ERROR HANDLING TESTS
# ============================================================

def test_custom_exceptions():
    """Test custom exception classes."""
    print("\n--- Custom Exceptions ---")

    try:
        # Import directly from errors module to avoid PIL dependency
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "errors",
            PROJECT_ROOT / "src" / "fal_api" / "errors.py"
        )
        errors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(errors_module)

        FalAPIError = errors_module.FalAPIError
        APIKeyError = errors_module.APIKeyError
        NetworkError = errors_module.NetworkError
        APITimeoutError = errors_module.APITimeoutError
        APIRateLimitError = errors_module.APIRateLimitError
        ImageProcessingError = errors_module.ImageProcessingError
        InvalidInputError = errors_module.InvalidInputError
        DependencyError = errors_module.DependencyError

        # Test FalAPIError base class
        error = FalAPIError("Test error", code="TEST", details={"key": "value"})
        test("FalAPIError has message", error.message == "Test error")
        test("FalAPIError has code", error.code == "TEST")
        test("FalAPIError has details", error.details == {"key": "value"})

        # Test to_dict method
        error_dict = error.to_dict()
        test("to_dict has success=False", error_dict["success"] == False)
        test("to_dict has error message", error_dict["error"] == "Test error")
        test("to_dict has error_code", error_dict["error_code"] == "TEST")

        # Test APIKeyError
        api_key_error = APIKeyError()
        test("APIKeyError has default message", "FAL_KEY" in api_key_error.message)
        test("APIKeyError code is API_KEY_MISSING", api_key_error.code == "API_KEY_MISSING")

        # Test NetworkError
        original = ValueError("original error")
        network_error = NetworkError("Connection failed", original)
        test("NetworkError captures original", "original error" in str(network_error.details))

        # Test APITimeoutError
        timeout_error = APITimeoutError(30)
        test("APITimeoutError has timeout", "30" in timeout_error.message)
        test("APITimeoutError details has timeout", timeout_error.details["timeout"] == 30)

        # Test APIRateLimitError
        rate_error = APIRateLimitError(retry_after=60)
        test("APIRateLimitError has retry_after", rate_error.details["retry_after"] == 60)

        # Test ImageProcessingError
        img_error = ImageProcessingError("Failed to process", image_path="/test/image.png")
        test("ImageProcessingError has image_path", img_error.details["image_path"] == "/test/image.png")

        # Test InvalidInputError
        input_error = InvalidInputError("Invalid value", field="size", value=100)
        test("InvalidInputError has field", input_error.details["field"] == "size")
        test("InvalidInputError has value", input_error.details["value"] == "100")

        # Test DependencyError
        dep_error = DependencyError("fal-client")
        test("DependencyError has package", dep_error.details["package"] == "fal-client")
        test("DependencyError has install_command", "pip install" in dep_error.details["install_command"])

        return True

    except Exception as e:
        test("custom exceptions", False, str(e))
        return False


def test_error_utilities():
    """Test error utility functions."""
    print("\n--- Error Utilities ---")

    try:
        # Import directly from errors module to avoid PIL dependency
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "errors",
            PROJECT_ROOT / "src" / "fal_api" / "errors.py"
        )
        errors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(errors_module)

        safe_result = errors_module.safe_result
        error_result = errors_module.error_result
        FalAPIError = errors_module.FalAPIError

        # Test safe_result
        success_result = safe_result(True, data="test", count=5)
        test("safe_result has success", success_result["success"] == True)
        test("safe_result includes kwargs", success_result["data"] == "test")
        test("safe_result includes all kwargs", success_result["count"] == 5)

        failure_result = safe_result(False, error="something failed")
        test("safe_result failure", failure_result["success"] == False)

        # Test error_result with FalAPIError
        fal_error = FalAPIError("API failed", code="API_ERROR")
        result = error_result(fal_error)
        test("error_result with FalAPIError", result["error"] == "API failed")
        test("error_result has code", result["error_code"] == "API_ERROR")

        # Test error_result with generic exception
        generic_error = ValueError("generic error")
        generic_result = error_result(generic_error)
        test("error_result with generic exception", "generic error" in generic_result["error"])
        test("error_result generic has code", generic_result["error_code"] == "UNKNOWN_ERROR")

        return True

    except Exception as e:
        test("error utilities", False, str(e))
        return False


def test_validation_functions():
    """Test validation utility functions."""
    print("\n--- Validation Functions ---")

    try:
        # Import directly from errors module to avoid PIL dependency
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "errors",
            PROJECT_ROOT / "src" / "fal_api" / "errors.py"
        )
        errors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(errors_module)

        validate_api_key = errors_module.validate_api_key
        validate_file_exists = errors_module.validate_file_exists
        validate_image_file = errors_module.validate_image_file
        APIKeyError = errors_module.APIKeyError
        InvalidInputError = errors_module.InvalidInputError

        # Test validate_api_key without key
        original_key = os.environ.get("FAL_KEY")
        if "FAL_KEY" in os.environ:
            del os.environ["FAL_KEY"]

        try:
            validate_api_key()
            test("validate_api_key raises without key", False)
        except APIKeyError as e:
            test("validate_api_key raises APIKeyError", True)

        # Restore key if it existed
        if original_key:
            os.environ["FAL_KEY"] = original_key

        # Test validate_api_key with key
        os.environ["FAL_KEY"] = "test-key"
        try:
            result = validate_api_key()
            test("validate_api_key passes with key", result == True)
        except APIKeyError:
            test("validate_api_key passes with key", False)
        finally:
            if original_key:
                os.environ["FAL_KEY"] = original_key
            else:
                del os.environ["FAL_KEY"]

        # Test validate_file_exists
        CustomFileNotFoundError = errors_module.FileNotFoundError

        try:
            validate_file_exists("/nonexistent/file.png")
            test("validate_file_exists raises for missing", False)
        except CustomFileNotFoundError as e:
            test("validate_file_exists raises FileNotFoundError", True)

        # Test with existing file
        existing_file = PROJECT_ROOT / "AGENTS.md"
        if existing_file.exists():
            result = validate_file_exists(str(existing_file))
            test("validate_file_exists passes for existing", result == True)

        # Test validate_image_file with invalid extension
        try:
            validate_image_file("/test/file.txt")
            test("validate_image_file rejects txt", False)
        except (InvalidInputError, CustomFileNotFoundError):
            test("validate_image_file rejects txt", True)

        return True

    except Exception as e:
        test("validation functions", False, str(e))
        return False


def test_decorator_handle_api_errors():
    """Test handle_api_errors decorator."""
    print("\n--- handle_api_errors Decorator ---")

    try:
        # Import directly from errors module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "errors",
            PROJECT_ROOT / "src" / "fal_api" / "errors.py"
        )
        errors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(errors_module)

        handle_api_errors = errors_module.handle_api_errors
        FalAPIError = errors_module.FalAPIError

        # Test function that succeeds
        @handle_api_errors
        def success_func():
            return {"success": True, "data": "test"}

        result = success_func()
        test("success passes through", result["success"] == True)
        test("success data preserved", result["data"] == "test")

        # Test function that raises FalAPIError
        @handle_api_errors
        def fal_error_func():
            raise FalAPIError("API error", code="TEST_ERROR")

        result = fal_error_func()
        test("FalAPIError converted to dict", result["success"] == False)
        test("FalAPIError message preserved", result["error"] == "API error")
        test("FalAPIError code preserved", result["error_code"] == "TEST_ERROR")

        # Test function that raises generic exception
        @handle_api_errors
        def generic_error_func():
            raise ValueError("generic error")

        result = generic_error_func()
        test("generic exception converted", result["success"] == False)
        test("generic exception message", "generic error" in result["error"])
        test("generic exception code", result["error_code"] == "UNEXPECTED_ERROR")

        return True

    except Exception as e:
        test("handle_api_errors decorator", False, str(e))
        return False


def test_retry_decorator():
    """Test retry_on_error decorator."""
    print("\n--- retry_on_error Decorator ---")

    try:
        # Import directly from errors module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "errors",
            PROJECT_ROOT / "src" / "fal_api" / "errors.py"
        )
        errors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(errors_module)

        retry_on_error = errors_module.retry_on_error
        NetworkError = errors_module.NetworkError

        call_count = 0

        # Test function that fails then succeeds
        @retry_on_error(max_retries=3, delay=0.1, backoff=1.0, exceptions=(NetworkError,))
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Connection failed")
            return {"success": True}

        call_count = 0
        result = flaky_func()
        test("retry succeeds after failures", result["success"] == True)
        test("retry called correct times", call_count == 3)

        # Test function that always fails
        @retry_on_error(max_retries=2, delay=0.05, backoff=1.0, exceptions=(NetworkError,))
        def always_fails():
            raise NetworkError("Always fails")

        try:
            always_fails()
            test("retry raises after max retries", False)
        except NetworkError:
            test("retry raises after max retries", True)

        # Test that non-matching exceptions are not retried
        @retry_on_error(max_retries=3, delay=0.1, exceptions=(NetworkError,))
        def wrong_exception():
            raise ValueError("Wrong type")

        try:
            wrong_exception()
            test("non-matching exception not retried", False)
        except ValueError:
            test("non-matching exception not retried", True)

        return True

    except Exception as e:
        test("retry_on_error decorator", False, str(e))
        return False


def test_error_codes():
    """Test error codes reference."""
    print("\n--- Error Codes ---")

    try:
        # Import directly from errors module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "errors",
            PROJECT_ROOT / "src" / "fal_api" / "errors.py"
        )
        errors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(errors_module)

        ERROR_CODES = errors_module.ERROR_CODES

        expected_codes = [
            "API_KEY_MISSING",
            "NETWORK_ERROR",
            "TIMEOUT",
            "RATE_LIMIT",
            "IMAGE_PROCESSING_ERROR",
            "INVALID_INPUT",
            "FILE_NOT_FOUND",
            "DEPENDENCY_MISSING",
            "UNKNOWN_ERROR",
            "UNEXPECTED_ERROR"
        ]

        test("ERROR_CODES is dict", isinstance(ERROR_CODES, dict))
        test("ERROR_CODES has 10 codes", len(ERROR_CODES) >= 10)

        for code in expected_codes:
            test(f"ERROR_CODES has {code}", code in ERROR_CODES)

        return True

    except Exception as e:
        test("error codes", False, str(e))
        return False


def test_logging_utilities():
    """Test logging utility functions."""
    print("\n--- Logging Utilities ---")

    try:
        # Import directly from errors module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "errors",
            PROJECT_ROOT / "src" / "fal_api" / "errors.py"
        )
        errors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(errors_module)

        log_error = errors_module.log_error
        log_warning = errors_module.log_warning
        import io
        import sys as sys_module

        # Capture stderr
        old_stderr = sys_module.stderr
        sys_module.stderr = io.StringIO()

        # Test log_error
        test_error = ValueError("test error")
        log_error(test_error, context="TEST")

        # Test log_warning
        log_warning("test warning", context="TEST")

        # Get output
        output = sys_module.stderr.getvalue()
        sys_module.stderr = old_stderr

        test("log_error outputs to stderr", "ERROR" in output or "error" in output.lower())
        test("log_warning outputs to stderr", "WARNING" in output or "warning" in output.lower())

        return True

    except Exception as e:
        test("logging utilities", False, str(e))
        return False


def test_error_propagation_in_workflow():
    """Test error propagation through a simulated workflow."""
    print("\n--- Error Propagation in Workflow ---")

    try:
        # Import directly from errors module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "errors",
            PROJECT_ROOT / "src" / "fal_api" / "errors.py"
        )
        errors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(errors_module)

        FalAPIError = errors_module.FalAPIError
        APIKeyError = errors_module.APIKeyError
        safe_result = errors_module.safe_result
        error_result = errors_module.error_result

        # Simulate workflow steps
        def step1_upload():
            # Simulate success
            return safe_result(True, url="https://example.com/image.png")

        def step2_process(upload_result):
            if not upload_result.get("success"):
                return upload_result  # Propagate error
            # Simulate API error
            raise FalAPIError("Processing failed", code="PROCESS_ERROR")

        def step3_download(process_result):
            if not process_result.get("success"):
                return process_result  # Propagate error
            return safe_result(True, path="/output/result.png")

        def run_workflow():
            try:
                r1 = step1_upload()
                if not r1.get("success"):
                    return r1
                r2 = step2_process(r1)
                if not r2.get("success"):
                    return r2
                r3 = step3_download(r2)
                return r3
            except FalAPIError as e:
                return error_result(e)

        result = run_workflow()
        test("workflow catches error", result["success"] == False)
        test("workflow has error message", "error" in result)
        test("error is from step2", "Processing" in result.get("error", "") or "PROCESS" in result.get("error_code", ""))

        return True

    except Exception as e:
        test("error propagation workflow", False, str(e))
        return False


# ============================================================
# MAIN
# ============================================================

def run_all_tests():
    """Run all error handling tests."""
    global passed, failed

    print("=" * 60)
    print("ERROR HANDLING TESTS")
    print("=" * 60)

    # Run tests
    test_custom_exceptions()
    test_error_utilities()
    test_validation_functions()
    test_decorator_handle_api_errors()
    test_retry_decorator()
    test_error_codes()
    test_logging_utilities()
    test_error_propagation_in_workflow()

    # Summary
    print("\n" + "=" * 60)
    print("ERROR HANDLING TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")

    if passed + failed > 0:
        print(f"Success Rate: {passed / (passed + failed) * 100:.1f}%")

    if errors:
        print("\n--- Errors ---")
        for name, msg in errors:
            print(f"  {name}: {msg}")

    print("\n" + "=" * 60)
    if failed == 0:
        print("ALL ERROR HANDLING TESTS PASSED")
        return 0
    else:
        print(f"ERROR HANDLING TESTS FAILED - {failed} failures")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
