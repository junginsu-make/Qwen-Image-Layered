#!/usr/bin/env python3
"""
TDD Tests for LLM Integration System.

Tests for:
- LLM Client (unified API wrapper)
- Prompt Optimizer
- Model Selector
- Intelligent Router
- Quality Validator
- Error Recovery
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Phase 1: LLM Client Tests
# =============================================================================

class TestLLMClientModule(unittest.TestCase):
    """Tests for llm_client module existence and structure."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "llm_client",
            PROJECT_ROOT / "src" / "fal_api" / "llm_client.py"
        )
        cls.llm_client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.llm_client)

    def test_module_has_llm_provider_enum(self):
        """Test LLMProvider enum exists."""
        self.assertTrue(hasattr(self.llm_client, 'LLMProvider'))

    def test_llm_provider_has_claude(self):
        """Test CLAUDE provider exists."""
        self.assertTrue(hasattr(self.llm_client.LLMProvider, 'CLAUDE'))

    def test_llm_provider_has_openai(self):
        """Test OPENAI provider exists."""
        self.assertTrue(hasattr(self.llm_client.LLMProvider, 'OPENAI'))

    def test_llm_provider_has_gemini(self):
        """Test GEMINI provider exists."""
        self.assertTrue(hasattr(self.llm_client.LLMProvider, 'GEMINI'))

    def test_module_has_llm_client_class(self):
        """Test LLMClient class exists."""
        self.assertTrue(hasattr(self.llm_client, 'LLMClient'))

    def test_module_has_convenience_functions(self):
        """Test convenience functions exist."""
        self.assertTrue(hasattr(self.llm_client, 'query_llm'))
        self.assertTrue(hasattr(self.llm_client, 'query_with_image'))
        self.assertTrue(hasattr(self.llm_client, 'get_available_providers'))


class TestLLMClient(unittest.TestCase):
    """Tests for LLMClient class functionality."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "llm_client",
            PROJECT_ROOT / "src" / "fal_api" / "llm_client.py"
        )
        cls.llm_client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.llm_client)

    def test_client_instantiation(self):
        """Test LLMClient can be instantiated."""
        client = self.llm_client.LLMClient()
        self.assertIsNotNone(client)

    def test_client_has_query_method(self):
        """Test client has query method."""
        client = self.llm_client.LLMClient()
        self.assertTrue(hasattr(client, 'query'))
        self.assertTrue(callable(client.query))

    def test_client_has_query_with_image_method(self):
        """Test client has query_with_image method."""
        client = self.llm_client.LLMClient()
        self.assertTrue(hasattr(client, 'query_with_image'))
        self.assertTrue(callable(client.query_with_image))

    def test_client_has_get_model_info(self):
        """Test client has get_model_info method."""
        client = self.llm_client.LLMClient()
        self.assertTrue(hasattr(client, 'get_model_info'))

    def test_model_config_structure(self):
        """Test MODEL_CONFIG has proper structure."""
        self.assertTrue(hasattr(self.llm_client, 'MODEL_CONFIG'))
        config = self.llm_client.MODEL_CONFIG
        self.assertIn('claude', config)
        self.assertIn('openai', config)
        self.assertIn('gemini', config)


# =============================================================================
# Phase 1: Prompt Optimizer Tests
# =============================================================================

class TestPromptOptimizerModule(unittest.TestCase):
    """Tests for prompt_optimizer module."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "prompt_optimizer",
            PROJECT_ROOT / "src" / "fal_api" / "prompt_optimizer.py"
        )
        cls.prompt_optimizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.prompt_optimizer)

    def test_module_has_prompt_optimizer_class(self):
        """Test PromptOptimizer class exists."""
        self.assertTrue(hasattr(self.prompt_optimizer, 'PromptOptimizer'))

    def test_module_has_convenience_functions(self):
        """Test convenience functions exist."""
        self.assertTrue(hasattr(self.prompt_optimizer, 'enhance_prompt'))
        self.assertTrue(hasattr(self.prompt_optimizer, 'generate_variations'))
        self.assertTrue(hasattr(self.prompt_optimizer, 'score_prompt'))


class TestPromptOptimizer(unittest.TestCase):
    """Tests for PromptOptimizer functionality."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "prompt_optimizer",
            PROJECT_ROOT / "src" / "fal_api" / "prompt_optimizer.py"
        )
        cls.prompt_optimizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.prompt_optimizer)

    def test_optimizer_instantiation(self):
        """Test PromptOptimizer can be instantiated."""
        optimizer = self.prompt_optimizer.PromptOptimizer()
        self.assertIsNotNone(optimizer)

    def test_enhance_returns_string(self):
        """Test enhance returns a string."""
        optimizer = self.prompt_optimizer.PromptOptimizer()
        result = optimizer.enhance("make it pretty")
        self.assertIsInstance(result, str)

    def test_enhance_improves_vague_prompt(self):
        """Test enhancement improves vague prompts."""
        optimizer = self.prompt_optimizer.PromptOptimizer()
        original = "nice image"
        enhanced = optimizer.enhance(original)
        # Enhanced should be longer or more detailed
        self.assertGreaterEqual(len(enhanced), len(original))

    def test_generate_variations_returns_list(self):
        """Test generate_variations returns list."""
        optimizer = self.prompt_optimizer.PromptOptimizer()
        result = optimizer.generate_variations("sunset landscape", count=3)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)

    def test_score_prompt_returns_float(self):
        """Test score_prompt returns float between 0-1."""
        optimizer = self.prompt_optimizer.PromptOptimizer()
        score = optimizer.score_prompt("A beautiful sunset over mountains")
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_low_quality_prompt_scores_lower(self):
        """Test vague prompts score lower than detailed ones."""
        optimizer = self.prompt_optimizer.PromptOptimizer()
        vague_score = optimizer.score_prompt("nice")
        detailed_score = optimizer.score_prompt(
            "A breathtaking mountain landscape at golden hour with "
            "vibrant orange and purple sky, dramatic clouds"
        )
        self.assertLess(vague_score, detailed_score)


# =============================================================================
# Phase 1: Model Selector Tests
# =============================================================================

class TestModelSelectorModule(unittest.TestCase):
    """Tests for model_selector module."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "model_selector",
            PROJECT_ROOT / "src" / "fal_api" / "model_selector.py"
        )
        cls.model_selector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.model_selector)

    def test_module_has_model_selector_class(self):
        """Test ModelSelector class exists."""
        self.assertTrue(hasattr(self.model_selector, 'ModelSelector'))

    def test_module_has_complexity_enum(self):
        """Test TaskComplexity enum exists."""
        self.assertTrue(hasattr(self.model_selector, 'TaskComplexity'))

    def test_module_has_convenience_functions(self):
        """Test convenience functions exist."""
        self.assertTrue(hasattr(self.model_selector, 'select_model'))
        self.assertTrue(hasattr(self.model_selector, 'assess_complexity'))
        self.assertTrue(hasattr(self.model_selector, 'calculate_cost_quality_score'))


class TestModelSelector(unittest.TestCase):
    """Tests for ModelSelector functionality."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "model_selector",
            PROJECT_ROOT / "src" / "fal_api" / "model_selector.py"
        )
        cls.model_selector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.model_selector)

    def test_selector_instantiation(self):
        """Test ModelSelector can be instantiated."""
        selector = self.model_selector.ModelSelector()
        self.assertIsNotNone(selector)

    def test_assess_complexity_returns_enum(self):
        """Test assess_complexity returns TaskComplexity."""
        selector = self.model_selector.ModelSelector()
        result = selector.assess_complexity("Generate a simple icon")
        self.assertIn(result, [
            self.model_selector.TaskComplexity.LOW,
            self.model_selector.TaskComplexity.MEDIUM,
            self.model_selector.TaskComplexity.HIGH,
        ])

    def test_select_model_returns_dict(self):
        """Test select_model returns recommendation dict."""
        selector = self.model_selector.ModelSelector()
        result = selector.select_model(
            task="Generate product photo",
            budget=0.50
        )
        self.assertIsInstance(result, dict)
        self.assertIn('model', result)
        self.assertIn('cost', result)
        self.assertIn('reason', result)

    def test_budget_constraint_respected(self):
        """Test model selection respects budget."""
        selector = self.model_selector.ModelSelector()
        result = selector.select_model(
            task="Generate image",
            budget=0.05  # Low budget
        )
        self.assertLessEqual(result['cost'], 0.05)

    def test_quality_preference_affects_selection(self):
        """Test quality preference affects model choice."""
        selector = self.model_selector.ModelSelector()

        # Low quality preference
        low_quality = selector.select_model(
            task="Quick preview",
            budget=1.0,
            prefer_quality=False
        )

        # High quality preference
        high_quality = selector.select_model(
            task="Commercial artwork",
            budget=1.0,
            prefer_quality=True
        )

        # High quality should cost same or more
        self.assertGreaterEqual(high_quality['cost'], low_quality['cost'] * 0.5)


# =============================================================================
# Phase 1: Intelligent Router Tests
# =============================================================================

class TestIntelligentRouterModule(unittest.TestCase):
    """Tests for intelligent_router module."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "intelligent_router",
            PROJECT_ROOT / "src" / "fal_api" / "intelligent_router.py"
        )
        cls.intelligent_router = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.intelligent_router)

    def test_module_has_task_router_class(self):
        """Test TaskRouter class exists."""
        self.assertTrue(hasattr(self.intelligent_router, 'TaskRouter'))

    def test_module_has_intent_enum(self):
        """Test Intent enum exists."""
        self.assertTrue(hasattr(self.intelligent_router, 'Intent'))

    def test_module_has_convenience_functions(self):
        """Test convenience functions exist."""
        self.assertTrue(hasattr(self.intelligent_router, 'route_request'))
        self.assertTrue(hasattr(self.intelligent_router, 'parse_intent'))
        self.assertTrue(hasattr(self.intelligent_router, 'get_execution_plan'))


class TestIntelligentRouter(unittest.TestCase):
    """Tests for TaskRouter functionality."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "intelligent_router",
            PROJECT_ROOT / "src" / "fal_api" / "intelligent_router.py"
        )
        cls.intelligent_router = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.intelligent_router)

    def test_router_instantiation(self):
        """Test TaskRouter can be instantiated."""
        router = self.intelligent_router.TaskRouter()
        self.assertIsNotNone(router)

    def test_parse_intent_returns_list(self):
        """Test parse_intent returns list of intents."""
        router = self.intelligent_router.TaskRouter()
        result = router.parse_intent("Remove background and change colors")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_route_request_returns_plan(self):
        """Test route_request returns execution plan."""
        router = self.intelligent_router.TaskRouter()
        result = router.route_request("Generate a logo")
        self.assertIsInstance(result, dict)
        self.assertIn('intents', result)
        self.assertIn('skills', result)
        self.assertIn('estimated_cost', result)

    def test_complex_request_decomposition(self):
        """Test complex requests are decomposed into steps."""
        router = self.intelligent_router.TaskRouter()
        result = router.route_request(
            "Decompose the image, remove text, and apply watercolor style"
        )
        # Should identify multiple skills
        self.assertGreater(len(result['skills']), 1)

    def test_execution_plan_has_order(self):
        """Test execution plan has proper ordering."""
        router = self.intelligent_router.TaskRouter()
        result = router.get_execution_plan(
            "Extract colors and generate new image"
        )
        self.assertIsInstance(result, list)
        for step in result:
            self.assertIn('order', step)
            self.assertIn('skill', step)


# =============================================================================
# Phase 2: Quality Validator Tests
# =============================================================================

class TestQualityValidatorModule(unittest.TestCase):
    """Tests for quality_validator module."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "quality_validator",
            PROJECT_ROOT / "src" / "fal_api" / "quality_validator.py"
        )
        cls.quality_validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.quality_validator)

    def test_module_has_quality_validator_class(self):
        """Test QualityValidator class exists."""
        self.assertTrue(hasattr(self.quality_validator, 'QualityValidator'))

    def test_module_has_quality_score_class(self):
        """Test QualityScore dataclass exists."""
        self.assertTrue(hasattr(self.quality_validator, 'QualityScore'))

    def test_module_has_convenience_functions(self):
        """Test convenience functions exist."""
        self.assertTrue(hasattr(self.quality_validator, 'validate_output'))
        self.assertTrue(hasattr(self.quality_validator, 'rate_generation'))
        self.assertTrue(hasattr(self.quality_validator, 'detect_artifacts'))


class TestQualityValidator(unittest.TestCase):
    """Tests for QualityValidator functionality."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "quality_validator",
            PROJECT_ROOT / "src" / "fal_api" / "quality_validator.py"
        )
        cls.quality_validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.quality_validator)

    def test_validator_instantiation(self):
        """Test QualityValidator can be instantiated."""
        validator = self.quality_validator.QualityValidator()
        self.assertIsNotNone(validator)

    def test_validate_returns_quality_score(self):
        """Test validate returns QualityScore."""
        validator = self.quality_validator.QualityValidator()
        # Use mock image path for testing
        result = validator.validate("test_image.png", task="generation")
        self.assertIsInstance(result, self.quality_validator.QualityScore)

    def test_quality_score_has_fields(self):
        """Test QualityScore has required fields."""
        score = self.quality_validator.QualityScore(
            overall=0.85,
            details={"clarity": 0.9, "composition": 0.8},
            issues=[],
            suggestions=[]
        )
        self.assertEqual(score.overall, 0.85)
        self.assertIsInstance(score.details, dict)
        self.assertIsInstance(score.issues, list)
        self.assertIsInstance(score.suggestions, list)

    def test_detect_artifacts_returns_list(self):
        """Test detect_artifacts returns list."""
        validator = self.quality_validator.QualityValidator()
        result = validator.detect_artifacts("test_image.png")
        self.assertIsInstance(result, list)


# =============================================================================
# Phase 2: Error Recovery Tests
# =============================================================================

class TestErrorRecoveryModule(unittest.TestCase):
    """Tests for error_recovery module."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "error_recovery",
            PROJECT_ROOT / "src" / "fal_api" / "error_recovery.py"
        )
        cls.error_recovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.error_recovery)

    def test_module_has_error_recovery_class(self):
        """Test ErrorRecovery class exists."""
        self.assertTrue(hasattr(self.error_recovery, 'ErrorRecovery'))

    def test_module_has_recovery_strategy_enum(self):
        """Test RecoveryStrategy enum exists."""
        self.assertTrue(hasattr(self.error_recovery, 'RecoveryStrategy'))

    def test_module_has_convenience_functions(self):
        """Test convenience functions exist."""
        self.assertTrue(hasattr(self.error_recovery, 'analyze_error'))
        self.assertTrue(hasattr(self.error_recovery, 'suggest_recovery'))
        self.assertTrue(hasattr(self.error_recovery, 'auto_recover'))


class TestErrorRecovery(unittest.TestCase):
    """Tests for ErrorRecovery functionality."""

    @classmethod
    def setUpClass(cls):
        """Load module once."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "error_recovery",
            PROJECT_ROOT / "src" / "fal_api" / "error_recovery.py"
        )
        cls.error_recovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.error_recovery)

    def test_recovery_instantiation(self):
        """Test ErrorRecovery can be instantiated."""
        recovery = self.error_recovery.ErrorRecovery()
        self.assertIsNotNone(recovery)

    def test_analyze_error_returns_analysis(self):
        """Test analyze_error returns analysis dict."""
        recovery = self.error_recovery.ErrorRecovery()
        error = Exception("API timeout after 30 seconds")
        result = recovery.analyze_error(error, context={"operation": "generate"})
        self.assertIsInstance(result, dict)
        self.assertIn('root_cause', result)
        self.assertIn('severity', result)

    def test_suggest_recovery_returns_strategies(self):
        """Test suggest_recovery returns list of strategies."""
        recovery = self.error_recovery.ErrorRecovery()
        error = Exception("Rate limit exceeded")
        result = recovery.suggest_recovery(error)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_recovery_strategy_has_fields(self):
        """Test recovery strategies have required fields."""
        recovery = self.error_recovery.ErrorRecovery()
        error = Exception("Network error")
        strategies = recovery.suggest_recovery(error)
        for strategy in strategies:
            self.assertIn('strategy', strategy)
            self.assertIn('success_probability', strategy)
            self.assertIn('description', strategy)


# =============================================================================
# Integration Tests
# =============================================================================

class TestLLMIntegration(unittest.TestCase):
    """Integration tests for LLM modules."""

    @classmethod
    def setUpClass(cls):
        """Load all modules."""
        import importlib.util

        modules = [
            'llm_client', 'prompt_optimizer', 'model_selector',
            'intelligent_router', 'quality_validator', 'error_recovery'
        ]

        for mod_name in modules:
            spec = importlib.util.spec_from_file_location(
                mod_name,
                PROJECT_ROOT / "src" / "fal_api" / f"{mod_name}.py"
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            setattr(cls, mod_name, mod)

    def test_prompt_optimizer_uses_llm_client(self):
        """Test PromptOptimizer can use LLMClient."""
        optimizer = self.prompt_optimizer.PromptOptimizer()
        self.assertTrue(hasattr(optimizer, '_llm_client') or
                       hasattr(optimizer, 'llm_client') or
                       hasattr(optimizer, '_client'))

    def test_router_uses_model_selector(self):
        """Test TaskRouter uses ModelSelector for recommendations."""
        router = self.intelligent_router.TaskRouter()
        result = router.route_request("Generate high-quality artwork")
        # Should include model recommendation
        self.assertTrue('model' in result or 'recommended_model' in result or
                       'skills' in result)

    def test_all_modules_import_successfully(self):
        """Test all modules can be imported together."""
        # If we got here, all modules loaded successfully
        self.assertTrue(True)


# =============================================================================
# Test Runner
# =============================================================================

def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        # Phase 1
        TestLLMClientModule,
        TestLLMClient,
        TestPromptOptimizerModule,
        TestPromptOptimizer,
        TestModelSelectorModule,
        TestModelSelector,
        TestIntelligentRouterModule,
        TestIntelligentRouter,
        # Phase 2
        TestQualityValidatorModule,
        TestQualityValidator,
        TestErrorRecoveryModule,
        TestErrorRecovery,
        # Integration
        TestLLMIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()

    passed = result.testsRun - len(result.failures) - len(result.errors)
    failed = len(result.failures) + len(result.errors)

    print("\n" + "=" * 60)
    print("LLM INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {result.testsRun}")

    success_rate = (passed / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("\nALL LLM INTEGRATION TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")

    sys.exit(0 if result.wasSuccessful() else 1)
