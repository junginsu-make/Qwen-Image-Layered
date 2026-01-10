"""
TDD Tests for Health Check System.
Tests written BEFORE implementation (TDD approach).
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestHealthCheckModule(unittest.TestCase):
    """Tests for health_check module existence and structure."""

    @classmethod
    def setUpClass(cls):
        """Load health_check module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_module_has_health_checker_class(self):
        """Test that HealthChecker class exists."""
        self.assertTrue(hasattr(self.health_check, 'HealthChecker'))

    def test_module_has_check_status_enum(self):
        """Test that CheckStatus enum exists."""
        self.assertTrue(hasattr(self.health_check, 'CheckStatus'))

    def test_module_has_convenience_functions(self):
        """Test convenience functions exist."""
        self.assertTrue(hasattr(self.health_check, 'run_health_check'))
        self.assertTrue(hasattr(self.health_check, 'get_system_status'))
        self.assertTrue(hasattr(self.health_check, 'get_recent_errors'))


class TestCheckStatus(unittest.TestCase):
    """Tests for CheckStatus enum."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_check_status_has_ok(self):
        """Test OK status exists."""
        self.assertTrue(hasattr(self.health_check.CheckStatus, 'OK'))

    def test_check_status_has_warning(self):
        """Test WARNING status exists."""
        self.assertTrue(hasattr(self.health_check.CheckStatus, 'WARNING'))

    def test_check_status_has_error(self):
        """Test ERROR status exists."""
        self.assertTrue(hasattr(self.health_check.CheckStatus, 'ERROR'))

    def test_check_status_has_unknown(self):
        """Test UNKNOWN status exists."""
        self.assertTrue(hasattr(self.health_check.CheckStatus, 'UNKNOWN'))


class TestHealthChecker(unittest.TestCase):
    """Tests for HealthChecker class."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_health_checker_instantiation(self):
        """Test HealthChecker can be instantiated."""
        checker = self.health_check.HealthChecker()
        self.assertIsNotNone(checker)

    def test_check_all_returns_dict(self):
        """Test check_all returns a dictionary."""
        checker = self.health_check.HealthChecker()
        result = checker.check_all()
        self.assertIsInstance(result, dict)

    def test_check_all_has_required_keys(self):
        """Test check_all result has required keys."""
        checker = self.health_check.HealthChecker()
        result = checker.check_all()

        required_keys = [
            'api_key', 'dependencies', 'disk_space',
            'output_directory', 'overall_status', 'timestamp'
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_check_all_overall_status_is_enum(self):
        """Test overall_status is a CheckStatus value."""
        checker = self.health_check.HealthChecker()
        result = checker.check_all()
        self.assertIn(result['overall_status'],
                     [s.value for s in self.health_check.CheckStatus])


class TestAPIKeyCheck(unittest.TestCase):
    """Tests for API key validation."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_check_api_key_returns_dict(self):
        """Test _check_api_key returns dict."""
        checker = self.health_check.HealthChecker()
        result = checker._check_api_key()
        self.assertIsInstance(result, dict)

    def test_check_api_key_has_status(self):
        """Test API key check has status field."""
        checker = self.health_check.HealthChecker()
        result = checker._check_api_key()
        self.assertIn('status', result)

    def test_check_api_key_has_message(self):
        """Test API key check has message field."""
        checker = self.health_check.HealthChecker()
        result = checker._check_api_key()
        self.assertIn('message', result)

    def test_check_api_key_without_env_returns_error(self):
        """Test missing API key returns error status."""
        # Temporarily remove FAL_KEY
        original = os.environ.pop('FAL_KEY', None)
        try:
            checker = self.health_check.HealthChecker()
            result = checker._check_api_key()
            self.assertEqual(result['status'], 'error')
        finally:
            if original:
                os.environ['FAL_KEY'] = original

    def test_check_api_key_with_env_returns_ok(self):
        """Test valid API key returns ok status."""
        os.environ['FAL_KEY'] = 'test_key_12345'
        try:
            checker = self.health_check.HealthChecker()
            result = checker._check_api_key()
            self.assertEqual(result['status'], 'ok')
        finally:
            os.environ.pop('FAL_KEY', None)


class TestDependencyCheck(unittest.TestCase):
    """Tests for dependency checking."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_check_dependencies_returns_dict(self):
        """Test _check_dependencies returns dict."""
        checker = self.health_check.HealthChecker()
        result = checker._check_dependencies()
        self.assertIsInstance(result, dict)

    def test_check_dependencies_has_status(self):
        """Test dependency check has status field."""
        checker = self.health_check.HealthChecker()
        result = checker._check_dependencies()
        self.assertIn('status', result)

    def test_check_dependencies_has_packages(self):
        """Test dependency check lists packages."""
        checker = self.health_check.HealthChecker()
        result = checker._check_dependencies()
        self.assertIn('packages', result)
        self.assertIsInstance(result['packages'], dict)

    def test_check_dependencies_includes_pillow(self):
        """Test Pillow is in checked packages."""
        checker = self.health_check.HealthChecker()
        result = checker._check_dependencies()
        # Pillow might be listed as 'PIL' or 'Pillow'
        packages = result['packages']
        self.assertTrue(
            'PIL' in packages or 'Pillow' in packages or 'pillow' in packages,
            "Pillow not found in dependency check"
        )


class TestDiskSpaceCheck(unittest.TestCase):
    """Tests for disk space checking."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_check_disk_space_returns_dict(self):
        """Test _check_disk_space returns dict."""
        checker = self.health_check.HealthChecker()
        result = checker._check_disk_space()
        self.assertIsInstance(result, dict)

    def test_check_disk_space_has_status(self):
        """Test disk space check has status field."""
        checker = self.health_check.HealthChecker()
        result = checker._check_disk_space()
        self.assertIn('status', result)

    def test_check_disk_space_has_free_bytes(self):
        """Test disk space check includes free space."""
        checker = self.health_check.HealthChecker()
        result = checker._check_disk_space()
        self.assertIn('free_bytes', result)
        self.assertIsInstance(result['free_bytes'], int)

    def test_check_disk_space_has_free_human(self):
        """Test disk space check includes human-readable free space."""
        checker = self.health_check.HealthChecker()
        result = checker._check_disk_space()
        self.assertIn('free_human', result)


class TestOutputDirectoryCheck(unittest.TestCase):
    """Tests for output directory checking."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_check_output_directory_returns_dict(self):
        """Test _check_output_directory returns dict."""
        checker = self.health_check.HealthChecker()
        result = checker._check_output_directory()
        self.assertIsInstance(result, dict)

    def test_check_output_directory_with_custom_path(self):
        """Test output directory check with custom path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = self.health_check.HealthChecker(output_dir=tmpdir)
            result = checker._check_output_directory()
            self.assertEqual(result['status'], 'ok')

    def test_check_output_directory_creates_if_missing(self):
        """Test output directory is created if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_output"
            checker = self.health_check.HealthChecker(output_dir=str(new_dir))
            result = checker._check_output_directory()
            self.assertEqual(result['status'], 'ok')
            self.assertTrue(new_dir.exists())


class TestErrorTracking(unittest.TestCase):
    """Tests for error tracking functionality."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def setUp(self):
        """Clear errors before each test."""
        self.health_check.HealthChecker._errors = []

    def test_record_error(self):
        """Test error can be recorded."""
        checker = self.health_check.HealthChecker()
        checker.record_error("test_operation", "Test error message")
        errors = checker.get_recent_errors()
        self.assertEqual(len(errors), 1)

    def test_record_error_has_timestamp(self):
        """Test recorded error has timestamp."""
        checker = self.health_check.HealthChecker()
        checker.record_error("test_op", "Test message")
        errors = checker.get_recent_errors()
        self.assertIn('timestamp', errors[0])

    def test_record_error_has_operation(self):
        """Test recorded error has operation field."""
        checker = self.health_check.HealthChecker()
        checker.record_error("test_operation", "Test message")
        errors = checker.get_recent_errors()
        self.assertEqual(errors[0]['operation'], 'test_operation')

    def test_get_recent_errors_limit(self):
        """Test get_recent_errors respects limit."""
        checker = self.health_check.HealthChecker()
        for i in range(20):
            checker.record_error(f"op_{i}", f"Error {i}")

        errors = checker.get_recent_errors(limit=5)
        self.assertEqual(len(errors), 5)

    def test_clear_errors(self):
        """Test errors can be cleared."""
        checker = self.health_check.HealthChecker()
        checker.record_error("test", "message")
        checker.clear_errors()
        errors = checker.get_recent_errors()
        self.assertEqual(len(errors), 0)


class TestHealthReport(unittest.TestCase):
    """Tests for health report generation."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_get_report_returns_string(self):
        """Test get_report returns a string."""
        checker = self.health_check.HealthChecker()
        report = checker.get_report()
        self.assertIsInstance(report, str)

    def test_get_report_includes_status(self):
        """Test report includes overall status."""
        checker = self.health_check.HealthChecker()
        report = checker.get_report()
        self.assertIn('Status', report)

    def test_get_json_report(self):
        """Test JSON report generation."""
        checker = self.health_check.HealthChecker()
        json_report = checker.get_json_report()
        # Should be valid JSON
        data = json.loads(json_report)
        self.assertIsInstance(data, dict)


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for module-level convenience functions."""

    @classmethod
    def setUpClass(cls):
        """Load module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_check",
            Path(__file__).parent.parent / "src" / "fal_api" / "health_check.py"
        )
        cls.health_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.health_check)

    def test_run_health_check(self):
        """Test run_health_check function."""
        result = self.health_check.run_health_check()
        self.assertIsInstance(result, dict)
        self.assertIn('overall_status', result)

    def test_get_system_status(self):
        """Test get_system_status function."""
        status = self.health_check.get_system_status()
        self.assertIn(status, ['ok', 'warning', 'error', 'unknown'])

    def test_get_recent_errors_function(self):
        """Test module-level get_recent_errors function."""
        errors = self.health_check.get_recent_errors()
        self.assertIsInstance(errors, list)


class TestSkillIntegration(unittest.TestCase):
    """Tests for Skill file existence."""

    def test_system_health_skill_exists(self):
        """Test system-health skill directory exists."""
        skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "system-health"
        self.assertTrue(skill_path.exists(), "system-health skill directory not found")

    def test_system_health_skill_has_skill_md(self):
        """Test system-health skill has SKILL.md."""
        skill_file = Path(__file__).parent.parent / ".claude" / "skills" / "system-health" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "SKILL.md not found")

    def test_skill_md_has_triggers(self):
        """Test SKILL.md contains trigger keywords."""
        skill_file = Path(__file__).parent.parent / ".claude" / "skills" / "system-health" / "SKILL.md"
        content = skill_file.read_text()
        self.assertIn('trigger', content.lower())


class TestSubAgentIntegration(unittest.TestCase):
    """Tests for SubAgent file existence."""

    def test_system_diagnostics_agent_exists(self):
        """Test system_diagnostics agent file exists."""
        agent_path = Path(__file__).parent.parent / ".claude" / "agents" / "system_diagnostics.md"
        self.assertTrue(agent_path.exists(), "system_diagnostics.md not found")

    def test_agent_has_description(self):
        """Test agent file has description."""
        agent_file = Path(__file__).parent.parent / ".claude" / "agents" / "system_diagnostics.md"
        content = agent_file.read_text()
        self.assertIn('description', content.lower())


def run_tests():
    """Run all health check tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHealthCheckModule))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIKeyCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestDependencyCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestDiskSpaceCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputDirectoryCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthReport))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSubAgentIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()

    passed = result.testsRun - len(result.failures) - len(result.errors)
    failed = len(result.failures) + len(result.errors)

    print("\n" + "=" * 60)
    print("HEALTH CHECK TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {result.testsRun}")

    success_rate = (passed / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("\nALL HEALTH CHECK TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")

    sys.exit(0 if result.wasSuccessful() else 1)
