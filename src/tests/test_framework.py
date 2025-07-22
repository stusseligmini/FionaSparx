"""
Basic Testing Infrastructure
Enterprise-grade testing framework for FionaSparx components

Features:
- Unit tests for core components
- Integration tests with mock services
- Performance benchmarks
- Health check validation
- Configuration testing
- AI model testing

Author: FionaSparx AI Content Creator
Version: 2.0.0 - Enterprise Edition
"""

import unittest
import time
import tempfile
import shutil
import os
import json
import logging
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.config_validator import EnhancedConfigValidator, ConfigValidationError
from utils.circuit_breaker import CircuitBreaker, CircuitBreakerError, ResilientAIWrapper
from utils.performance_monitor import PerformanceMonitor, PerformanceTimer
from utils.health_check import HealthCheckManager, SystemResourcesHealthCheck, DirectoryHealthCheck
from utils.enhanced_cli import EnhancedCLI

logger = logging.getLogger(__name__)

class TestEnhancedConfigValidator(unittest.TestCase):
    """Test enhanced configuration validator"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = EnhancedConfigValidator()
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config_validation(self):
        """Test validation with default configuration"""
        config = self.validator.validate_and_load_config("nonexistent_config.json")
        
        self.assertIn("ai_model", config)
        self.assertIn("platforms", config)
        self.assertIn("monitoring", config)
        self.assertIn("security", config)
        self.assertIn("error_handling", config)
    
    def test_environment_variable_override(self):
        """Test environment variable overrides"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'FIONA_AI_DEVICE': 'cpu',
            'FIONA_MONITORING_ENABLED': 'false',
            'FIONA_AI_MAX_RETRIES': '5'
        }):
            validator = EnhancedConfigValidator()
            config = validator.validate_and_load_config("nonexistent_config.json")
            
            self.assertEqual(config["ai_model"]["device"], "cpu")
            self.assertEqual(config["monitoring"]["enabled"], False)
            self.assertEqual(config["ai_model"]["max_retries"], 5)
    
    def test_invalid_config_validation(self):
        """Test validation with invalid configuration"""
        invalid_config = {
            "ai_model": {
                "device": "invalid_device",
                "image_size": [0, -1],
                "max_retries": -1
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        with self.assertRaises(ConfigValidationError):
            self.validator.validate_and_load_config(self.config_path)
    
    def test_partial_config_merge(self):
        """Test partial configuration merge with defaults"""
        partial_config = {
            "ai_model": {
                "device": "cpu"
            },
            "platforms": {
                "fanvue": {
                    "enabled": False
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(partial_config, f)
        
        config = self.validator.validate_and_load_config(self.config_path)
        
        # Should have defaults merged
        self.assertIn("monitoring", config)
        self.assertEqual(config["ai_model"]["device"], "cpu")
        self.assertEqual(config["platforms"]["fanvue"]["enabled"], False)
        self.assertIn("loyalfans", config["platforms"])

class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=1,
            name="test_circuit"
        )
    
    def test_circuit_breaker_normal_operation(self):
        """Test normal operation of circuit breaker"""
        @self.circuit_breaker
        def successful_operation():
            return "success"
        
        result = successful_operation()
        self.assertEqual(result, "success")
        self.assertTrue(self.circuit_breaker.is_closed)
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        @self.circuit_breaker
        def failing_operation():
            raise ValueError("Test failure")
        
        # Cause failures to trip the circuit
        for _ in range(3):
            with self.assertRaises(ValueError):
                failing_operation()
        
        # Circuit should be open now
        self.assertTrue(self.circuit_breaker.is_open)
        
        # Next call should raise CircuitBreakerError
        with self.assertRaises(CircuitBreakerError):
            failing_operation()
    
    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state"""
        @self.circuit_breaker
        def operation(should_fail=True):
            if should_fail:
                raise ValueError("Test failure")
            return "success"
        
        # Trip the circuit
        for _ in range(3):
            with self.assertRaises(ValueError):
                operation(should_fail=True)
        
        self.assertTrue(self.circuit_breaker.is_open)
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Should try half-open state and recover
        result = operation(should_fail=False)
        self.assertEqual(result, "success")
        self.assertTrue(self.circuit_breaker.is_closed)
    
    def test_circuit_breaker_metrics(self):
        """Test circuit breaker metrics collection"""
        @self.circuit_breaker
        def test_operation(should_fail=False):
            if should_fail:
                raise ValueError("Test failure")
            return "success"
        
        # Some successful calls
        for _ in range(5):
            test_operation(should_fail=False)
        
        # Some failed calls
        for _ in range(2):
            with self.assertRaises(ValueError):
                test_operation(should_fail=True)
        
        metrics = self.circuit_breaker.get_metrics()
        
        self.assertEqual(metrics["metrics"]["total_calls"], 7)
        self.assertEqual(metrics["metrics"]["successful_calls"], 5)
        self.assertEqual(metrics["metrics"]["failed_calls"], 2)
        self.assertAlmostEqual(metrics["metrics"]["success_rate"], 71.4, places=1)

class TestPerformanceMonitor(unittest.TestCase):
    """Test performance monitoring functionality"""
    
    def setUp(self):
        """Set up test environment"""
        config = {
            "monitoring": {
                "enabled": True,
                "metrics_interval": 1,
                "max_history_size": 100
            }
        }
        self.monitor = PerformanceMonitor(config)
    
    def tearDown(self):
        """Clean up test environment"""
        self.monitor.stop_monitoring()
    
    def test_performance_timer(self):
        """Test performance timer context manager"""
        with PerformanceTimer(self.monitor, "test_operation", "test_model") as timer:
            time.sleep(0.1)  # Simulate work
        
        # Check that metrics were recorded
        ai_metrics = self.monitor.collector.get_recent_ai_metrics(1)
        self.assertEqual(len(ai_metrics), 1)
        self.assertEqual(ai_metrics[0]["metrics"]["operation_type"], "test_operation")
        self.assertTrue(ai_metrics[0]["metrics"]["success"])
        self.assertGreater(ai_metrics[0]["metrics"]["execution_time_ms"], 90)
    
    def test_ai_operation_recording(self):
        """Test AI operation metrics recording"""
        self.monitor.record_ai_operation(
            operation_type="text_generation",
            execution_time_ms=150.5,
            success=True,
            model_used="test_model",
            input_size=100,
            output_size=50
        )
        
        ai_metrics = self.monitor.collector.get_recent_ai_metrics(1)
        self.assertEqual(len(ai_metrics), 1)
        
        metrics = ai_metrics[0]["metrics"]
        self.assertEqual(metrics["operation_type"], "text_generation")
        self.assertEqual(metrics["execution_time_ms"], 150.5)
        self.assertTrue(metrics["success"])
        self.assertEqual(metrics["input_size"], 100)
        self.assertEqual(metrics["output_size"], 50)
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        # Record some test metrics
        for i in range(5):
            self.monitor.record_ai_operation(
                operation_type="test_operation",
                execution_time_ms=100 + i * 10,
                success=i < 4,  # One failure
                model_used="test_model"
            )
        
        summary = self.monitor.get_performance_summary()
        
        self.assertIn("system_health", summary)
        self.assertIn("ai_operations", summary)
        self.assertEqual(summary["ai_operations"]["total_operations"], 5)
        self.assertEqual(summary["ai_operations"]["success_rate"], 80.0)

class TestHealthCheckManager(unittest.TestCase):
    """Test health check manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        config = {
            "monitoring": {
                "enabled": True,
                "health_check_interval": 1
            }
        }
        self.temp_dir = tempfile.mkdtemp()
        self.health_manager = HealthCheckManager(config)
    
    def tearDown(self):
        """Clean up test environment"""
        self.health_manager.stop_monitoring()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_system_resources_health_check(self):
        """Test system resources health check"""
        health_check = SystemResourcesHealthCheck(
            cpu_warning=50.0,  # Lower thresholds for testing
            memory_warning=50.0,
            disk_warning=50.0
        )
        
        result = health_check.check()
        
        self.assertEqual(result.name, "system_resources")
        self.assertIn(result.status.value, ["healthy", "warning", "critical"])
        self.assertIn("cpu_percent", result.details)
        self.assertIn("memory_percent", result.details)
        self.assertIn("disk_percent", result.details)
    
    def test_directory_health_check(self):
        """Test directory accessibility health check"""
        # Create test directories
        test_dirs = [
            os.path.join(self.temp_dir, "dir1"),
            os.path.join(self.temp_dir, "dir2"),
            "/nonexistent/directory"
        ]
        
        os.makedirs(test_dirs[0])
        os.makedirs(test_dirs[1])
        
        health_check = DirectoryHealthCheck(test_dirs)
        result = health_check.check()
        
        self.assertEqual(result.name, "directories")
        self.assertIn("directories", result.details)
        self.assertEqual(len(result.details["directories"]), 3)
        
        # Should be critical due to nonexistent directory
        self.assertEqual(result.status.value, "critical")
    
    def test_overall_health_status(self):
        """Test overall health status calculation"""
        results = self.health_manager.run_all_checks()
        
        self.assertGreater(len(results), 0)
        
        overall_health = self.health_manager.get_overall_health()
        
        self.assertIn("status", overall_health)
        self.assertIn("checks", overall_health)
        self.assertIn("summary", overall_health)
        self.assertIn(overall_health["status"], ["healthy", "warning", "critical", "unknown"])

class TestEnhancedCLI(unittest.TestCase):
    """Test enhanced CLI functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.cli = EnhancedCLI(enable_colors=False)  # Disable colors for testing
    
    def test_colorize_method(self):
        """Test color application"""
        # With colors disabled, should return original text
        result = self.cli._colorize("test", "\033[31m")
        self.assertEqual(result, "test")
        
        # With colors enabled
        cli_with_colors = EnhancedCLI(enable_colors=True)
        result = cli_with_colors._colorize("test", "\033[31m")
        self.assertEqual(result, "\033[31mtest\033[0m")
    
    def test_progress_bar(self):
        """Test progress bar functionality"""
        progress_bar = self.cli.create_progress_bar(10, "Test Progress")
        
        self.assertEqual(progress_bar.total, 10)
        self.assertEqual(progress_bar.current, 0)
        self.assertEqual(progress_bar.description, "Test Progress")
        
        progress_bar.update(5)
        self.assertEqual(progress_bar.current, 5)
        
        progress_bar.update(10)  # Should cap at total
        self.assertEqual(progress_bar.current, 10)

class TestResilientAIWrapper(unittest.TestCase):
    """Test resilient AI wrapper functionality"""
    
    def setUp(self):
        """Set up test environment"""
        config = {
            "error_handling": {
                "circuit_breaker_enabled": True,
                "circuit_breaker_failure_threshold": 3,
                "circuit_breaker_timeout": 1,
                "exponential_backoff_enabled": True,
                "max_retries": 2,
                "retry_delay_base": 0.1
            }
        }
        self.wrapper = ResilientAIWrapper(config)
    
    def test_successful_operation(self):
        """Test successful operation execution"""
        def successful_operation():
            return "success"
        
        result = self.wrapper.execute_with_resilience(
            successful_operation,
            self.wrapper.text_circuit,
            "test_operation"
        )
        
        self.assertEqual(result, "success")
    
    def test_operation_with_retries(self):
        """Test operation that succeeds after retries"""
        call_count = 0
        
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = self.wrapper.execute_with_resilience(
            flaky_operation,
            self.wrapper.text_circuit,
            "flaky_operation"
        )
        
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_operation_failure_after_retries(self):
        """Test operation that fails after all retries"""
        def failing_operation():
            raise ValueError("Persistent failure")
        
        with self.assertRaises(ValueError):
            self.wrapper.execute_with_resilience(
                failing_operation,
                self.wrapper.text_circuit,
                "failing_operation"
            )
    
    def test_health_status(self):
        """Test health status reporting"""
        health_status = self.wrapper.get_health_status()
        
        self.assertIn("text_generation", health_status)
        self.assertIn("image_generation", health_status)
        self.assertIn("overall_health", health_status)

class TestRunner:
    """Test runner for FionaSparx testing infrastructure"""
    
    def __init__(self, verbose: bool = True):
        """Initialize test runner"""
        self.verbose = verbose
        self.cli = EnhancedCLI()
        
        # Configure logging for tests
        logging.basicConfig(
            level=logging.WARNING,  # Reduce noise during tests
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def run_all_tests(self) -> bool:
        """Run all test suites"""
        self.cli.print_banner()
        self.cli.print_header("FionaSparx Testing Infrastructure")
        
        test_classes = [
            TestEnhancedConfigValidator,
            TestCircuitBreaker,
            TestPerformanceMonitor,
            TestHealthCheckManager,
            TestEnhancedCLI,
            TestResilientAIWrapper
        ]
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        progress_bar = self.cli.create_progress_bar(len(test_classes), "Running test suites")
        
        for test_class in test_classes:
            progress_bar.set_description(f"Testing {test_class.__name__}")
            
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(
                verbosity=2 if self.verbose else 1,
                stream=open(os.devnull, 'w') if not self.verbose else sys.stdout
            )
            
            result = runner.run(suite)
            
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            
            if result.failures or result.errors:
                self.cli.print_error(f"Test suite {test_class.__name__} had issues")
                if self.verbose:
                    for test, traceback in result.failures + result.errors:
                        self.cli.print_error(f"  {test}: {traceback}")
            else:
                self.cli.print_success(f"Test suite {test_class.__name__} passed")
            
            progress_bar.update(1)
        
        # Print summary
        self.cli.print_header("Test Results Summary")
        self.cli.print_info(f"Total Tests: {total_tests}")
        
        if total_failures == 0 and total_errors == 0:
            self.cli.print_success("All tests passed!")
            return True
        else:
            self.cli.print_error(f"Failures: {total_failures}, Errors: {total_errors}")
            return False
    
    def run_specific_test(self, test_class_name: str) -> bool:
        """Run a specific test class"""
        test_classes = {
            "config": TestEnhancedConfigValidator,
            "circuit_breaker": TestCircuitBreaker,
            "performance": TestPerformanceMonitor,
            "health": TestHealthCheckManager,
            "cli": TestEnhancedCLI,
            "resilient": TestResilientAIWrapper
        }
        
        if test_class_name not in test_classes:
            self.cli.print_error(f"Unknown test class: {test_class_name}")
            self.cli.print_info(f"Available tests: {', '.join(test_classes.keys())}")
            return False
        
        self.cli.print_header(f"Running {test_class_name} tests")
        
        test_class = test_classes[test_class_name]
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        success = len(result.failures) == 0 and len(result.errors) == 0
        
        if success:
            self.cli.print_success("Tests passed!")
        else:
            self.cli.print_error("Tests failed!")
        
        return success

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)