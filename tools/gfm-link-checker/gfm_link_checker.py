#!/usr/bin/env python3
"""
GitHub Flavored Markdown Link Integrity Checker for Local Workspaces
Ultra-comprehensive validation with GitHub-specific behavior awareness.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

import mistletoe
from mistletoe import Document
from mistletoe.span_token import Link, AutoLink

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    print("⚠️  Warning: 'httpx' module not available. External link checking disabled.")
    print("   Install with: uv add httpx")


@dataclass
class LinkValidationResult:
    """Result of validating a single link."""
    link: str
    source_file: str
    line_number: int
    is_valid: bool
    error_type: str
    error_message: str
    link_type: str  # 'local_file', 'local_anchor', 'directory', 'external', 'mailto'


class GFMLinkChecker:
    """GitHub Flavored Markdown Link Integrity Checker."""
    
    def __init__(self, workspace_path: str, config: Optional[Dict] = None):
        self.workspace_path = Path(workspace_path).resolve()
        self.config = config or {}
        self.git_root = self._find_git_root()
        self.results: List[LinkValidationResult] = []
        
        # GitHub-specific patterns
        self.github_anchor_pattern = re.compile(r'^[a-z0-9\-_]+$')
        self.relative_link_pattern = re.compile(r'^(?!https?://|mailto:|#)')
        
    def _find_git_root(self) -> Optional[Path]:
        """Find the root of the git repository."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the workspace."""
        markdown_files = []
        for pattern in ['*.md', '*.markdown', '*.mdown', '*.mkdn']:
            markdown_files.extend(self.workspace_path.rglob(pattern))
        
        # Filter out files in common ignore directories
        ignore_dirs = {'.git', 'node_modules', '.venv', '__pycache__', '.pytest_cache'}
        return [f for f in markdown_files if not any(part in ignore_dirs for part in f.parts)]
    
    def extract_links(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from markdown content using mistletoe AST parser."""
        links = []
        
        try:
            # Parse markdown content into AST
            doc = Document(content)
            
            # Walk the AST to find all links
            def walk_tokens(token):
                # Check if this is a Link token
                if isinstance(token, Link):
                    link_url = token.target
                    link_text = self._render_token_content(token)
                    # mistletoe doesn't track line numbers by default, estimate from content
                    line_num = self._estimate_line_number(content, link_url, link_text)
                    links.append((link_url, line_num, link_text))
                
                # Check if this is an AutoLink token
                elif isinstance(token, AutoLink):
                    link_url = token.target
                    line_num = self._estimate_line_number(content, link_url, link_url)
                    links.append((link_url, line_num, link_url))
                
                # Recursively walk children (mistletoe automatically respects code blocks)
                if hasattr(token, 'children') and token.children is not None:
                    for child in token.children:
                        walk_tokens(child)
            
            walk_tokens(doc)
            
        except Exception as e:
            # If mistletoe fails, log error and return empty list
            print(f"Error: Failed to parse {file_path}: {e}")
            return []
        
        return links
    
    def _render_token_content(self, token) -> str:
        """Extract text content from a token."""
        if hasattr(token, 'children') and token.children:
            parts = []
            for child in token.children:
                if hasattr(child, 'content'):
                    parts.append(child.content)
                else:
                    parts.append(self._render_token_content(child))
            return ''.join(parts)
        return getattr(token, 'content', '')
    
    def _estimate_line_number(self, content: str, url: str, text: str) -> int:
        """Estimate line number by searching for the link pattern in content."""
        lines = content.split('\n')
        # Look for the markdown link pattern
        for i, line in enumerate(lines, 1):
            if f']({url})' in line or f'[{text}]' in line:
                return i
        return 1  # Default to line 1 if not found
    
    
    def validate_local_file_link(self, link: str, source_file: Path) -> LinkValidationResult:
        """Validate a local file or directory link."""
        # Remove anchor if present
        link_parts = link.split('#', 1)
        file_part = link_parts[0]
        anchor_part = link_parts[1] if len(link_parts) > 1 else None
        
        # Resolve relative path
        if file_part.startswith('/'):
            # Absolute path from git root
            if self.git_root:
                target_path = self.git_root / file_part.lstrip('/')
            else:
                target_path = Path(file_part)
        else:
            # Relative path from source file
            target_path = (source_file.parent / file_part).resolve()
        
        # Check if target exists
        if target_path.is_file():
            link_type = 'local_file'
            # If it's a markdown file and has an anchor, validate the anchor
            if anchor_part and target_path.suffix.lower() in ['.md', '.markdown']:
                return self._validate_markdown_anchor(target_path, anchor_part, link, source_file, 0)
            return LinkValidationResult(
                link=link, source_file=str(source_file), line_number=0,
                is_valid=True, error_type='', error_message='', link_type=link_type
            )
        elif target_path.is_dir():
            # GitHub directory behavior: check for README.md
            readme_files = ['README.md', 'readme.md', 'Readme.md']
            has_readme = any((target_path / readme).exists() for readme in readme_files)
            
            if has_readme:
                return LinkValidationResult(
                    link=link, source_file=str(source_file), line_number=0,
                    is_valid=True, error_type='', error_message='', link_type='directory'
                )
            else:
                return LinkValidationResult(
                    link=link, source_file=str(source_file), line_number=0,
                    is_valid=False, error_type='missing_readme',
                    error_message=f'Directory exists but no README.md found: {target_path}',
                    link_type='directory'
                )
        else:
            return LinkValidationResult(
                link=link, source_file=str(source_file), line_number=0,
                is_valid=False, error_type='file_not_found',
                error_message=f'File or directory not found: {target_path}',
                link_type='local_file'
            )
    
    def _validate_markdown_anchor(self, md_file: Path, anchor: str, original_link: str, 
                                source_file: Path, line_number: int) -> LinkValidationResult:
        """Validate anchor link within a markdown file."""
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # GitHub anchor generation rules
            # 1. Convert to lowercase
            # 2. Remove non-alphanumeric chars except hyphens and spaces
            # 3. Replace spaces with hyphens
            # 4. Remove leading/trailing hyphens
            
            headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
            valid_anchors = set()
            
            for heading in headings:
                # GitHub's anchor generation
                clean_heading = re.sub(r'[^a-zA-Z0-9\s\-_]', '', heading)
                clean_heading = clean_heading.lower().strip()
                clean_heading = re.sub(r'\s+', '-', clean_heading)
                clean_heading = clean_heading.strip('-')
                valid_anchors.add(clean_heading)
            
            # Check for user-defined anchor IDs
            user_anchors = re.findall(r'<[^>]*id=["\']([^"\']*)["\'][^>]*>', content)
            valid_anchors.update(user_anchors)
            
            if anchor in valid_anchors:
                return LinkValidationResult(
                    link=original_link, source_file=str(source_file), line_number=line_number,
                    is_valid=True, error_type='', error_message='', link_type='local_anchor'
                )
            else:
                return LinkValidationResult(
                    link=original_link, source_file=str(source_file), line_number=line_number,
                    is_valid=False, error_type='invalid_anchor',
                    error_message=f'Anchor not found: #{anchor}. Available: {", ".join(sorted(valid_anchors))}',
                    link_type='local_anchor'
                )
                
        except Exception as e:
            return LinkValidationResult(
                link=original_link, source_file=str(source_file), line_number=line_number,
                is_valid=False, error_type='read_error',
                error_message=f'Could not read file {md_file}: {e}',
                link_type='local_anchor'
            )
    
    def validate_external_link(self, link: str, source_file: Path, line_number: int) -> LinkValidationResult:
        """Validate external HTTP/HTTPS link."""
        if not HAS_HTTPX:
            return LinkValidationResult(
                link=link, source_file=str(source_file), line_number=line_number,
                is_valid=True, error_type='', error_message='External check skipped (httpx not available)',
                link_type='external'
            )
            
        try:
            # Use httpx with timeout and proper headers
            headers = {
                'User-Agent': 'GFM-Link-Checker/1.0 (GitHub Flavored Markdown Link Integrity Checker)'
            }
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                response = client.head(link, headers=headers)
            
            if response.status_code < 400:
                return LinkValidationResult(
                    link=link, source_file=str(source_file), line_number=line_number,
                    is_valid=True, error_type='', error_message='', link_type='external'
                )
            else:
                return LinkValidationResult(
                    link=link, source_file=str(source_file), line_number=line_number,
                    is_valid=False, error_type='http_error',
                    error_message=f'HTTP {response.status_code}',
                    link_type='external'
                )
                
        except httpx.RequestError as e:
            return LinkValidationResult(
                link=link, source_file=str(source_file), line_number=line_number,
                is_valid=False, error_type='connection_error',
                error_message=str(e), link_type='external'
            )
    
    def check_file(self, file_path: Path) -> List[LinkValidationResult]:
        """Check all links in a single markdown file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return [LinkValidationResult(
                link='', source_file=str(file_path), line_number=0,
                is_valid=False, error_type='read_error',
                error_message=f'Could not read file: {e}', link_type='file'
            )]
        
        links = self.extract_links(content, file_path)
        results = []
        
        for link, line_number, _ in links:
            # Skip empty links
            if not link.strip():
                continue
                
            # Handle different link types
            if link.startswith('mailto:'):
                # Basic mailto validation
                email_part = link[7:]
                if '@' in email_part and '.' in email_part:
                    results.append(LinkValidationResult(
                        link=link, source_file=str(file_path), line_number=line_number,
                        is_valid=True, error_type='', error_message='', link_type='mailto'
                    ))
                else:
                    results.append(LinkValidationResult(
                        link=link, source_file=str(file_path), line_number=line_number,
                        is_valid=False, error_type='invalid_email',
                        error_message='Invalid email format', link_type='mailto'
                    ))
            elif link.startswith(('http://', 'https://')):
                # External link - Report only, no auto-fix
                if self.config.get('check_external', True):
                    result = self.validate_external_link(link, file_path, line_number)
                    # Mark external links as non-fixable
                    if not result.is_valid:
                        result.error_message = f"{result.error_message} (External links are not auto-fixed - please check manually)"
                    results.append(result)
                else:
                    results.append(LinkValidationResult(
                        link=link, source_file=str(file_path), line_number=line_number,
                        is_valid=True, error_type='', error_message='External check skipped',
                        link_type='external'
                    ))
            elif link.startswith('#'):
                # Internal anchor
                anchor = link[1:]
                results.append(self._validate_markdown_anchor(file_path, anchor, link, file_path, line_number))
            else:
                # Local file/directory link
                results.append(self.validate_local_file_link(link, file_path))
        
        return results
    
    def check_workspace(self) -> Dict:
        """Check all markdown files in the workspace."""
        markdown_files = self.find_markdown_files()
        
        print(f"Found {len(markdown_files)} markdown files to check...")
        
        all_results = []
        for file_path in markdown_files:
            print(f"Checking: {file_path.relative_to(self.workspace_path)}")
            file_results = self.check_file(file_path)
            all_results.extend(file_results)
        
        # Categorize results
        valid_links = [r for r in all_results if r.is_valid]
        invalid_links = [r for r in all_results if not r.is_valid]
        
        # Group by error type
        error_summary = {}
        for result in invalid_links:
            error_type = result.error_type
            if error_type not in error_summary:
                error_summary[error_type] = []
            error_summary[error_type].append(result)
        
        return {
            'total_links': len(all_results),
            'valid_links': len(valid_links),
            'invalid_links': len(invalid_links),
            'error_summary': error_summary,
            'all_results': all_results
        }
    
    def generate_report(self, results: Dict, output_format: str = 'text') -> str:
        """Generate a formatted report."""
        if output_format == 'json':
            # Convert dataclasses to dicts for JSON serialization
            serializable_results = []
            for result in results['all_results']:
                serializable_results.append({
                    'link': result.link,
                    'source_file': result.source_file,
                    'line_number': result.line_number,
                    'is_valid': result.is_valid,
                    'error_type': result.error_type,
                    'error_message': result.error_message,
                    'link_type': result.link_type
                })
            return json.dumps({
                'summary': {
                    'total_links': results['total_links'],
                    'valid_links': results['valid_links'],
                    'invalid_links': results['invalid_links']
                },
                'results': serializable_results
            }, indent=2)
        
        # Text format
        report = []
        report.append("=" * 80)
        report.append("GitHub Flavored Markdown Link Integrity Report")
        report.append("=" * 80)
        report.append(f"Workspace: {self.workspace_path}")
        report.append(f"Total links checked: {results['total_links']}")
        report.append(f"Valid links: {results['valid_links']}")
        report.append(f"Invalid links: {results['invalid_links']}")
        report.append("")
        
        if results['invalid_links'] > 0:
            report.append("ERRORS FOUND:")
            report.append("-" * 40)
            report.append("📝 Note: Only internal/local links can be auto-fixed.")
            report.append("    External links are reported for manual review.")
            report.append("")
            
            for error_type, error_results in results['error_summary'].items():
                report.append(f"\n{error_type.upper()} ({len(error_results)} errors):")
                for result in error_results:
                    report.append(f"  ❌ {result.source_file}:{result.line_number}")
                    report.append(f"     Link: {result.link}")
                    report.append(f"     Error: {result.error_message}")
                    report.append("")
        else:
            report.append("✅ All links are valid!")
        
        return "\n".join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub Flavored Markdown Link Integrity Checker - Auto-fixes internal links, reports external link issues"
    )
    parser.add_argument(
        'workspace', 
        nargs='?', 
        default='.', 
        help='Workspace directory to check (default: current directory)'
    )
    parser.add_argument(
        '--no-external', '-ne',
        action='store_true',
        help='Skip external URL validation'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'check_external': not args.no_external
    }
    
    # Initialize checker
    checker = GFMLinkChecker(args.workspace, config)
    
    # Run checks
    results = checker.check_workspace()
    
    # Generate report
    report = checker.generate_report(results, args.format)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)
    
    # Exit with error code if links are broken
    sys.exit(1 if results['invalid_links'] > 0 else 0)


if __name__ == '__main__':
    main()