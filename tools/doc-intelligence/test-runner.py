#!/usr/bin/env python3
"""
Test runner for Documentation Intelligence Layer
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)

    try:
        result = subprocess.run(cmd, cwd='/Users/terryli/.claude',
                              capture_output=True, text=True, check=True)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    print("Testing Documentation Intelligence Layer")

    # Test if we can find agents
    cmd = ['python', 'tools/doc-intelligence/parser.py', '--workspace', '.']
    if not run_command(cmd, "Generate agent registry"):
        sys.exit(1)

    # Test OpenAPI generation
    cmd = ['python', 'tools/doc-intelligence/openapi_gen.py', '--workspace', '.']
    if not run_command(cmd, "Generate OpenAPI specs"):
        print("OpenAPI generation failed, but continuing...")

    # Test schema generation
    cmd = ['python', 'tools/doc-intelligence/schema_builder.py', '--workspace', '.']
    if not run_command(cmd, "Generate JSON schemas"):
        print("Schema generation failed, but continuing...")

    # Test query interface
    cmd = ['python', 'tools/doc-intelligence/query.py', 'git commit', '--workspace', '.']
    if not run_command(cmd, "Test query interface"):
        print("Query test failed, but continuing...")

    print(f"\n{'='*60}")
    print("Documentation Intelligence Layer test complete!")
    print('='*60)

if __name__ == "__main__":
    main()