"""
Enhanced CLI Interface
Enterprise-grade command line interface with progress indicators and rich feedback

Features:
- Rich progress bars and status indicators
- Colored output for better readability
- Interactive prompts and confirmations
- Detailed operation logging
- Performance metrics display
- Error handling with clear messages

Author: FionaSparx AI Content Creator
Version: 2.0.0 - Enterprise Edition
"""

import sys
import time
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Regular colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'

class ProgressBar:
    """Simple progress bar implementation"""
    
    def __init__(self, total: int, description: str = "", width: int = 50):
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.start_time = time.time()
        
    def update(self, progress: int = 1):
        """Update progress bar"""
        self.current = min(self.current + progress, self.total)
        self._draw()
    
    def set_description(self, description: str):
        """Update description"""
        self.description = description
        self._draw()
    
    def _draw(self):
        """Draw the progress bar"""
        if self.total == 0:
            percentage = 100
        else:
            percentage = (self.current / self.total) * 100
        
        filled_width = int(self.width * self.current // self.total) if self.total > 0 else self.width
        bar = "█" * filled_width + "░" * (self.width - filled_width)
        
        # Calculate time estimates
        elapsed = time.time() - self.start_time
        if self.current > 0 and self.total > self.current:
            eta = elapsed * (self.total - self.current) / self.current
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"
        
        # Clear line and write progress
        sys.stdout.write(f"\r{Colors.CYAN}{self.description}{Colors.RESET} ")
        sys.stdout.write(f"[{Colors.GREEN}{bar}{Colors.RESET}] ")
        sys.stdout.write(f"{percentage:.1f}% ({self.current}/{self.total}) {eta_str}")
        sys.stdout.flush()
        
        if self.current >= self.total:
            print()  # New line when complete

class EnhancedCLI:
    """Enhanced CLI interface for FionaSparx"""
    
    def __init__(self, enable_colors: bool = True):
        """Initialize enhanced CLI"""
        self.enable_colors = enable_colors and self._supports_color()
        self.start_time = time.time()
        
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        import os
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and os.getenv('TERM') != 'dumb'
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if self.enable_colors:
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def print_header(self, title: str):
        """Print section header"""
        border = "=" * 60
        print()
        print(self._colorize(border, Colors.CYAN))
        print(self._colorize(f" {title}", Colors.BOLD + Colors.CYAN))
        print(self._colorize(border, Colors.CYAN))
        print()
    
    def print_info(self, message: str, prefix: str = "ℹ️"):
        """Print info message"""
        print(f"{prefix} {self._colorize(message, Colors.BLUE)}")
    
    def print_success(self, message: str, prefix: str = "✅"):
        """Print success message"""
        print(f"{prefix} {self._colorize(message, Colors.GREEN)}")
    
    def print_warning(self, message: str, prefix: str = "⚠️"):
        """Print warning message"""
        print(f"{prefix} {self._colorize(message, Colors.YELLOW)}")
    
    def print_error(self, message: str, prefix: str = "❌"):
        """Print error message"""
        print(f"{prefix} {self._colorize(message, Colors.RED)}")
    
    def print_step(self, step_num: int, total_steps: int, description: str):
        """Print step progress"""
        step_info = f"[{step_num}/{total_steps}]"
        print(f"{self._colorize(step_info, Colors.MAGENTA)} {description}")
    
    def create_progress_bar(self, total: int, description: str = "") -> ProgressBar:
        """Create a progress bar"""
        return ProgressBar(total, description)
    
    def print_table(self, headers: List[str], rows: List[List[str]], title: str = ""):
        """Print formatted table"""
        if title:
            print(f"\n{self._colorize(title, Colors.BOLD)}")
        
        if not rows:
            print(self._colorize("No data to display", Colors.DIM))
            return
        
        # Calculate column widths
        widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Print header
        header_row = " | ".join(header.ljust(widths[i]) for i, header in enumerate(headers))
        print(self._colorize(header_row, Colors.BOLD))
        print(self._colorize("-" * len(header_row), Colors.DIM))
        
        # Print rows
        for row in rows:
            row_str = " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            print(row_str)
    
    def print_json(self, data: Dict[str, Any], title: str = ""):
        """Print formatted JSON"""
        if title:
            print(f"\n{self._colorize(title, Colors.BOLD)}")
        
        try:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            print(self._colorize(json_str, Colors.CYAN))
        except Exception as e:
            self.print_error(f"Error formatting JSON: {e}")
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask for user confirmation"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{message} ({default_str}): ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
    
    def select_option(self, options: List[str], message: str = "Select option") -> int:
        """Select from multiple options"""
        print(f"\n{message}:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = input(f"\nEnter choice (1-{len(options)}): ").strip()
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return index
                else:
                    self.print_error(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return -1
    
    def print_system_info(self, system_info: Dict[str, Any]):
        """Print system information"""
        self.print_header("System Information")
        
        for section, data in system_info.items():
            print(f"\n{self._colorize(section.replace('_', ' ').title(), Colors.BOLD)}")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {self._colorize(str(value), Colors.GREEN)}")
            else:
                print(f"  {self._colorize(str(data), Colors.GREEN)}")
    
    def print_health_status(self, health_status: Dict[str, Any]):
        """Print health status"""
        self.print_header("System Health Status")
        
        status = health_status.get("status", "unknown")
        status_color = {
            "healthy": Colors.GREEN,
            "warning": Colors.YELLOW,
            "critical": Colors.RED,
            "unknown": Colors.DIM
        }.get(status, Colors.DIM)
        
        print(f"Overall Status: {self._colorize(status.upper(), status_color)}")
        
        if "message" in health_status:
            print(f"Message: {health_status['message']}")
        
        if "summary" in health_status:
            summary = health_status["summary"]
            print(f"\nTotal Checks: {summary.get('total_checks', 0)}")
            
            if "status_counts" in summary:
                for status_type, count in summary["status_counts"].items():
                    if count > 0:
                        color = {
                            "healthy": Colors.GREEN,
                            "warning": Colors.YELLOW,
                            "critical": Colors.RED,
                            "unknown": Colors.DIM
                        }.get(status_type, Colors.DIM)
                        print(f"  {status_type.title()}: {self._colorize(str(count), color)}")
        
        if "checks" in health_status:
            print(f"\n{self._colorize('Individual Checks:', Colors.BOLD)}")
            for name, check_result in health_status["checks"].items():
                status_icon = {
                    "healthy": "✅",
                    "warning": "⚠️",
                    "critical": "🚨",
                    "unknown": "❓"
                }.get(check_result.get("status", "unknown"), "❓")
                
                print(f"  {status_icon} {name}: {check_result.get('message', 'No message')}")
    
    def print_performance_summary(self, performance_data: Dict[str, Any]):
        """Print performance summary"""
        self.print_header("Performance Summary")
        
        if "system_health" in performance_data:
            system = performance_data["system_health"]
            print(f"{self._colorize('System Resources:', Colors.BOLD)}")
            cpu_usage = system.get("cpu_usage", 0)
            memory_usage = system.get("memory_usage", 0)
            disk_usage = system.get("disk_usage", 0)
            print(f"  CPU Usage: {self._colorize(f'{cpu_usage:.1f}%', Colors.CYAN)}")
            print(f"  Memory Usage: {self._colorize(f'{memory_usage:.1f}%', Colors.CYAN)}")
            print(f"  Disk Usage: {self._colorize(f'{disk_usage:.1f}%', Colors.CYAN)}")
            
            gpu_memory_usage = system.get("gpu_memory_usage")
            if gpu_memory_usage is not None:
                print(f"  GPU Memory: {self._colorize(f'{gpu_memory_usage:.1f}%', Colors.CYAN)}")
        
        if "ai_operations" in performance_data:
            ai_ops = performance_data["ai_operations"]
            print(f"\n{self._colorize('AI Operations:', Colors.BOLD)}")
            total_ops = ai_ops.get('total_operations', 0)
            success_rate = ai_ops.get("success_rate", 0)
            avg_time = ai_ops.get("average_execution_time_ms", 0)
            print(f"  Total Operations: {self._colorize(str(total_ops), Colors.GREEN)}")
            print(f"  Success Rate: {self._colorize(f'{success_rate:.1f}%', Colors.GREEN)}")
            print(f"  Avg Execution Time: {self._colorize(f'{avg_time:.1f}ms', Colors.BLUE)}")
            
            if "operations_by_type" in ai_ops:
                print(f"\n  Operations by Type:")
                for op_type, count in ai_ops["operations_by_type"].items():
                    print(f"    {op_type}: {self._colorize(str(count), Colors.CYAN)}")
    
    def print_execution_summary(self, start_time: float, operations: List[str], success: bool = True):
        """Print execution summary"""
        execution_time = time.time() - start_time
        
        print(f"\n{self._colorize('Execution Summary', Colors.BOLD)}")
        print(f"{'─' * 50}")
        
        status_icon = "✅" if success else "❌"
        status_text = "COMPLETED" if success else "FAILED"
        status_color = Colors.GREEN if success else Colors.RED
        
        print(f"Status: {status_icon} {self._colorize(status_text, status_color)}")
        print(f"Execution Time: {self._colorize(f'{execution_time:.2f}s', Colors.BLUE)}")
        print(f"Operations Performed: {self._colorize(str(len(operations)), Colors.CYAN)}")
        
        if operations:
            print(f"\nOperations:")
            for i, operation in enumerate(operations, 1):
                print(f"  {i}. {operation}")
    
    def show_operation_progress(self, operation_name: str, total_steps: int, step_function: Callable):
        """Show progress for a multi-step operation"""
        self.print_header(f"Executing: {operation_name}")
        
        progress_bar = self.create_progress_bar(total_steps, "Progress")
        operations_performed = []
        
        start_time = time.time()
        success = True
        
        try:
            for step, step_desc in step_function():
                progress_bar.set_description(step_desc)
                progress_bar.update(1)
                operations_performed.append(step_desc)
                time.sleep(0.1)  # Small delay for visual effect
                
        except Exception as e:
            success = False
            self.print_error(f"Operation failed: {e}")
        
        self.print_execution_summary(start_time, operations_performed, success)
        return success
    
    def print_banner(self):
        """Print application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    FionaSparx AI Content Creator               ║
║                      Enterprise Edition 2.0                   ║
║              Advanced AI Content Generation System             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(self._colorize(banner, Colors.BRIGHT_CYAN))
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def print_command_help(self, commands: Dict[str, str]):
        """Print command help"""
        self.print_header("Available Commands")
        
        for command, description in commands.items():
            print(f"  {self._colorize(command.ljust(15), Colors.GREEN)} {description}")
        
        print(f"\nUsage: python main.py {self._colorize('<command>', Colors.YELLOW)}")
    
    def wait_for_key(self, message: str = "Press Enter to continue..."):
        """Wait for user input"""
        try:
            input(f"\n{message}")
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            sys.exit(0)