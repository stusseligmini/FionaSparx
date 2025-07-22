"""
Improved CLI Module with Progress Bars

This module enhances the command-line experience with rich progress bars,
colorful output, and interactive elements for better user experience.

Key Features:
- Rich progress bars for long-running operations
- Colorful console output
- Spinners for indeterminate progress
- Tables for structured data display
- Interactive prompts and menus

Author: FionaSparx AI Content Creator
Version: 1.0.0
"""

import sys
import time
import shutil
from datetime import datetime
import threading
import logging
from enum import Enum

logger = logging.getLogger(__name__)

# ANSI color codes for colorful output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class ProgressStyle(Enum):
    """Stiler for fremdriftsindikatorer"""
    BAR = "bar"              # Standard fremdriftslinje
    SPINNER = "spinner"      # Roterende spinner for udefinert fremgang
    COUNTER = "counter"      # Enkel numerisk teller
    DETAILED = "detailed"    # Detaljert visning med flere indikatorer


class ProgressBar:
    """
    Avansert fremdriftsindikator for CLI med flere visningsalternativer
    """
    
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, total=100, description="Processing", style=ProgressStyle.BAR, 
                 width=None, color=Colors.BLUE, show_time=True, show_percent=True):
        self.total = total
        self.description = description
        self.style = style
        self.width = width or (shutil.get_terminal_size().columns - 30)
        self.color = color
        self.show_time = show_time
        self.show_percent = show_percent
        
        self.start_time = None
        self.current = 0
        self.is_running = False
        self.spinner_index = 0
        self.spinner_thread = None
        self._last_update_time = 0
        self._update_interval = 0.1  # Sekunder mellom oppdateringer
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()
    
    def start(self):
        """Start fremdriftsindikatoren"""
        self.start_time = time.time()
        self.is_running = True
        self.update(0)
        
        if self.style == ProgressStyle.SPINNER:
            self.spinner_thread = threading.Thread(target=self._run_spinner)
            self.spinner_thread.daemon = True
            self.spinner_thread.start()
    
    def update(self, current, description=None):
        """Oppdater fremdriftsindikator med ny verdi"""
        self.current = min(current, self.total)
        
        if description:
            self.description = description
            
        # Begrens frekvensen på oppdateringer for bedre ytelse
        current_time = time.time()
        if current_time - self._last_update_time < self._update_interval and current < self.total:
            return
            
        self._last_update_time = current_time
        
        if self.style == ProgressStyle.BAR:
            self._draw_bar()
        elif self.style == ProgressStyle.COUNTER:
            self._draw_counter()
        elif self.style == ProgressStyle.DETAILED:
            self._draw_detailed()
    
    def finish(self, success=True):
        """Avslutt fremdriftsindikatoren"""
        self.is_running = False
        if self.spinner_thread:
            self.spinner_thread.join(timeout=0.5)
        
        self.update(self.total)
        end_color = Colors.GREEN if success else Colors.RED
        symbol = "✓" if success else "✗"
        duration = time.time() - self.start_time
        
        print(f"\n{end_color}{symbol} {self.description} fullført på {duration:.2f}s{Colors.RESET}")
    
    def _draw_bar(self):
        """Tegn standard fremdriftslinje"""
        percent = self.current / self.total
        filled_width = int(self.width * percent)
        
        bar = "█" * filled_width + "░" * (self.width - filled_width)
        percent_str = f"{percent * 100:.1f}%" if self.show_percent else ""
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        time_str = f"{elapsed:.1f}s" if self.show_time else ""
        
        status = f"\r{self.color}{self.description}: {bar} {self.current}/{self.total} {percent_str} {time_str}{Colors.RESET}"
        sys.stdout.write(status)
        sys.stdout.flush()
    
    def _draw_counter(self):
        """Tegn enkel numerisk teller"""
        percent = self.current / self.total
        percent_str = f"{percent * 100:.1f}%" if self.show_percent else ""
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        time_str = f"{elapsed:.1f}s" if self.show_time else ""
        
        status = f"\r{self.color}{self.description}: {self.current}/{self.total} {percent_str} {time_str}{Colors.RESET}"
        sys.stdout.write(status)
        sys.stdout.flush()
    
    def _draw_detailed(self):
        """Tegn detaljert fremdriftsvisning"""
        percent = self.current / self.total
        filled_width = int(self.width * percent)
        
        bar = "█" * filled_width + "░" * (self.width - filled_width)
        percent_str = f"{percent * 100:.1f}%"
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # Estimer gjenværende tid
        if percent > 0:
            remaining = elapsed / percent - elapsed
            eta = datetime.now().timestamp() + remaining
            eta_str = f"ETA: {datetime.fromtimestamp(eta).strftime('%H:%M:%S')}"
        else:
            eta_str = "ETA: --:--:--"
        
        # Viser detaljert status med flere linjer
        status = (
            f"\r{self.color}{self.description}:{Colors.RESET}\n"
            f"{self.color}[{bar}] {percent_str}{Colors.RESET}\n"
            f"{self.color}Progress: {self.current}/{self.total} | Elapsed: {elapsed:.1f}s | {eta_str}{Colors.RESET}"
        )
        
        sys.stdout.write("\033[K")  # Fjern gjeldende linje
        sys.stdout.write("\033[3A") if self.current > 0 else None  # Flytt tilbake tre linjer hvis ikke første tegning
        sys.stdout.write(status)
        sys.stdout.flush()
    
    def _run_spinner(self):
        """Kjører spinner animasjon i egen tråd"""
        while self.is_running:
            if not self.is_running:
                break
                
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
            spinner = self.spinner_chars[self.spinner_index]
            
            elapsed = time.time() - self.start_time if self.start_time else 0
            time_str = f"{elapsed:.1f}s" if self.show_time else ""
            
            status = f"\r{self.color}{spinner} {self.description}... {time_str}{Colors.RESET}"
            sys.stdout.write(status)
            sys.stdout.flush()
            
            time.sleep(0.1)


class ConsoleUI:
    """
    Forbedret konsollgrensesnitt med farger og formatering
    """
    
    @staticmethod
    def print_header(text, color=Colors.BLUE):
        """Skriv ut formatert overskrift"""
        term_width = shutil.get_terminal_size().columns
        print(f"\n{color}{Colors.BOLD}{text.center(term_width)}{Colors.RESET}\n")
    
    @staticmethod
    def print_section(text, color=Colors.CYAN):
        """Skriv ut formatert seksjonoverskrift"""
        print(f"\n{color}{Colors.BOLD}=== {text} ==={Colors.RESET}")
    
    @staticmethod
    def print_success(text):
        """Skriv ut suksessmelding"""
        print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")
    
    @staticmethod
    def print_error(text):
        """Skriv ut feilmelding"""
        print(f"{Colors.RED}✗ {text}{Colors.RESET}")
    
    @staticmethod
    def print_warning(text):
        """Skriv ut advarsel"""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")
    
    @staticmethod
    def print_info(text):
        """Skriv ut informasjonsmelding"""
        print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")
    
    @staticmethod
    def print_table(headers, rows, color=Colors.BLUE):
        """Skriv ut formatert tabell"""
        # Beregn kolonnebredder
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Lag skillestrek
        separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
        
        # Skriv ut overskrift
        print(separator)
        header_row = "|" + "|".join([f" {h:{w}} " for h, w in zip(headers, col_widths)]) + "|"
        print(f"{color}{header_row}{Colors.RESET}")
        print(separator)
        
        # Skriv ut rader
        for row in rows:
            data_row = "|" + "|".join([f" {str(c):{w}} " for c, w in zip(row, col_widths)]) + "|"
            print(data_row)
        
        print(separator)
    
    @staticmethod
    def prompt(text, default=None, color=Colors.CYAN):
        """Be om brukerinndata med formatering"""
        default_text = f" [{default}]" if default is not None else ""
        user_input = input(f"{color}{text}{default_text}: {Colors.RESET}")
        return user_input if user_input else default
    
    @staticmethod
    def confirm(text, default=True):
        """Be om bekreftelse fra bruker"""
        y_n = "[Y/n]" if default else "[y/N]"
        user_input = input(f"{Colors.YELLOW}{text} {y_n}{Colors.RESET} ").lower()
        
        if user_input in ["y", "yes"]:
            return True
        elif user_input in ["n", "no"]:
            return False
        else:
            return default


# Eksempelfunksjon for demo
def demo():
    """Demonstrerer ulike CLI-funksjoner"""
    ConsoleUI.print_header("FionaSparx CLI Demo")
    
    ConsoleUI.print_section("Progress Bar Demo")
    with ProgressBar(total=100, description="Processing data") as pbar:
        for i in range(101):
            time.sleep(0.05)
            pbar.update(i)
    
    ConsoleUI.print_section("Spinner Demo")
    with ProgressBar(total=100, description="Loading data", style=ProgressStyle.SPINNER) as pbar:
        for i in range(101):
            time.sleep(0.05)
            pbar.update(i)
    
    ConsoleUI.print_section("Detailed Progress Demo")
    with ProgressBar(total=100, description="Analyzing content", style=ProgressStyle.DETAILED) as pbar:
        for i in range(101):
            time.sleep(0.05)
            pbar.update(i)
    
    ConsoleUI.print_section("Console UI Demo")
    ConsoleUI.print_success("Operation completed successfully")
    ConsoleUI.print_error("Something went wrong")
    ConsoleUI.print_warning("This might cause issues")
    ConsoleUI.print_info("Here's some useful information")
    
    # Demo tabell
    headers = ["Name", "Value", "Status"]
    rows = [
        ["Item 1", 42, "Active"],
        ["Item 2", 18, "Inactive"],
        ["Item 3", 73, "Pending"]
    ]
    ConsoleUI.print_table(headers, rows)
    
    # Demo brukerinteraksjon
    name = ConsoleUI.prompt("Enter your name", default="User")
    ConsoleUI.print_info(f"Hello, {name}!")
    
    if ConsoleUI.confirm("Would you like to continue?"):
        ConsoleUI.print_success("Continuing...")
    else:
        ConsoleUI.print_warning("Operation cancelled")


if __name__ == "__main__":
    demo()
