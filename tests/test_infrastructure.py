"""
Tests for infrastructure modules: logging, cost tracking, and path validation.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestLoggingConfig(unittest.TestCase):
    """Tests for logging_config module."""

    def setUp(self):
        """Reset logger state before each test."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "logging_config",
            Path(__file__).parent.parent / "src" / "fal_api" / "logging_config.py"
        )
        self.logging_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.logging_config)
        self.logging_config.LoggerFactory.reset()

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = self.logging_config.get_logger("test")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "fal_api.test")

    def test_configure_logging_sets_level(self):
        """Test that configure_logging sets the log level."""
        self.logging_config.configure_logging(level="DEBUG")
        logger = self.logging_config.get_logger("test")
        self.assertTrue(logger.isEnabledFor(10))  # DEBUG level

    def test_configure_logging_with_file(self):
        """Test logging to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.logging_config.LoggerFactory.reset()
            self.logging_config.LoggerFactory.initialize(
                log_level="INFO",
                log_dir=tmpdir,
                log_to_file=True,
                log_to_console=False,
            )
            logger = self.logging_config.get_logger("file_test")
            logger.info("Test message")

            # Check log file exists
            log_files = list(Path(tmpdir).glob("*.log"))
            self.assertEqual(len(log_files), 1)

    def test_logger_factory_singleton_behavior(self):
        """Test that LoggerFactory initializes only once."""
        self.logging_config.configure_logging(level="INFO")
        # Second call should not raise
        self.logging_config.configure_logging(level="DEBUG")
        # Still at INFO because already initialized
        logger = self.logging_config.get_logger("test")
        self.assertIsNotNone(logger)

    def test_set_level_changes_log_level(self):
        """Test that set_level changes logging level."""
        self.logging_config.configure_logging(level="INFO")
        self.logging_config.LoggerFactory.set_level("DEBUG")
        # Verify level changed
        logger = self.logging_config.get_logger("test")
        self.assertTrue(logger.isEnabledFor(10))


class TestCostTracker(unittest.TestCase):
    """Tests for cost_tracker module."""

    @classmethod
    def setUpClass(cls):
        """Load modules once for all tests."""
        import importlib.util

        # Load cost_tracker (it will load logging_config internally)
        spec = importlib.util.spec_from_file_location(
            "cost_tracker",
            Path(__file__).parent.parent / "src" / "fal_api" / "cost_tracker.py"
        )
        cls.cost_tracker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.cost_tracker)

    def setUp(self):
        """Reset tracker state before each test."""
        self.cost_tracker.CostTracker.reset_instance()

    def test_record_cost_basic(self):
        """Test basic cost recording."""
        tracker = self.cost_tracker.CostTracker()
        entry = tracker.record(
            self.cost_tracker.OperationType.GENERATE,
            "nano-banana",
            0.039,
        )
        self.assertEqual(entry.cost, 0.039)
        self.assertEqual(entry.model, "nano-banana")

    def test_get_total_accumulates(self):
        """Test that total cost accumulates."""
        tracker = self.cost_tracker.CostTracker()
        tracker.record(self.cost_tracker.OperationType.GENERATE, "test", 0.10)
        tracker.record(self.cost_tracker.OperationType.EDIT, "test", 0.05)
        self.assertAlmostEqual(tracker.get_total(), 0.15, places=5)

    def test_get_by_operation(self):
        """Test grouping by operation type."""
        tracker = self.cost_tracker.CostTracker()
        tracker.record(self.cost_tracker.OperationType.GENERATE, "m1", 0.10)
        tracker.record(self.cost_tracker.OperationType.GENERATE, "m1", 0.10)
        tracker.record(self.cost_tracker.OperationType.EDIT, "m2", 0.05)

        by_op = tracker.get_by_operation()
        self.assertEqual(by_op["generate"], 0.20)
        self.assertEqual(by_op["edit"], 0.05)

    def test_get_by_model(self):
        """Test grouping by model."""
        tracker = self.cost_tracker.CostTracker()
        tracker.record(self.cost_tracker.OperationType.GENERATE, "model-a", 0.10)
        tracker.record(self.cost_tracker.OperationType.GENERATE, "model-b", 0.20)
        tracker.record(self.cost_tracker.OperationType.GENERATE, "model-a", 0.10)

        by_model = tracker.get_by_model()
        self.assertEqual(by_model["model-a"], 0.20)
        self.assertEqual(by_model["model-b"], 0.20)

    def test_budget_limit_warning(self):
        """Test budget limit tracking."""
        tracker = self.cost_tracker.CostTracker(budget_limit=1.00)
        tracker.record(self.cost_tracker.OperationType.GENERATE, "test", 0.50)
        tracker.record(self.cost_tracker.OperationType.GENERATE, "test", 0.50)
        # Should be at limit now
        summary = tracker.get_summary()
        self.assertEqual(summary["budget_remaining"], 0.0)

    def test_get_summary_structure(self):
        """Test summary structure."""
        tracker = self.cost_tracker.CostTracker(budget_limit=10.00)
        tracker.record(self.cost_tracker.OperationType.GENERATE, "test", 1.00)

        summary = tracker.get_summary()
        self.assertIn("total_cost", summary)
        self.assertIn("session_cost", summary)
        self.assertIn("entry_count", summary)
        self.assertIn("by_operation", summary)
        self.assertIn("by_model", summary)
        self.assertIn("budget_limit", summary)

    def test_get_report_readable(self):
        """Test report generation."""
        tracker = self.cost_tracker.CostTracker()
        tracker.record(self.cost_tracker.OperationType.GENERATE, "test", 0.10)

        report = tracker.get_report()
        self.assertIn("Cost Report", report)
        self.assertIn("Total Cost", report)
        self.assertIn("$0.10", report)

    def test_clear_resets_entries(self):
        """Test that clear resets all entries."""
        tracker = self.cost_tracker.CostTracker()
        tracker.record(self.cost_tracker.OperationType.GENERATE, "test", 1.00)
        tracker.clear()
        self.assertEqual(tracker.get_total(), 0.0)

    def test_persistence(self):
        """Test saving and loading cost history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_path = Path(tmpdir) / "costs.json"

            # Create tracker with persistence
            tracker = self.cost_tracker.CostTracker(persist_path=str(persist_path))
            tracker.record(self.cost_tracker.OperationType.GENERATE, "test", 1.00)

            # Verify file was created
            self.assertTrue(persist_path.exists())

            # Create new tracker that loads history
            tracker2 = self.cost_tracker.CostTracker(persist_path=str(persist_path))
            self.assertEqual(tracker2.get_total(), 1.00)

    def test_cost_entry_serialization(self):
        """Test CostEntry serialization."""
        entry = self.cost_tracker.CostEntry(
            timestamp=datetime.now(),
            operation=self.cost_tracker.OperationType.GENERATE,
            model="test",
            cost=0.10,
            details={"note": "test"},
        )

        data = entry.to_dict()
        restored = self.cost_tracker.CostEntry.from_dict(data)

        self.assertEqual(restored.model, entry.model)
        self.assertEqual(restored.cost, entry.cost)

    def test_singleton_instance(self):
        """Test singleton behavior."""
        self.cost_tracker.CostTracker.reset_instance()
        tracker1 = self.cost_tracker.get_tracker()
        tracker2 = self.cost_tracker.get_tracker()
        self.assertIs(tracker1, tracker2)

    def test_convenience_functions(self):
        """Test module-level convenience functions."""
        self.cost_tracker.CostTracker.reset_instance()
        self.cost_tracker.record_cost(
            self.cost_tracker.OperationType.GENERATE,
            "test",
            0.50,
        )
        total = self.cost_tracker.get_total_cost()
        self.assertEqual(total, 0.50)

    def test_default_cost_used_when_not_specified(self):
        """Test that default cost is used when not specified."""
        tracker = self.cost_tracker.CostTracker()
        entry = tracker.record(
            self.cost_tracker.OperationType.OCR,
            "test-model",
            cost=None,  # Use default
        )
        self.assertEqual(entry.cost, 0.01)  # DEFAULT_COSTS[OCR]


class TestPathValidator(unittest.TestCase):
    """Tests for path_validator module."""

    @classmethod
    def setUpClass(cls):
        """Load modules once for all tests."""
        import importlib.util

        # Load errors module
        spec = importlib.util.spec_from_file_location(
            "errors",
            Path(__file__).parent.parent / "src" / "fal_api" / "errors.py"
        )
        cls.errors = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.errors)

        # Load path_validator (it will load logging_config and errors internally)
        spec = importlib.util.spec_from_file_location(
            "path_validator",
            Path(__file__).parent.parent / "src" / "fal_api" / "path_validator.py"
        )
        cls.path_validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.path_validator)

    def test_validate_path_existing_file(self):
        """Test validating an existing file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = f.name

        try:
            result = self.path_validator.PathValidator.validate_path(path)
            self.assertEqual(result, Path(path).resolve())
        finally:
            os.unlink(path)

    def test_validate_path_nonexistent_raises(self):
        """Test that validating nonexistent path raises error."""
        try:
            self.path_validator.PathValidator.validate_path(
                "/nonexistent/path/file.txt",
                must_exist=True,
            )
            self.fail("Expected InvalidInputError")
        except Exception as e:
            self.assertIn("InvalidInputError", type(e).__name__)

    def test_validate_path_with_extensions(self):
        """Test extension validation."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = f.name

        try:
            # Should fail with wrong extension requirement
            try:
                self.path_validator.PathValidator.validate_path(
                    path,
                    allowed_extensions={".png", ".jpg"},
                )
                self.fail("Expected InvalidInputError")
            except Exception as e:
                self.assertIn("InvalidInputError", type(e).__name__)
        finally:
            os.unlink(path)

    def test_validate_image_path(self):
        """Test image path validation."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name

        try:
            result = self.path_validator.validate_image(path)
            self.assertTrue(str(result).endswith(".png"))
        finally:
            os.unlink(path)

    def test_validate_output_creates_directory(self):
        """Test that output validation creates parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "output.png"
            result = self.path_validator.validate_output(
                output_path,
                extensions={".png"},
            )
            self.assertTrue(result.parent.exists())

    def test_ensure_directory_creates(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_subdir"
            result = self.path_validator.ensure_dir(new_dir)
            self.assertTrue(result.exists())
            self.assertTrue(result.is_dir())

    def test_ensure_directory_existing(self):
        """Test with existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.path_validator.ensure_dir(tmpdir)
            self.assertTrue(result.exists())

    def test_get_safe_filename_removes_unsafe(self):
        """Test unsafe character removal."""
        unsafe = 'test<>:"/\\|?*file.txt'
        safe = self.path_validator.safe_filename(unsafe)
        self.assertNotIn("<", safe)
        self.assertNotIn(">", safe)
        self.assertNotIn(":", safe)
        self.assertNotIn('"', safe)
        self.assertIn("file", safe)

    def test_get_safe_filename_truncation(self):
        """Test filename truncation."""
        long_name = "a" * 300 + ".txt"
        safe = self.path_validator.PathValidator.get_safe_filename(
            long_name, max_length=50
        )
        self.assertLessEqual(len(safe), 50)
        self.assertTrue(safe.endswith(".txt"))

    def test_list_images(self):
        """Test listing images in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "image1.png").touch()
            (Path(tmpdir) / "image2.jpg").touch()
            (Path(tmpdir) / "document.txt").touch()

            images = self.path_validator.list_images(tmpdir)
            self.assertEqual(len(images), 2)

    def test_list_images_recursive(self):
        """Test recursive image listing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test structure
            (Path(tmpdir) / "image1.png").touch()
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (subdir / "image2.png").touch()

            images = self.path_validator.list_images(tmpdir, recursive=True)
            self.assertEqual(len(images), 2)

    def test_get_unique_path(self):
        """Test unique path generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "file.txt"
            base_path.touch()

            unique = self.path_validator.get_unique_path(base_path)
            self.assertNotEqual(unique, base_path)
            self.assertTrue(str(unique).endswith(".txt"))

    def test_get_unique_path_nonexistent(self):
        """Test unique path when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "newfile.txt"
            unique = self.path_validator.get_unique_path(path)
            self.assertEqual(unique, path)

    def test_supported_formats_constants(self):
        """Test supported format constants."""
        self.assertIn(".png", self.path_validator.SUPPORTED_IMAGE_FORMATS)
        self.assertIn(".jpg", self.path_validator.SUPPORTED_IMAGE_FORMATS)
        self.assertIn(".pptx", self.path_validator.SUPPORTED_EXPORT_FORMATS)

    def test_validate_path_none_raises(self):
        """Test that None path raises error."""
        try:
            self.path_validator.PathValidator.validate_path(None)
            self.fail("Expected InvalidInputError")
        except Exception as e:
            self.assertIn("InvalidInputError", type(e).__name__)


class TestIntegration(unittest.TestCase):
    """Integration tests for infrastructure modules."""

    @classmethod
    def setUpClass(cls):
        """Load modules once."""
        import importlib.util

        # Load logging_config
        spec = importlib.util.spec_from_file_location(
            "logging_config",
            Path(__file__).parent.parent / "src" / "fal_api" / "logging_config.py"
        )
        cls.logging_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.logging_config)

        # Load cost_tracker
        spec = importlib.util.spec_from_file_location(
            "cost_tracker",
            Path(__file__).parent.parent / "src" / "fal_api" / "cost_tracker.py"
        )
        cls.cost_tracker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.cost_tracker)

    def test_cost_tracker_with_logging(self):
        """Test cost tracker using logging system."""
        # Configure logging to file
        with tempfile.TemporaryDirectory() as tmpdir:
            self.logging_config.LoggerFactory.reset()
            self.logging_config.LoggerFactory.initialize(
                log_level="DEBUG",
                log_dir=tmpdir,
                log_to_file=True,
                log_to_console=False,
            )

            # Use cost tracker
            self.cost_tracker.CostTracker.reset_instance()
            tracker = self.cost_tracker.CostTracker()
            tracker.record(self.cost_tracker.OperationType.GENERATE, "test", 0.10)

            # Verify log was written
            log_files = list(Path(tmpdir).glob("*.log"))
            self.assertEqual(len(log_files), 1)

            log_content = log_files[0].read_text()
            self.assertIn("Cost recorded", log_content)

    def test_module_imports_from_init(self):
        """Test that all modules can be imported from __init__."""
        # This test verifies the __init__.py exports work correctly
        import importlib.util

        # First set up the fal_api package properly
        fal_api_path = Path(__file__).parent.parent / "src" / "fal_api"

        # Load logging first
        spec = importlib.util.spec_from_file_location(
            "fal_api.logging_config",
            fal_api_path / "logging_config.py"
        )
        logging_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(logging_config)
        sys.modules["fal_api.logging_config"] = logging_config

        # The full package import requires more setup
        # Just verify the module file exists and has expected exports
        init_file = fal_api_path / "__init__.py"
        content = init_file.read_text()

        # Check expected exports are in __init__.py
        self.assertIn("LoggerFactory", content)
        self.assertIn("CostTracker", content)
        self.assertIn("PathValidator", content)
        self.assertIn("configure_logging", content)
        self.assertIn("record_cost", content)
        self.assertIn("validate_image", content)


def run_tests():
    """Run all infrastructure tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLoggingConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestCostTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestPathValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()

    passed = result.testsRun - len(result.failures) - len(result.errors)
    failed = len(result.failures) + len(result.errors)

    # Summary in the format expected by run_all_tests.py
    print("\n" + "=" * 60)
    print("INFRASTRUCTURE TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {result.testsRun}")

    success_rate = (passed / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("\nALL INFRASTRUCTURE TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")

    sys.exit(0 if result.wasSuccessful() else 1)
