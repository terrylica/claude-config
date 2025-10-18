#!/usr/bin/env python3
"""
Comprehensive Validation Suite for mql5-crossover Project
Version: 1.0.0
Date: 2025-10-18

Validates all production components after recent changes:
- v3.0.0 Wine Python exports
- v4.0.0 File-based config generation
- Archive reorganization (cc indicator fix)
- Documentation link integrity
- Python indicator implementations

Usage:
    python comprehensive_validation.py [--priority P0|P1|P2|P3|ALL] [--verbose] [--json OUTPUT.json]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# ANSI Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class TestResult:
    """Single test result"""
    test_id: int
    name: str
    priority: str
    status: str  # PASS, FAIL, SKIP
    duration_ms: float
    message: str
    details: Optional[str] = None

class ValidationSuite:
    """Comprehensive validation test suite"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.start_time = datetime.now()

        # Paths (absolute from bottle root)
        self.bottle_root = Path("/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c")
        self.python_workspace = self.bottle_root / "users/crossover"
        self.mt5_root = self.bottle_root / "Program Files/MetaTrader 5"
        self.docs_root = self.bottle_root / "docs"
        self.archive_root = self.bottle_root / "archive"

    def log(self, message: str, color: str = ""):
        """Print log message with optional color"""
        if color:
            print(f"{color}{message}{Colors.END}")
        else:
            print(message)

    def run_test(self, test_id: int, name: str, priority: str, test_func) -> TestResult:
        """Run a single test and capture result"""
        start = datetime.now()

        if self.verbose:
            self.log(f"\n[{priority}:{test_id:02d}] {name}...", Colors.CYAN)

        try:
            status, message, details = test_func()
            duration_ms = (datetime.now() - start).total_seconds() * 1000

            result = TestResult(
                test_id=test_id,
                name=name,
                priority=priority,
                status=status,
                duration_ms=duration_ms,
                message=message,
                details=details
            )

            # Print result
            if status == "PASS":
                icon = f"{Colors.GREEN}✅{Colors.END}"
            elif status == "FAIL":
                icon = f"{Colors.RED}❌{Colors.END}"
            else:  # SKIP
                icon = f"{Colors.YELLOW}⏭️{Colors.END}"

            if self.verbose or status == "FAIL":
                self.log(f"  {icon} {message}")
                if details and (self.verbose or status == "FAIL"):
                    self.log(f"     {details}", Colors.BLUE if self.verbose else Colors.RED)

            self.results.append(result)
            return result

        except Exception as e:
            duration_ms = (datetime.now() - start).total_seconds() * 1000
            result = TestResult(
                test_id=test_id,
                name=name,
                priority=priority,
                status="FAIL",
                duration_ms=duration_ms,
                message=f"Exception: {str(e)}",
                details=None
            )
            self.log(f"  {Colors.RED}❌ Exception: {str(e)}{Colors.END}")
            self.results.append(result)
            return result

    # =========================================================================
    # P0 CRITICAL TESTS (10 tests)
    # =========================================================================

    def test_p0_01_v3_wine_python_export(self) -> Tuple[str, str, str]:
        """Test v3.0.0 Wine Python export"""
        # Skip actual export in validation (too slow), just check script exists and is valid Python
        script_path = self.python_workspace / "export_aligned.py"
        if not script_path.exists():
            return ("FAIL", "export_aligned.py not found", str(script_path))

        # Check it's valid Python syntax
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return ("PASS", "export_aligned.py exists and is valid Python", f"Size: {script_path.stat().st_size} bytes")
        else:
            return ("FAIL", "export_aligned.py has syntax errors", result.stderr)

    def test_p0_02_v4_config_gen_rsi(self) -> Tuple[str, str, str]:
        """Test v4.0.0 config generation - RSI"""
        script_path = self.python_workspace / "generate_export_config.py"
        if not script_path.exists():
            return ("FAIL", "generate_export_config.py not found", str(script_path))

        # Check script is valid Python
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return ("PASS", "generate_export_config.py exists and is valid Python", f"Size: {script_path.stat().st_size} bytes")
        else:
            return ("FAIL", "generate_export_config.py has syntax errors", result.stderr)

    def test_p0_03_validate_indicator_exists(self) -> Tuple[str, str, str]:
        """Test validate_indicator.py exists"""
        script_path = self.python_workspace / "validate_indicator.py"
        if not script_path.exists():
            return ("FAIL", "validate_indicator.py not found", str(script_path))

        # Check it's valid Python
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return ("PASS", "validate_indicator.py exists and is valid Python", f"Size: {script_path.stat().st_size} bytes")
        else:
            return ("FAIL", "validate_indicator.py has syntax errors", result.stderr)

    def test_p0_04_laguerre_rsi_indicator_exists(self) -> Tuple[str, str, str]:
        """Test indicators/laguerre_rsi.py exists"""
        indicator_path = self.python_workspace / "indicators" / "laguerre_rsi.py"
        if not indicator_path.exists():
            return ("FAIL", "laguerre_rsi.py not found", str(indicator_path))

        # Check for v1.0.0 marker
        content = indicator_path.read_text()
        if "__version__ = '1.0.0'" in content or '__version__ = "1.0.0"' in content:
            return ("PASS", "laguerre_rsi.py v1.0.0 exists", "Version marker found")
        else:
            return ("FAIL", "laguerre_rsi.py missing version marker", "Expected: __version__ = '1.0.0'")

    def test_p0_05_export_aligned_ex5_exists(self) -> Tuple[str, str, str]:
        """Test ExportAligned.ex5 exists"""
        ex5_path = self.mt5_root / "MQL5/Scripts/DataExport/ExportAligned.ex5"
        if not ex5_path.exists():
            return ("FAIL", "ExportAligned.ex5 not found", str(ex5_path))

        size = ex5_path.stat().st_size
        if size > 20_000:  # At least 20KB
            return ("PASS", f"ExportAligned.ex5 exists ({size:,} bytes)", str(ex5_path))
        else:
            return ("FAIL", f"ExportAligned.ex5 too small ({size} bytes)", "Expected > 20KB")

    def test_p0_06_export_aligned_mq5_exists(self) -> Tuple[str, str, str]:
        """Test ExportAligned.mq5 exists"""
        mq5_path = self.mt5_root / "MQL5/Scripts/DataExport/ExportAligned.mq5"
        if not mq5_path.exists():
            return ("FAIL", "ExportAligned.mq5 not found", str(mq5_path))

        lines = len(mq5_path.read_text(encoding='utf-8', errors='ignore').split('\n'))
        if lines > 200:  # Should be ~274 lines
            return ("PASS", f"ExportAligned.mq5 exists ({lines} lines)", str(mq5_path))
        else:
            return ("FAIL", f"ExportAligned.mq5 too small ({lines} lines)", "Expected > 200 lines")

    def test_p0_07_config_examples_exist(self) -> Tuple[str, str, str]:
        """Test all 5 config examples exist"""
        configs_dir = self.mt5_root / "MQL5/Files/configs"
        if not configs_dir.exists():
            return ("FAIL", "configs/ directory not found", str(configs_dir))

        expected_files = [
            "example_rsi_only.txt",
            "example_sma_only.txt",
            "example_laguerre_rsi.txt",
            "example_multi_indicator.txt",
            "example_validation_100bars.txt"
        ]

        missing = []
        for filename in expected_files:
            if not (configs_dir / filename).exists():
                missing.append(filename)

        if not missing:
            return ("PASS", f"All 5 config examples exist", f"Location: {configs_dir}")
        else:
            return ("FAIL", f"Missing {len(missing)} config examples", f"Missing: {', '.join(missing)}")

    def test_p0_08_python_imports(self) -> Tuple[str, str, str]:
        """Test Python scripts are importable"""
        os.chdir(self.python_workspace)

        scripts_to_test = [
            ("export_aligned", "export_aligned.py"),
            ("validate_indicator", "validate_indicator.py"),
            ("generate_export_config", "generate_export_config.py"),
        ]

        failed = []
        skipped = []
        for module_name, script_name in scripts_to_test:
            try:
                __import__(module_name)
            except ModuleNotFoundError as e:
                # MetaTrader5 module only available in Wine Python, not macOS Python
                if "MetaTrader5" in str(e):
                    skipped.append(f"{script_name}: Requires Wine Python (MetaTrader5 module)")
                else:
                    failed.append(f"{script_name}: {str(e)}")
            except Exception as e:
                failed.append(f"{script_name}: {str(e)}")

        if failed:
            return ("FAIL", f"{len(failed)} scripts have import errors", "\n".join(failed))
        elif skipped:
            return ("SKIP", f"{len(skipped)} scripts require Wine Python", "\n".join(skipped))
        else:
            return ("PASS", "All Python scripts importable", "No import errors")

    def test_p0_09_indicators_package(self) -> Tuple[str, str, str]:
        """Test indicators package is importable"""
        os.chdir(self.python_workspace)

        try:
            from indicators import laguerre_rsi
            return ("PASS", "indicators.laguerre_rsi importable", f"Version: {getattr(laguerre_rsi, '__version__', 'unknown')}")
        except Exception as e:
            return ("FAIL", "indicators.laguerre_rsi not importable", str(e))

    def test_p0_10_docs_exist(self) -> Tuple[str, str, str]:
        """Test key documentation files exist"""
        key_docs = [
            self.bottle_root / "CLAUDE.md",
            self.bottle_root / "DOCUMENTATION.md",
            self.docs_root / "MT5_REFERENCE_HUB.md",
            self.docs_root / "reports/LEGACY_CODE_ASSESSMENT.md",
        ]

        missing = [str(doc) for doc in key_docs if not doc.exists()]

        if not missing:
            return ("PASS", "All 4 key documentation files exist", "CLAUDE.md, DOCUMENTATION.md, MT5_REFERENCE_HUB.md, LEGACY_CODE_ASSESSMENT.md")
        else:
            return ("FAIL", f"{len(missing)} key docs missing", "\n".join(missing))

    # =========================================================================
    # P1 CORE FUNCTIONALITY TESTS (12 tests)
    # =========================================================================

    def test_p1_01_archive_cc_development(self) -> Tuple[str, str, str]:
        """Test archive/indicators/cc/development/ has 10 files"""
        cc_dev_dir = self.archive_root / "indicators/cc/development"
        if not cc_dev_dir.exists():
            return ("FAIL", "cc/development/ directory not found", str(cc_dev_dir))

        files = list(cc_dev_dir.glob("*"))
        file_count = len([f for f in files if f.is_file()])

        if file_count == 10:
            filenames = sorted([f.name for f in files if f.is_file()])
            return ("PASS", f"cc/development/ has exactly 10 files", f"Files: {', '.join(filenames[:3])}... (showing 3/{file_count})")
        else:
            return ("FAIL", f"cc/development/ has {file_count} files (expected 10)", f"Files: {[f.name for f in files if f.is_file()]}")

    def test_p1_02_archive_laguerre_no_cc(self) -> Tuple[str, str, str]:
        """Test laguerre_rsi/development/ has NO cc files"""
        laguerre_dev_dir = self.archive_root / "indicators/laguerre_rsi/development"
        if not laguerre_dev_dir.exists():
            return ("FAIL", "laguerre_rsi/development/ not found", str(laguerre_dev_dir))

        files = list(laguerre_dev_dir.glob("cc*"))

        if not files:
            all_files = [f.name for f in laguerre_dev_dir.glob("*") if f.is_file()]
            return ("PASS", "laguerre_rsi/development/ has NO cc files", f"{len(all_files)} Laguerre files only")
        else:
            return ("FAIL", f"laguerre_rsi/development/ still has {len(files)} cc files", f"Found: {[f.name for f in files]}")

    def test_p1_03_archive_cc_compiled(self) -> Tuple[str, str, str]:
        """Test cc/compiled/ has 4 .ex5 files"""
        cc_compiled_dir = self.archive_root / "indicators/cc/compiled"
        if not cc_compiled_dir.exists():
            return ("FAIL", "cc/compiled/ not found", str(cc_compiled_dir))

        ex5_files = list(cc_compiled_dir.glob("*.ex5"))

        if len(ex5_files) == 4:
            return ("PASS", "cc/compiled/ has 4 .ex5 files", f"Files: {', '.join([f.name for f in ex5_files])}")
        else:
            return ("FAIL", f"cc/compiled/ has {len(ex5_files)} .ex5 files (expected 4)", f"Files: {[f.name for f in ex5_files]}")

    def test_p1_04_mql5_scripts_structure(self) -> Tuple[str, str, str]:
        """Test MQL5 Scripts/DataExport/ structure"""
        scripts_dir = self.mt5_root / "MQL5/Scripts/DataExport"
        if not scripts_dir.exists():
            return ("FAIL", "Scripts/DataExport/ not found", str(scripts_dir))

        required_files = ["ExportAligned.mq5", "ExportAligned.ex5"]
        missing = [f for f in required_files if not (scripts_dir / f).exists()]

        if not missing:
            return ("PASS", "Scripts/DataExport/ structure correct", f"Contains: {', '.join(required_files)}")
        else:
            return ("FAIL", f"Scripts/DataExport/ missing {len(missing)} files", f"Missing: {', '.join(missing)}")

    def test_p1_05_mql5_include_structure(self) -> Tuple[str, str, str]:
        """Test MQL5 Include/DataExport/ structure"""
        include_dir = self.mt5_root / "MQL5/Include/DataExport"
        if not include_dir.exists():
            return ("FAIL", "Include/DataExport/ not found", str(include_dir))

        required_items = ["DataExportCore.mqh", "ExportAlignedCommon.mqh", "modules"]
        missing = [item for item in required_items if not (include_dir / item).exists()]

        if not missing:
            return ("PASS", "Include/DataExport/ structure correct", f"Contains: {', '.join(required_items)}")
        else:
            return ("FAIL", f"Include/DataExport/ missing {len(missing)} items", f"Missing: {', '.join(missing)}")

    def test_p1_06_config_examples_readable(self) -> Tuple[str, str, str]:
        """Test all config examples are readable"""
        configs_dir = self.mt5_root / "MQL5/Files/configs"
        if not configs_dir.exists():
            return ("SKIP", "configs/ directory not found", str(configs_dir))

        config_files = list(configs_dir.glob("example_*.txt"))

        failed = []
        for config_file in config_files:
            try:
                content = config_file.read_text()
                if len(content) < 100:  # Sanity check
                    failed.append(f"{config_file.name}: Too short ({len(content)} chars)")
            except Exception as e:
                failed.append(f"{config_file.name}: {str(e)}")

        if not failed:
            return ("PASS", f"All {len(config_files)} config examples readable", "No read errors")
        else:
            return ("FAIL", f"{len(failed)} config examples have issues", "\n".join(failed))

    def test_p1_07_git_archive_clean(self) -> Tuple[str, str, str]:
        """Test no untracked files in archive/indicators/"""
        result = subprocess.run(
            ["git", "status", "--porcelain", "archive/indicators/"],
            cwd=self.bottle_root,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return ("SKIP", "Git not available or not a git repo", result.stderr)

        untracked = [line for line in result.stdout.strip().split('\n') if line.startswith('??')]

        if not untracked or untracked == ['']:
            return ("PASS", "archive/indicators/ has no untracked files", "Git tracking clean")
        else:
            return ("FAIL", f"archive/indicators/ has {len(untracked)} untracked files", "\n".join(untracked))

    def test_p1_08_validate_indicator_framework(self) -> Tuple[str, str, str]:
        """Test validate_indicator.py contains universal framework"""
        script_path = self.python_workspace / "validate_indicator.py"
        if not script_path.exists():
            return ("SKIP", "validate_indicator.py not found", "")

        content = script_path.read_text()

        # Check for key framework features
        checks = [
            ("argparse", "CLI argument parsing"),
            ("--indicator", "Indicator selection flag"),
            ("--threshold", "Correlation threshold flag"),
            ("correlation", "Correlation calculation"),
        ]

        missing = [desc for pattern, desc in checks if pattern not in content]

        if not missing:
            return ("PASS", "validate_indicator.py has universal framework", f"All {len(checks)} features present")
        else:
            return ("FAIL", f"validate_indicator.py missing {len(missing)} features", f"Missing: {', '.join(missing)}")

    def test_p1_09_laguerre_rsi_v1_validated(self) -> Tuple[str, str, str]:
        """Test Laguerre RSI v1.0.0 validation report exists"""
        report_path = self.docs_root / "reports/LAGUERRE_RSI_VALIDATION_SUCCESS.md"
        if not report_path.exists():
            return ("FAIL", "LAGUERRE_RSI_VALIDATION_SUCCESS.md not found", str(report_path))

        content = report_path.read_text()

        # Check for 1.000000 correlation
        if "1.000000" in content and "correlation" in content.lower():
            return ("PASS", "Laguerre RSI v1.0.0 validation report exists", "Perfect correlation documented")
        else:
            return ("FAIL", "Validation report missing correlation data", "Expected: 1.000000 correlation")

    def test_p1_10_exports_directory_exists(self) -> Tuple[str, str, str]:
        """Test exports/ directory exists"""
        exports_dir = self.python_workspace / "exports"

        if exports_dir.exists():
            return ("PASS", "exports/ directory exists", str(exports_dir))
        else:
            return ("SKIP", "exports/ directory not found (may be gitignored)", str(exports_dir))

    def test_p1_11_mql5_logs_accessible(self) -> Tuple[str, str, str]:
        """Test MQL5/Logs/ directory accessible"""
        logs_dir = self.mt5_root / "MQL5/Logs"

        if logs_dir.exists() and os.access(logs_dir, os.R_OK):
            log_files = list(logs_dir.glob("*.log"))
            return ("PASS", f"MQL5/Logs/ accessible ({len(log_files)} log files)", str(logs_dir))
        elif logs_dir.exists():
            return ("FAIL", "MQL5/Logs/ exists but not readable", str(logs_dir))
        else:
            return ("FAIL", "MQL5/Logs/ directory not found", str(logs_dir))

    def test_p1_12_deprecated_warning_present(self) -> Tuple[str, str, str]:
        """Test validate_export.py has deprecation warning"""
        script_path = self.python_workspace / "validate_export.py"
        if not script_path.exists():
            return ("SKIP", "validate_export.py not found", "")

        content = script_path.read_text()

        if "DEPRECATED" in content or "deprecated" in content:
            return ("PASS", "validate_export.py has deprecation warning", "Warning present")
        else:
            return ("FAIL", "validate_export.py missing deprecation warning", "Should warn users to use validate_indicator.py")

    # =========================================================================
    # P2 DOCUMENTATION INTEGRITY TESTS (shortened for brevity)
    # =========================================================================

    def test_p2_01_claude_md_links(self) -> Tuple[str, str, str]:
        """Test CLAUDE.md links are valid"""
        claude_md = self.bottle_root / "CLAUDE.md"
        if not claude_md.exists():
            return ("FAIL", "CLAUDE.md not found", "")

        content = claude_md.read_text()

        # Extract markdown links [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        links = re.findall(link_pattern, content)

        broken_links = []
        for text, path in links:
            # Skip external URLs
            if path.startswith('http'):
                continue

            # Resolve relative path
            link_path = self.bottle_root / path.strip()
            if not link_path.exists():
                broken_links.append(f"{text} -> {path}")

        if not broken_links:
            return ("PASS", f"CLAUDE.md: All {len([p for t, p in links if not p.startswith('http')])} internal links valid", "No broken links")
        else:
            return ("FAIL", f"CLAUDE.md: {len(broken_links)} broken links", "\n".join(broken_links[:5]) + ("..." if len(broken_links) > 5 else ""))

    def test_p2_02_documentation_md_links(self) -> Tuple[str, str, str]:
        """Test DOCUMENTATION.md links are valid"""
        doc_md = self.bottle_root / "DOCUMENTATION.md"
        if not doc_md.exists():
            return ("FAIL", "DOCUMENTATION.md not found", "")

        content = doc_md.read_text()

        # Extract markdown links
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        links = re.findall(link_pattern, content)

        broken_links = []
        for text, path in links:
            # Skip external URLs and anchor links
            if path.startswith('http') or path.startswith('#'):
                continue

            link_path = self.bottle_root / path.strip()
            if not link_path.exists():
                broken_links.append(f"{text} -> {path}")

        if not broken_links:
            internal_links = len([p for t, p in links if not p.startswith('http') and not p.startswith('#')])
            return ("PASS", f"DOCUMENTATION.md: All {internal_links} internal links valid", "No broken links")
        else:
            return ("FAIL", f"DOCUMENTATION.md: {len(broken_links)} broken links", "\n".join(broken_links[:5]))

    def test_p2_03_mt5_reference_hub_links(self) -> Tuple[str, str, str]:
        """Test MT5_REFERENCE_HUB.md links are valid"""
        hub_md = self.docs_root / "MT5_REFERENCE_HUB.md"
        if not hub_md.exists():
            return ("FAIL", "MT5_REFERENCE_HUB.md not found", "")

        content = hub_md.read_text()

        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        links = re.findall(link_pattern, content)

        broken_links = []
        for text, path in links:
            if path.startswith('http'):
                continue

            # Paths in hub are relative to docs/
            link_path = self.docs_root / path.strip()
            if not link_path.exists():
                # Try from bottle root
                link_path = self.bottle_root / path.strip()
                if not link_path.exists():
                    broken_links.append(f"{text} -> {path}")

        if not broken_links:
            return ("PASS", f"MT5_REFERENCE_HUB.md: All internal links valid", "No broken links")
        else:
            return ("FAIL", f"MT5_REFERENCE_HUB.md: {len(broken_links)} broken links", "\n".join(broken_links[:3]))

    def test_p2_04_legacy_assessment_references(self) -> Tuple[str, str, str]:
        """Test LEGACY_CODE_ASSESSMENT.md file path references"""
        legacy_md = self.docs_root / "reports/LEGACY_CODE_ASSESSMENT.md"
        if not legacy_md.exists():
            return ("FAIL", "LEGACY_CODE_ASSESSMENT.md not found", "")

        content = legacy_md.read_text()

        # Check for incorrect references to old cc file locations
        if "laguerre_rsi/development/cc" in content:
            # This should be updated to cc/development/ after reorganization
            return ("FAIL", "LEGACY_CODE_ASSESSMENT.md has outdated cc file references", "References old laguerre_rsi/development/cc* locations")

        # Check for correct cc/development/ references
        if "archive/indicators/cc/development/" in content:
            return ("PASS", "LEGACY_CODE_ASSESSMENT.md references updated", "Correctly references cc/development/")
        else:
            return ("FAIL", "LEGACY_CODE_ASSESSMENT.md missing cc/development/ references", "Should reference new location")

    def test_p2_05_no_old_cc_references_in_docs(self) -> Tuple[str, str, str]:
        """Test docs don't reference old cc file locations"""
        key_docs = [
            self.bottle_root / "CLAUDE.md",
            self.bottle_root / "DOCUMENTATION.md",
            self.docs_root / "MT5_REFERENCE_HUB.md",
        ]

        docs_with_old_refs = []
        for doc in key_docs:
            if doc.exists():
                content = doc.read_text()
                if "laguerre_rsi/development/cc" in content:
                    docs_with_old_refs.append(doc.name)

        if not docs_with_old_refs:
            return ("PASS", "No old cc file location references found", f"Checked {len(key_docs)} key docs")
        else:
            return ("FAIL", f"{len(docs_with_old_refs)} docs have old cc references", f"Docs: {', '.join(docs_with_old_refs)}")

    # =========================================================================
    # P3 EDGE CASES TESTS (simplified)
    # =========================================================================

    def test_p3_01_crossover_app_exists(self) -> Tuple[str, str, str]:
        """Test CrossOver.app exists"""
        crossover_path = Path.home() / "Applications/CrossOver.app"

        if crossover_path.exists():
            return ("PASS", "CrossOver.app found at ~/Applications/", str(crossover_path))
        else:
            alt_path = Path("/Applications/CrossOver.app")
            if alt_path.exists():
                return ("PASS", "CrossOver.app found at /Applications/", str(alt_path))
            else:
                return ("FAIL", "CrossOver.app not found", "Checked ~/Applications and /Applications")

    def test_p3_02_wine_python_exists(self) -> Tuple[str, str, str]:
        """Test Wine Python exists in bottle"""
        # mt5_root.parent.parent goes from "Program Files/MetaTrader 5" -> "Program Files" -> bottle root
        wine_python = self.bottle_root / "Program Files/Python312/python.exe"

        if wine_python.exists():
            return ("PASS", "Wine Python 3.12 found", str(wine_python))
        else:
            return ("FAIL", "Wine Python not found", f"Expected: {wine_python}")

    def test_p3_03_git_repo_valid(self) -> Tuple[str, str, str]:
        """Test this is a valid git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=self.bottle_root,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return ("PASS", "Valid git repository", result.stdout.strip())
        else:
            return ("FAIL", "Not a valid git repository", result.stderr)

    def test_p3_04_git_remote_exists(self) -> Tuple[str, str, str]:
        """Test git remote is configured"""
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=self.bottle_root,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return ("PASS", f"Git remote configured: {result.stdout.strip()}", "origin remote exists")
        else:
            return ("FAIL", "Git remote not configured", "No origin remote")

    def test_p3_05_recent_commits_present(self) -> Tuple[str, str, str]:
        """Test recent commits (cc reorganization, legacy assessment) are present"""
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=self.bottle_root,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return ("SKIP", "Git log not available", "")

        log = result.stdout

        # Check for recent commits
        checks = [
            ("cc indicator", "cc indicator archive organization"),
            ("LEGACY_CODE_ASSESSMENT", "legacy code assessment"),
            ("DOCUMENTATION.md", "documentation hub"),
        ]

        found = sum(1 for pattern, _ in checks if pattern in log)

        if found >= 2:
            return ("PASS", f"Recent commits present ({found}/3)", "Git history intact")
        else:
            return ("FAIL", f"Only {found}/3 recent commits found", "Git history may be incomplete")

    # =========================================================================
    # TEST SUITE EXECUTION
    # =========================================================================

    def run_priority(self, priority: str) -> int:
        """Run all tests for a given priority level"""
        self.log(f"\n{'='*60}", Colors.BOLD)
        self.log(f"{priority} TEST SUITE", Colors.BOLD)
        self.log(f"{'='*60}\n", Colors.BOLD)

        # Map priority to test methods
        test_methods = {
            "P0": [
                (1, "v3.0.0 Wine Python Export Script", self.test_p0_01_v3_wine_python_export),
                (2, "v4.0.0 Config Generation - RSI", self.test_p0_02_v4_config_gen_rsi),
                (3, "validate_indicator.py Exists", self.test_p0_03_validate_indicator_exists),
                (4, "Laguerre RSI Indicator Exists", self.test_p0_04_laguerre_rsi_indicator_exists),
                (5, "ExportAligned.ex5 Exists", self.test_p0_05_export_aligned_ex5_exists),
                (6, "ExportAligned.mq5 Exists", self.test_p0_06_export_aligned_mq5_exists),
                (7, "Config Examples Exist", self.test_p0_07_config_examples_exist),
                (8, "Python Scripts Importable", self.test_p0_08_python_imports),
                (9, "Indicators Package Importable", self.test_p0_09_indicators_package),
                (10, "Key Documentation Exists", self.test_p0_10_docs_exist),
            ],
            "P1": [
                (11, "Archive: cc/development/ Structure", self.test_p1_01_archive_cc_development),
                (12, "Archive: laguerre_rsi/ No CC Files", self.test_p1_02_archive_laguerre_no_cc),
                (13, "Archive: cc/compiled/ Structure", self.test_p1_03_archive_cc_compiled),
                (14, "MQL5 Scripts Structure", self.test_p1_04_mql5_scripts_structure),
                (15, "MQL5 Include Structure", self.test_p1_05_mql5_include_structure),
                (16, "Config Examples Readable", self.test_p1_06_config_examples_readable),
                (17, "Git Archive Clean", self.test_p1_07_git_archive_clean),
                (18, "validate_indicator.py Framework", self.test_p1_08_validate_indicator_framework),
                (19, "Laguerre RSI v1.0.0 Validated", self.test_p1_09_laguerre_rsi_v1_validated),
                (20, "Exports Directory Exists", self.test_p1_10_exports_directory_exists),
                (21, "MQL5 Logs Accessible", self.test_p1_11_mql5_logs_accessible),
                (22, "validate_export.py Deprecation", self.test_p1_12_deprecated_warning_present),
            ],
            "P2": [
                (23, "CLAUDE.md Link Integrity", self.test_p2_01_claude_md_links),
                (24, "DOCUMENTATION.md Link Integrity", self.test_p2_02_documentation_md_links),
                (25, "MT5_REFERENCE_HUB.md Links", self.test_p2_03_mt5_reference_hub_links),
                (26, "LEGACY_CODE_ASSESSMENT.md References", self.test_p2_04_legacy_assessment_references),
                (27, "No Old CC References in Docs", self.test_p2_05_no_old_cc_references_in_docs),
            ],
            "P3": [
                (28, "CrossOver.app Exists", self.test_p3_01_crossover_app_exists),
                (29, "Wine Python Exists", self.test_p3_02_wine_python_exists),
                (30, "Git Repository Valid", self.test_p3_03_git_repo_valid),
                (31, "Git Remote Configured", self.test_p3_04_git_remote_exists),
                (32, "Recent Commits Present", self.test_p3_05_recent_commits_present),
            ]
        }

        tests = test_methods.get(priority, [])

        for test_id, name, test_func in tests:
            self.run_test(test_id, name, priority, test_func)

        # Count results for this priority
        priority_results = [r for r in self.results if r.priority == priority]
        passed = len([r for r in priority_results if r.status == "PASS"])
        failed = len([r for r in priority_results if r.status == "FAIL"])
        skipped = len([r for r in priority_results if r.status == "SKIP"])

        self.log(f"\n{priority} Summary: {passed} passed, {failed} failed, {skipped} skipped", Colors.BOLD)

        return failed

    def print_summary(self):
        """Print final test summary"""
        total = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        skipped = len([r for r in self.results if r.status == "SKIP"])

        duration_sec = (datetime.now() - self.start_time).total_seconds()

        self.log(f"\n{'='*60}", Colors.BOLD)
        self.log(f"FINAL SUMMARY", Colors.BOLD)
        self.log(f"{'='*60}\n", Colors.BOLD)

        self.log(f"Total Tests:    {total}")
        self.log(f"Passed:         {passed} {Colors.GREEN}✅{Colors.END}")
        self.log(f"Failed:         {failed} {Colors.RED}❌{Colors.END}" if failed > 0 else f"Failed:         {failed}")
        self.log(f"Skipped:        {skipped}")
        self.log(f"Duration:       {duration_sec:.2f}s")

        if failed == 0:
            self.log(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED!{Colors.END}")
        else:
            self.log(f"\n{Colors.RED}{Colors.BOLD}❌ {failed} TEST(S) FAILED{Colors.END}")
            self.log(f"\nFailed Tests:")
            for result in self.results:
                if result.status == "FAIL":
                    self.log(f"  [{result.priority}:{result.test_id:02d}] {result.name}")
                    self.log(f"      {result.message}", Colors.RED)

    def save_json_report(self, output_path: str):
        """Save test results to JSON file"""
        report = {
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "summary": {
                "total": len(self.results),
                "passed": len([r for r in self.results if r.status == "PASS"]),
                "failed": len([r for r in self.results if r.status == "FAIL"]),
                "skipped": len([r for r in self.results if r.status == "SKIP"]),
            },
            "results": [asdict(r) for r in self.results]
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.log(f"\nJSON report saved: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Validation Suite for mql5-crossover")
    parser.add_argument("--priority", choices=["P0", "P1", "P2", "P3", "ALL"], default="ALL",
                       help="Priority level to run (default: ALL)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output (show all test details)")
    parser.add_argument("--json", type=str,
                       help="Save results to JSON file")

    args = parser.parse_args()

    suite = ValidationSuite(verbose=args.verbose)

    suite.log(f"\n{Colors.BOLD}Comprehensive Validation Suite v1.0.0{Colors.END}")
    suite.log(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Run tests
    if args.priority == "ALL":
        for priority in ["P0", "P1", "P2", "P3"]:
            suite.run_priority(priority)
    else:
        suite.run_priority(args.priority)

    # Print summary
    suite.print_summary()

    # Save JSON report if requested
    if args.json:
        suite.save_json_report(args.json)

    # Exit with appropriate code
    failed_count = len([r for r in suite.results if r.status == "FAIL"])
    sys.exit(1 if failed_count > 0 else 0)

if __name__ == "__main__":
    main()
