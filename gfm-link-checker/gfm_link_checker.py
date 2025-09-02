#!/usr/bin/env python3
"""
GitHub Flavored Markdown Link Integrity Checker for Local Workspaces
Ultra-comprehensive validation with GitHub-specific behavior awareness.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from mistletoe import Document
from mistletoe.span_token import Link, AutoLink
import pathspec

try:
    import httpx
except ImportError:
    print("ERROR: 'httpx' module is required for link checking functionality")
    print("Install with: uv add httpx")
    sys.exit(1)


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
        self.gitignore_spec = self._load_gitignore_patterns()
        
        # Sub-repository ignore configuration
        self.include_ignored = self.config.get('include_ignored', False)
        self.verbose = self.config.get('verbose', False)
        self.skipped_directories = []
        
        # Comprehensive ignore patterns for directories (case-insensitive)
        self.ignore_patterns = {
            # Third-party dependencies
            'repos', 'vendor', 'third_party', 'third-party', 
            'node_modules', 'packages', 'dependencies',
            # Development environment
            '.git', '.venv', 'venv', 'env', '.tox', 
            '__pycache__', '.pytest_cache', 'build', 'dist', '.eggs',
            # IDE and editor directories
            '.vscode', '.idea', '.vs', '.sublime-project',
            # Cache and temporary directories
            '.ruff_cache', '.mypy_cache', '.coverage', 'htmlcov',
            # System and runtime directories  
            'bin', 'lib', 'include', 'share', 'var', 'tmp'
        }
        
        # GitHub-specific patterns
        self.github_anchor_pattern = re.compile(r'^[a-z0-9\-_]+$')
        self.relative_link_pattern = re.compile(r'^(?!https?://|mailto:|#)')
        
        # Special directories that need markdown files for functional purposes
        self.functional_md_dirs = {
            'commands',      # Executable slash commands for Claude Code - NO docs/README allowed
            'system',        # System configuration and status files
            'history',       # Historical documentation and logs
            'shell-snapshots', # Shell state snapshots
            'agents',        # Agent configuration files (only README.md allowed)
            'automation',    # Automation system configs (only README.md allowed)  
            'tmux',          # Terminal multiplexer configs (only README.md allowed)
            'tools',         # Tool directories (only README.md allowed)
        }
        
    def _find_git_root(self) -> Path:
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
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git repository required but git command failed: {e}")
        except FileNotFoundError:
            raise RuntimeError("Git repository required but git command not found")
    
    def _should_ignore_directory(self, dir_path: Path) -> bool:
        """Check if a directory should be ignored for documentation organization checks."""
        dir_name = dir_path.name.lower()
        
        # Check built-in ignore patterns
        if dir_name in self.ignore_patterns:
            return True
            
        # Check for hidden directories (starting with .)
        if dir_name.startswith('.'):
            return True
            
        # Check for functional markdown directories
        if dir_name in self.functional_md_dirs:
            return True
            
        return False
    
    def _load_gitignore_patterns(self) -> pathspec.PathSpec:
        """Load gitignore patterns from .gitignore files using pathspec."""
        patterns = []
        
        # Default patterns to always ignore
        default_patterns = [
            '.git/',
            'node_modules/',
            '.venv/',
            '__pycache__/',
            '.pytest_cache/',
            '*.pyc',
            '.DS_Store',
            'Thumbs.db',
        ]
        patterns.extend(default_patterns)
        
        # Find and load .gitignore files walking up from workspace to git root
        search_paths = [self.workspace_path]
        if self.git_root != self.workspace_path:
            # Add all parent directories up to git root
            current = self.workspace_path
            while current != self.git_root and current.parent != current:
                current = current.parent
                search_paths.append(current)
            search_paths.append(self.git_root)
        
        # Load patterns from all .gitignore files
        for search_path in search_paths:
            gitignore_path = search_path / '.gitignore'
            if gitignore_path.exists():
                try:
                    with open(gitignore_path, 'r', encoding='utf-8') as f:
                        gitignore_patterns = f.read().splitlines()
                        # Filter out comments and empty lines
                        gitignore_patterns = [
                            line.strip() for line in gitignore_patterns 
                            if line.strip() and not line.strip().startswith('#')
                        ]
                        patterns.extend(gitignore_patterns)
                except Exception as e:
                    raise RuntimeError(f"Failed to read required gitignore file {gitignore_path}: {e}")
        
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    def _should_skip_directory(self, dir_path: Path) -> Tuple[bool, str]:
        """Check if a directory should be skipped based on ignore patterns."""
        if self.include_ignored:
            return False, ""
            
        dir_name = dir_path.name.lower()
        
        # Check built-in ignore patterns (case-insensitive)
        if dir_name in self.ignore_patterns:
            return True, f"built-in pattern ({dir_name})"
        
        # Check if it's a symlink pointing to an ignored directory
        if dir_path.is_symlink():
            try:
                target = dir_path.resolve()
                if target.is_dir():
                    target_name = target.name.lower()
                    if target_name in self.ignore_patterns:
                        return True, f"symlink to ignored directory ({target_name})"
            except (OSError, RuntimeError):
                # Broken symlink or circular reference
                return True, "broken symlink"
        
        # Check .gitmodules for submodule paths
        gitmodules_path = self.git_root / '.gitmodules'
        if gitmodules_path.exists():
            try:
                rel_path = dir_path.relative_to(self.git_root)
                gitmodules_content = gitmodules_path.read_text(encoding='utf-8')
                if f'path = {rel_path}' in gitmodules_content:
                    return True, "git submodule"
            except (ValueError, OSError):
                pass
        
        # Check gitignore patterns
        if self._is_ignored(dir_path):
            return True, "gitignore pattern"
            
        return False, ""
    
    def _is_ignored(self, file_path: Path) -> bool:
        """Check if a file path should be ignored based on gitignore patterns."""
        # Convert to relative path from git root
        base_path = self.git_root
        try:
            rel_path = file_path.relative_to(base_path)
            # pathspec expects forward slashes
            rel_path_str = str(rel_path).replace('\\', '/')
            return self.gitignore_spec.match_file(rel_path_str)
        except ValueError:
            # Path is not relative to base_path, don't ignore
            return False
    
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the workspace, respecting ignore patterns."""
        markdown_files = []
        markdown_extensions = {'.md', '.markdown', '.mdown', '.mkdn'}
        
        # Walk directories manually to skip ignored ones
        def walk_directory(current_path: Path):
            try:
                # Check if we can read the directory
                entries = list(current_path.iterdir())
            except PermissionError as e:
                raise PermissionError(f"Permission denied accessing directory {current_path}: {e}")
            except OSError as e:
                raise OSError(f"Cannot read directory {current_path}: {e}")
            
            for entry in entries:
                if entry.is_file():
                    # Check if it's a markdown file
                    if entry.suffix.lower() in markdown_extensions:
                        # Apply gitignore filtering to files
                        if not self._is_ignored(entry):
                            markdown_files.append(entry)
                elif entry.is_dir():
                    # Check if directory should be skipped
                    should_skip, reason = self._should_skip_directory(entry)
                    if should_skip:
                        self.skipped_directories.append((entry, reason))
                        if self.verbose:
                            print(f"⏭️  Skipping directory: {entry.relative_to(self.workspace_path)} ({reason})")
                    else:
                        # Recursively walk non-ignored directories
                        walk_directory(entry)
        
        # Start walking from workspace root
        walk_directory(self.workspace_path)
        
        # Report skipped directories summary
        if self.verbose and self.skipped_directories:
            skip_counts = {}
            for _, reason in self.skipped_directories:
                skip_counts[reason] = skip_counts.get(reason, 0) + 1
            
            print(f"\n📊 Skipped {len(self.skipped_directories)} directories:")
            for reason, count in skip_counts.items():
                print(f"   • {count} directories: {reason}")
        
        return markdown_files
    
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
            # If mistletoe fails, raise exception immediately
            raise RuntimeError(f"Failed to parse markdown file {file_path}: {e}")
        
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
            target_path = self.git_root / file_part.lstrip('/')
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
    
    def check_readme_completeness(self, markdown_files: List[Path]) -> List[LinkValidationResult]:
        """Check that each README.md contains links to all sibling markdown files."""
        results = []
        
        # Group files by directory
        dirs_with_files = {}
        for file_path in markdown_files:
            dir_path = file_path.parent
            if dir_path not in dirs_with_files:
                dirs_with_files[dir_path] = []
            dirs_with_files[dir_path].append(file_path)
        
        # Check each directory that has a README.md
        for dir_path, files_in_dir in dirs_with_files.items():
            readme_path = dir_path / 'README.md'
            
            # Skip if no README.md in this directory
            if readme_path not in files_in_dir:
                continue
                
            # Skip Claude Code directories - README.md files conflict with slash commands
            if '.claude' in str(dir_path) and str(dir_path) != str(self.workspace_path):
                continue
                
            # Skip directories that should be ignored for completeness checks
            if self._should_ignore_directory(dir_path):
                continue
                
            # Get all non-README markdown files in this directory
            sibling_files = [f for f in files_in_dir if f.name != 'README.md']
            
            if not sibling_files:
                continue  # No siblings to link to
            
            # Read README content
            try:
                readme_content = readme_path.read_text(encoding='utf-8')
            except Exception as e:
                results.append(LinkValidationResult(
                    link='', source_file=str(readme_path), line_number=0,
                    is_valid=False, error_type='read_error',
                    error_message=f'Cannot read README: {e}', link_type='completeness'
                ))
                continue
            
            # Check which sibling files are linked
            for sibling in sibling_files:
                sibling_name = sibling.name
                sibling_relative = sibling.relative_to(dir_path)
                
                # Check various link formats that could reference this file
                link_patterns = [
                    sibling_name,                    # filename.md
                    f'./{sibling_name}',            # ./filename.md
                    str(sibling_relative),          # path/filename.md
                    f'./{sibling_relative}',        # ./path/filename.md
                ]
                
                # Check if any pattern is found in README
                is_linked = any(pattern in readme_content for pattern in link_patterns)
                
                if not is_linked:
                    results.append(LinkValidationResult(
                        link=sibling_name, source_file=str(readme_path), line_number=0,
                        is_valid=False, error_type='missing_navigation',
                        error_message=f'README does not link to sibling file: {sibling_name}',
                        link_type='completeness'
                    ))
                else:
                    # Add successful completeness check
                    results.append(LinkValidationResult(
                        link=sibling_name, source_file=str(readme_path), line_number=0,
                        is_valid=True, error_type='', error_message='',
                        link_type='completeness'
                    ))
        
        return results
    
    def check_claude_code_restrictions(self, markdown_files: List[Path]) -> List[LinkValidationResult]:
        """Check Claude Code specific restrictions for .claude directories and root README."""
        results = []
        
        # Check 1: No markdown files in project .claude directories (except global ~/.claude)
        home_claude = Path.home() / '.claude'
        for file_path in markdown_files:
            # Check if file is in a .claude directory
            if '.claude' in str(file_path):
                # Allow files in global ~/.claude directory
                if not str(file_path).startswith(str(home_claude)):
                    # This is a project .claude directory - no markdown allowed
                    results.append(LinkValidationResult(
                        link='', source_file=str(file_path), line_number=0,
                        is_valid=False, error_type='claude_code_conflict',
                        error_message=f'Markdown files not allowed in project .claude directories (Claude Code slash command conflict): {file_path}',
                        link_type='claude_restriction'
                    ))
        
        # Check 2: No docs/ or README.md in commands directory (they become executable commands)
        for file_path in markdown_files:
            path_parts = file_path.parts
            if 'commands' in path_parts:
                commands_index = path_parts.index('commands')
                # Check if this is directly in commands/ or in commands/docs/
                if len(path_parts) > commands_index + 1:
                    subpath = path_parts[commands_index + 1]
                    if subpath in ('docs', 'README.md') or file_path.name == 'README.md':
                        results.append(LinkValidationResult(
                            link='', source_file=str(file_path), line_number=0,
                            is_valid=False, error_type='commands_directory_conflict',
                            error_message=f'No docs/ or README.md allowed in commands directory - they become executable slash commands: {file_path}',
                            link_type='claude_restriction'
                        ))
        
        # Check 3: No root README.md when docs/README.md exists
        root_readme = self.workspace_path / 'README.md'
        docs_readme = self.workspace_path / 'docs' / 'README.md'
        
        if root_readme.exists() and docs_readme.exists():
            results.append(LinkValidationResult(
                link='', source_file=str(root_readme), line_number=0,
                is_valid=False, error_type='root_readme_delegation',
                error_message='Root README.md should not exist when docs/README.md is present (use docs/README.md as main documentation)',
                link_type='claude_restriction'
            ))
        elif root_readme.exists() and not docs_readme.exists():
            results.append(LinkValidationResult(
                link='', source_file=str(root_readme), line_number=0,
                is_valid=False, error_type='root_readme_delegation',
                error_message='Root README.md should be moved to docs/README.md for better organization',
                link_type='claude_restriction'
            ))
        
        # Check 4: Documentation organization - root-level docs should be in docs/ directories
        results.extend(self.check_documentation_organization(markdown_files))
        
        return results
    
    def check_documentation_organization(self, markdown_files: List[Path]) -> List[LinkValidationResult]:
        """Check that documentation files are properly organized in docs/ directories."""
        results = []
        
        # Files that should be allowed in root directories
        allowed_root_files = {
            'README.md',   # Navigation file
            'CLAUDE.md',   # Claude Code user memory (special case)
            'LICENSE.md', 'LICENSE', 'COPYING.md',  # Legal files
            'CHANGELOG.md', 'HISTORY.md', 'NEWS.md',  # Project history
            'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md',  # Community files
        }
        
        for file_path in markdown_files:
            # Check if this is a root-level documentation file (not README.md)
            relative_path = file_path.relative_to(self.workspace_path)
            path_parts = relative_path.parts
            
            # Skip if already in a docs/ directory
            if 'docs' in path_parts:
                continue
                
            # Skip if in a deep subdirectory (only check 1-2 levels deep)
            if len(path_parts) > 2:
                continue
                
            # Skip allowed root files
            if file_path.name in allowed_root_files:
                continue
                
            # Skip directories that should be ignored for documentation organization
            parent_dir_path = file_path.parent
            if self._should_ignore_directory(parent_dir_path):
                continue
            
            # This appears to be a documentation file that should be in docs/
            if len(path_parts) == 1:  # Root level file
                results.append(LinkValidationResult(
                    link='', source_file=str(file_path), line_number=0,
                    is_valid=False, error_type='documentation_organization',
                    error_message=f'Documentation file should be moved to docs/ directory: {file_path.name}',
                    link_type='organization_policy'
                ))
            elif len(path_parts) == 2 and file_path.name != 'README.md':  # Subdirectory doc file
                subdir_path = self.workspace_path / path_parts[0]
                # Only flag if the subdirectory itself shouldn't be ignored
                if not self._should_ignore_directory(subdir_path):
                    results.append(LinkValidationResult(
                        link='', source_file=str(file_path), line_number=0,
                        is_valid=False, error_type='documentation_organization',
                        error_message=f'Documentation file should be moved to {path_parts[0]}/docs/ directory: {file_path.name}',
                        link_type='organization_policy'
                    ))
        
        return results
    
    def auto_fix_links(self, results: List[LinkValidationResult]) -> int:
        """Auto-fix broken internal links where possible."""
        fixes_applied = 0
        
        if not self.config.get('auto_fix', False):
            return fixes_applied
            
        # Group results by source file for batch processing
        files_to_fix = {}
        for result in results:
            if not result.is_valid and result.error_type in ['file_not_found', 'missing_readme', 'invalid_anchor']:
                # Only auto-fix internal link issues
                if result.link_type in ['local_file', 'directory', 'local_anchor']:
                    source_file = result.source_file
                    if source_file not in files_to_fix:
                        files_to_fix[source_file] = []
                    files_to_fix[source_file].append(result)
        
        for source_file_path, file_results in files_to_fix.items():
            try:
                source_path = Path(source_file_path)
                if not source_path.exists():
                    continue
                    
                # Try to apply fixes for this file
                file_fixes = self._fix_file_links(source_path, file_results)
                fixes_applied += file_fixes
                
            except Exception as e:
                print(f"⚠️  Could not auto-fix links in {source_file_path}: {e}")
        
        return fixes_applied
    
    def _fix_file_links(self, source_path: Path, results: List[LinkValidationResult]) -> int:
        """Fix links in a specific file."""
        fixes_applied = 0
        
        try:
            content = source_path.read_text(encoding='utf-8')
            original_content = content
            
            for result in results:
                if result.error_type == 'missing_readme':
                    # Create missing README.md for directories
                    link_parts = result.link.split('#', 1)
                    file_part = link_parts[0]
                    
                    # Resolve the target directory
                    if file_part.startswith('/'):
                        target_dir = self.git_root / file_part.lstrip('/')
                    else:
                        target_dir = (source_path.parent / file_part).resolve()
                    
                    if target_dir.is_dir():
                        readme_path = target_dir / 'README.md'
                        if not readme_path.exists():
                            # Create basic README
                            readme_content = f"# {target_dir.name}\n\nDocumentation for {target_dir.name}.\n"
                            readme_path.write_text(readme_content, encoding='utf-8')
                            print(f"✅ Created missing README: {readme_path}")
                            fixes_applied += 1
                
                elif result.error_type == 'file_not_found':
                    # Try to find similar files and suggest corrections
                    # This is more complex - for now, just report
                    print(f"⚠️  Cannot auto-fix missing file: {result.link} (manual intervention required)")
                
                elif result.error_type == 'invalid_anchor':
                    # Try to fix anchor references by finding similar headings
                    # This is complex and error-prone - skip for now
                    print(f"⚠️  Cannot auto-fix invalid anchor: {result.link} (manual intervention required)")
            
            # If content was modified, write it back
            if content != original_content:
                source_path.write_text(content, encoding='utf-8')
                print(f"✅ Fixed links in: {source_path}")
                
        except Exception as e:
            print(f"❌ Error fixing links in {source_path}: {e}")
        
        return fixes_applied
    
    def check_workspace(self) -> Dict:
        """Check all markdown files in the workspace."""
        markdown_files = self.find_markdown_files()
        
        print(f"Found {len(markdown_files)} markdown files to check...")
        
        all_results = []
        for file_path in markdown_files:
            print(f"Checking: {file_path.relative_to(self.workspace_path)}")
            file_results = self.check_file(file_path)
            all_results.extend(file_results)
        
        # Check README completeness by default
        if self.config.get('check_completeness', True):
            print("Checking README completeness...")
            completeness_results = self.check_readme_completeness(markdown_files)
            all_results.extend(completeness_results)
        
        # Check Claude Code specific restrictions
        print("Checking Claude Code restrictions...")
        restriction_results = self.check_claude_code_restrictions(markdown_files)
        all_results.extend(restriction_results)
        
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
        '--no-completeness', '-nc',
        action='store_true',
        help='Skip README completeness checking (default: completeness checking enabled)'
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
    parser.add_argument(
        '--include-ignored', '-ii',
        action='store_true',
        help='Include ignored directories (third-party dependencies, development environment)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output showing skipped directories and permission issues'
    )
    parser.add_argument(
        '--fix', '-x',
        action='store_true',
        help='Auto-fix broken internal links only (external links are reported for manual review)'
    )
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'check_external': not args.no_external,
        'check_completeness': not args.no_completeness,
        'auto_fix': args.fix,
        'include_ignored': args.include_ignored,
        'verbose': args.verbose
    }
    
    # Initialize checker
    checker = GFMLinkChecker(args.workspace, config)
    
    # Run checks
    results = checker.check_workspace()
    
    # Apply auto-fixes if requested
    if args.fix and results['invalid_links'] > 0:
        print("\n🔧 Applying auto-fixes for internal links...")
        fixes_applied = checker.auto_fix_links(results['all_results'])
        
        if fixes_applied > 0:
            print(f"✅ Applied {fixes_applied} auto-fixes. Re-running validation...")
            # Re-run checks to verify fixes
            results = checker.check_workspace()
        else:
            print("ℹ️  No auto-fixable issues found.")
    
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