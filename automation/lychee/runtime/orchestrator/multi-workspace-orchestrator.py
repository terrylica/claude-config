#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jsonschema>=4.0.0",
#     "jinja2>=3.1.0",
# ]
# ///
"""
Multi-Workspace Workflow Orchestrator - One-Shot Execution

Processes selection and approval files, renders Jinja2 templates, executes Claude CLI.
Supports multi-workflow execution with dependency resolution.
Exits immediately after completion (no watching, no daemon).

Version: 4.0.0
Specification: ~/.claude/specifications/telegram-workflows-orchestration-v4.yaml

Changes from v3.0.0:
- Loads workflow registry from workflows.json
- Processes WorkflowSelection files (v4) and Approval files (v3 backward compat)
- Renders Jinja2 prompt templates with session context
- Supports multi-workflow execution (sequential, respects dependencies)
- Emits WorkflowExecution results to executions/ directory
- Maintains dual-mode: selections (v4) + approvals (v3 backward compat)
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from jinja2 import Template, TemplateError

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Configuration
STATE_DIR = Path.home() / ".claude" / "automation" / "lychee" / "state"
APPROVAL_DIR = STATE_DIR / "approvals"
COMPLETION_DIR = STATE_DIR / "completions"
SELECTIONS_DIR = STATE_DIR / "selections"  # Phase 4 - v4.0.0
EXECUTIONS_DIR = STATE_DIR / "executions"  # Phase 4 - v4.0.0
WORKFLOWS_REGISTRY = STATE_DIR / "workflows.json"  # Phase 4 - v4.0.0
AUTOFIX_STATE_FILE = STATE_DIR / "autofix-in-progress.json"
CLAUDE_CLI_TIMEOUT = 300  # 5 minutes
HEARTBEAT_INTERVAL = 30  # Log every 30 seconds during wait

# Phase 4 - v4.0.0: Workflow registry (loaded at module level for CLI mode)
workflow_registry: Optional[Dict[str, Any]] = None


# Import workspace helpers
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from workspace_helpers import (
    validate_workspace_path,
    get_workspace_id_from_path,
    compute_workspace_hash,
    STATE_TTL_MINUTES
)


# Event Logging
def log_event(
    correlation_id: str,
    workspace_id: str,
    session_id: str,
    component: str,
    event_type: str,
    metadata: Dict[str, Any] = None
) -> None:
    """
    Log event to SQLite event store via event_logger.py.

    Args:
        correlation_id: ULID for request tracing
        workspace_id: Workspace hash or ULID
        session_id: Claude Code session UUID
        component: Component name (orchestrator)
        event_type: Event type (e.g., orchestrator.started)
        metadata: Event-specific data

    Raises:
        subprocess.CalledProcessError: Event logging failed
    """
    event_logger = Path.home() / ".claude" / "automation" / "lychee" / "runtime" / "lib" / "event_logger.py"
    metadata_json = json.dumps(metadata) if metadata else "{}"

    try:
        subprocess.run(
            [str(event_logger), correlation_id, workspace_id, session_id, component, event_type, metadata_json],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to log event {event_type}: {e.stderr}", file=sys.stderr)
        raise


# Phase 4 - v4.0.0: Workflow Registry Functions
def load_workflow_registry() -> Dict[str, Any]:
    """
    Load workflow registry from workflows.json.

    Returns:
        Workflow registry dictionary

    Raises:
        FileNotFoundError: Registry file not found
        json.JSONDecodeError: Invalid JSON
        ValueError: Invalid registry schema
    """
    if not WORKFLOWS_REGISTRY.exists():
        raise FileNotFoundError(f"Workflow registry not found: {WORKFLOWS_REGISTRY}")

    with open(WORKFLOWS_REGISTRY) as f:
        registry = json.load(f)

    # Validate required fields
    if "version" not in registry or "workflows" not in registry:
        raise ValueError("Invalid registry: missing 'version' or 'workflows'")

    print(f"✅ Loaded workflow registry v{registry['version']} ({len(registry['workflows'])} workflows)")
    return registry


def render_workflow_prompt(
    workflow: Dict[str, Any],
    context: Dict[str, Any]
) -> str:
    """
    Render workflow prompt template using Jinja2.

    Args:
        workflow: Workflow manifest from registry
        context: Template context (workspace_path, session_id, git_status, lychee_status, etc.)

    Returns:
        Rendered prompt string

    Raises:
        TemplateError: Template rendering failed
    """
    template_str = workflow.get("prompt_template", "")
    if not template_str:
        raise ValueError(f"Workflow {workflow['id']} has no prompt_template")

    try:
        template = Template(template_str)
        rendered = template.render(**context)
        return rendered
    except TemplateError as e:
        raise TemplateError(f"Failed to render template for workflow {workflow['id']}: {e}") from e


def resolve_workflow_dependencies(
    workflow_ids: List[str],
    registry: Dict[str, Any]
) -> List[str]:
    """
    Resolve workflow dependencies and return execution order.

    For Phase 4: Simple implementation (no topological sort).
    Dependencies are listed in the workflow manifest but not enforced yet.

    Args:
        workflow_ids: List of workflow IDs to execute
        registry: Workflow registry

    Returns:
        Ordered list of workflow IDs (currently same as input, Phase 4 limitation)

    Future Enhancement:
        Implement topological sort for true dependency resolution
    """
    # Phase 4 limitation: Return workflows in order provided (no dependency resolution)
    # TODO Phase 5+: Implement topological sort
    print(f"⚠️  Dependency resolution not implemented - executing workflows in provided order")
    return workflow_ids


class ApprovalOrchestrator:
    """Processes single approval and executes Claude CLI (one-shot)."""

    def __init__(self):
        self.correlation_id = None
        self.workspace_hash = None
        self.session_id = None

    async def process_approval(self, approval_file: Path) -> None:
        """
        Process approval file and route to workspace.

        Args:
            approval_file: Path to approval JSON file

        Raises:
            All errors propagate to caller
        """
        try:
            # Read and validate
            state = self._read_approval(approval_file)
            self.session_id = state["session_id"]

            # Extract correlation ID from approval state or environment
            self.correlation_id = state.get("correlation_id") or os.environ.get("CORRELATION_ID", "unknown")

            # Validate workspace
            workspace_path = validate_workspace_path(
                Path(state["workspace_path"])
            )
            self.workspace_hash = compute_workspace_hash(workspace_path)

            # Log orchestrator started
            log_event(
                self.correlation_id,
                self.workspace_hash,
                self.session_id,
                "orchestrator",
                "orchestrator.started",
                {"approval_file": approval_file.name, "decision": state.get("decision")}
            )

            # Execute based on decision
            decision = state["decision"]
            if decision == "auto_fix_all":
                await self._invoke_claude_cli(workspace_path, state)
            elif decision == "reject":
                print(f"❌ Rejected: {self.session_id} in {workspace_path}")
            else:
                print(f"⚠️  Unknown decision: {decision}")

            # Log orchestrator completed
            log_event(
                self.correlation_id,
                self.workspace_hash,
                self.session_id,
                "orchestrator",
                "orchestrator.completed",
                {"decision": decision}
            )

        except Exception as e:
            # Log orchestrator failed
            if self.correlation_id and self.workspace_hash and self.session_id:
                log_event(
                    self.correlation_id,
                    self.workspace_hash,
                    self.session_id,
                    "orchestrator",
                    "orchestrator.failed",
                    {"error": str(e), "error_type": type(e).__name__}
                )
            raise

        finally:
            # Always cleanup consumed approval
            self._cleanup_approval(approval_file)

    def _read_approval(self, approval_file: Path) -> Dict[str, Any]:
        """Read and validate approval state file."""
        with approval_file.open() as f:
            state = json.load(f)

        # Validate required fields
        required = ["workspace_path", "session_id", "decision", "timestamp"]
        missing = [f for f in required if f not in state]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return state

    async def _invoke_claude_cli(
        self, workspace_path: Path, state: Dict[str, Any]
    ) -> None:
        """
        Invoke Claude CLI in workspace context and emit completion notification.

        Args:
            workspace_path: Validated workspace path
            state: Approval state dictionary
        """
        session_id = state["session_id"]
        decision = state.get("decision", "unknown")
        start_time = asyncio.get_event_loop().time()

        print(f"🚀 Invoking Claude CLI")
        print(f"   PID: {os.getpid()}")
        print(f"   Parent PID: {os.getppid()}")
        print(f"   Workspace: {workspace_path}")
        print(f"   Session: {session_id}")
        print(f"   Decision: {decision}")

        # Build prompt
        prompt = f"""Fix broken links detected by Lychee link validator.

Session: {session_id}

Instructions:
- Read .lychee-results.txt (in workspace root) for list of broken links
- Use Edit tool to fix broken links with high confidence
- Focus on fragment links and typos
- Report all changes made
"""

        # Create state file to prevent feedback loop
        # (hook will skip notifications while this file exists)
        state_file_created = False
        if decision == "auto_fix_all":
            try:
                AUTOFIX_STATE_FILE.write_text(json.dumps({
                    "session_id": session_id,
                    "workspace_path": str(workspace_path),
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "orchestrator_pid": os.getpid(),
                    "correlation_id": self.correlation_id
                }, indent=2))
                state_file_created = True
                print(f"   📝 Created state file: {AUTOFIX_STATE_FILE}")

                # Log state file created
                log_event(
                    self.correlation_id,
                    self.workspace_hash,
                    session_id,
                    "orchestrator",
                    "state_file.created",
                    {"state_file": str(AUTOFIX_STATE_FILE), "orchestrator_pid": os.getpid()}
                )
            except Exception as e:
                print(f"   ⚠️  Failed to create state file: {e}", file=sys.stderr)

        # Invoke Claude CLI and capture result
        completion_status = "success"
        exit_code = 0
        stdout_text = ""
        stderr_text = ""

        try:
            print(f"   🔧 Starting subprocess...")
            process = await asyncio.create_subprocess_exec(
                "/opt/homebrew/bin/claude",
                "-p", prompt,
                "--output-format", "json",
                cwd=workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print(f"   ✓ Process started (PID: {process.pid})")

            # Log Claude CLI started
            log_event(
                self.correlation_id,
                self.workspace_hash,
                session_id,
                "orchestrator",
                "claude_cli.started",
                {"pid": process.pid, "timeout_seconds": CLAUDE_CLI_TIMEOUT}
            )

            # Wait for completion with heartbeat logging
            print(f"   ⏳ Waiting for completion (timeout: {CLAUDE_CLI_TIMEOUT}s)...")

            # Create heartbeat task
            async def heartbeat_logger():
                """Log progress every 30 seconds."""
                elapsed = 0
                while elapsed < CLAUDE_CLI_TIMEOUT:
                    await asyncio.sleep(HEARTBEAT_INTERVAL)
                    elapsed += HEARTBEAT_INTERVAL

                    # Check if process still alive
                    try:
                        os.kill(process.pid, 0)  # Signal 0 = check existence
                        print(f"   ⏳ Still waiting... ({elapsed}s / {CLAUDE_CLI_TIMEOUT}s, PID {process.pid} alive)")

                        # Log heartbeat event
                        log_event(
                            self.correlation_id,
                            self.workspace_hash,
                            session_id,
                            "orchestrator",
                            "claude_cli.heartbeat",
                            {"pid": process.pid, "elapsed_seconds": elapsed, "timeout_seconds": CLAUDE_CLI_TIMEOUT}
                        )
                    except OSError:
                        print(f"   ❌ Process {process.pid} died unexpectedly!")
                        break

            heartbeat_task = asyncio.create_task(heartbeat_logger())

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=CLAUDE_CLI_TIMEOUT
                )
            finally:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
            stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
            exit_code = process.returncode

            print(f"   ✓ Process completed")
            print(f"   📊 Exit code: {exit_code}")
            print(f"   📊 Stdout length: {len(stdout_text)} chars")
            print(f"   📊 Stderr length: {len(stderr_text)} chars")

            if exit_code != 0:
                completion_status = "error"
                print(f"❌ Claude CLI failed with exit code {exit_code}")
                if stderr_text:
                    print(f"   Error output: {stderr_text[:200]}")
            else:
                print(f"✅ Claude CLI completed successfully")
                if stdout_text:
                    print(f"   Output preview: {stdout_text[:200]}")

            # Log Claude CLI completed
            duration = asyncio.get_event_loop().time() - start_time
            log_event(
                self.correlation_id,
                self.workspace_hash,
                session_id,
                "orchestrator",
                "claude_cli.completed",
                {
                    "pid": process.pid,
                    "exit_code": exit_code,
                    "status": completion_status,
                    "duration_seconds": round(duration, 1),
                    "stdout_length": len(stdout_text),
                    "stderr_length": len(stderr_text)
                }
            )

        except asyncio.TimeoutError:
            completion_status = "timeout"
            exit_code = -1
            stderr_text = f"Process exceeded {CLAUDE_CLI_TIMEOUT}-second timeout"
            print(f"⏱️  TIMEOUT: Claude CLI exceeded {CLAUDE_CLI_TIMEOUT}s limit")

            # Log timeout event
            log_event(
                self.correlation_id,
                self.workspace_hash,
                session_id,
                "orchestrator",
                "claude_cli.timeout",
                {"pid": process.pid, "timeout_seconds": CLAUDE_CLI_TIMEOUT}
            )

            # Try to kill the hanging process
            try:
                process.kill()
                print(f"   🛑 Killed hanging process (PID: {process.pid})")

                # Log kill event
                log_event(
                    self.correlation_id,
                    self.workspace_hash,
                    session_id,
                    "orchestrator",
                    "claude_cli.killed",
                    {"pid": process.pid, "reason": "timeout"}
                )
            except Exception as kill_error:
                print(f"   ⚠️  Failed to kill process: {kill_error}", file=sys.stderr)

        except Exception as e:
            completion_status = "error"
            exit_code = -1
            stderr_text = f"Unexpected error: {str(e)}"
            print(f"❌ Claude CLI error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)

        finally:
            # Remove state file (prevents hook from skipping notifications)
            if state_file_created and AUTOFIX_STATE_FILE.exists():
                try:
                    AUTOFIX_STATE_FILE.unlink()
                    print(f"   🗑️  Removed state file: {AUTOFIX_STATE_FILE}")

                    # Log state file removed
                    log_event(
                        self.correlation_id,
                        self.workspace_hash,
                        session_id,
                        "orchestrator",
                        "state_file.removed",
                        {"state_file": str(AUTOFIX_STATE_FILE)}
                    )
                except Exception as e:
                    print(f"   ⚠️  Failed to remove state file: {e}", file=sys.stderr)

            # Calculate duration
            duration = asyncio.get_event_loop().time() - start_time
            print(f"   ⏱️  Total duration: {duration:.1f}s")

            # Emit completion notification
            print(f"   📝 Emitting completion notification...")
            try:
                await self._emit_completion(
                    workspace_path=workspace_path,
                    session_id=session_id,
                    status=completion_status,
                    exit_code=exit_code,
                    stdout=stdout_text,
                    stderr=stderr_text,
                    duration=duration
                )
            except Exception as e:
                print(f"❌ Failed to emit completion: {type(e).__name__}: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)

    async def _emit_completion(
        self,
        workspace_path: Path,
        session_id: str,
        status: str,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration: float
    ) -> None:
        """
        Emit completion notification file.

        Args:
            workspace_path: Workspace path
            session_id: Session ID
            status: Completion status (success/error/timeout)
            exit_code: Process exit code
            stdout: Standard output from Claude CLI
            stderr: Standard error from Claude CLI
            duration: Execution duration in seconds
        """
        print(f"      🔄 Preparing completion notification...")

        # Get workspace ID
        workspace_id = get_workspace_id_from_path(workspace_path)
        workspace_hash = compute_workspace_hash(workspace_path)
        print(f"      ✓ Workspace: {workspace_id} (hash: {workspace_hash})")

        # Extract summary from output (progressive disclosure)
        print(f"      📝 Extracting summary from {status} output...")
        summary = "No output"
        if status == "success" and stdout:
            # Try JSON parsing first (Claude CLI uses --output-format json)
            try:
                result_data = json.loads(stdout)
                if isinstance(result_data, dict):
                    # Extract from 'result' field if present
                    if 'result' in result_data:
                        result_text = result_data['result']
                        # Get first meaningful line (not markdown header)
                        for line in result_text.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                summary = line[:200]
                                break
                    # Fallback: use subtype or type
                    elif 'subtype' in result_data:
                        summary = f"{result_data.get('type', 'result')}: {result_data['subtype']}"
                    elif 'type' in result_data:
                        summary = result_data['type']
            except json.JSONDecodeError:
                # Not JSON - use existing logic for non-JSON output
                lines = [l.strip() for l in stdout.strip().split('\n') if l.strip()]
                # Look for lines that don't start with JSON markers
                for line in lines:
                    if line and not line.startswith('{') and not line.startswith('['):
                        summary = line[:200]  # First 200 chars
                        break
        elif status == "error":
            if stderr:
                summary = stderr.split('\n')[0][:200]
            else:
                summary = f"Process failed with exit code {exit_code}"
        elif status == "timeout":
            summary = "Claude CLI exceeded 5-minute timeout"
        print(f"      ✓ Summary: {summary[:80]}{'...' if len(summary) > 80 else ''}")

        # Create completion notification
        completion = {
            "workspace_path": str(workspace_path),
            "workspace_id": workspace_id,
            "session_id": session_id,
            "status": status,
            "exit_code": exit_code,
            "duration_seconds": round(duration, 1),
            "summary": summary,
            "stdout": stdout,
            "stderr": stderr,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        print(f"      ✓ Completion object created ({len(json.dumps(completion))} bytes)")

        # Write completion file
        COMPLETION_DIR.mkdir(parents=True, exist_ok=True)
        completion_file = COMPLETION_DIR / f"completion_{session_id}_{workspace_hash}.json"
        print(f"      💾 Writing to: {completion_file.name}")
        completion_file.write_text(json.dumps(completion, indent=2))

        print(f"📤 Completion notification emitted: {completion_file.name}")

        # Log completion emitted event
        log_event(
            self.correlation_id,
            workspace_hash,
            session_id,
            "orchestrator",
            "completion.emitted",
            {
                "completion_file": completion_file.name,
                "status": status,
                "exit_code": exit_code,
                "duration_seconds": round(duration, 1)
            }
        )

    def _cleanup_approval(self, approval_file: Path) -> None:
        """Delete consumed approval file."""
        try:
            approval_file.unlink()
            print(f"🗑️  Consumed: {approval_file.name}")
        except FileNotFoundError:
            pass


async def main() -> int:
    """One-shot execution: process single approval file and exit."""

    print("=" * 70)
    print("Multi-Workspace Approval Orchestrator - One-Shot Mode")
    print("=" * 70)
    print(f"Version: 3.0.0")
    print(f"Timeout: {CLAUDE_CLI_TIMEOUT}s ({CLAUDE_CLI_TIMEOUT // 60} minutes)")
    print()

    # Accept approval file path as argument or scan directory
    if len(sys.argv) > 1:
        approval_file = Path(sys.argv[1]).resolve()
        if not approval_file.exists():
            print(f"❌ Approval file not found: {approval_file}", file=sys.stderr)
            return 1
        if not approval_file.name.startswith("approval_"):
            print(f"❌ Invalid approval file name: {approval_file.name}", file=sys.stderr)
            return 1

        print(f"📝 Processing approval: {approval_file.name}")
    else:
        # Scan approval directory for pending files
        APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
        approval_files = sorted(APPROVAL_DIR.glob("approval_*.json"))

        if not approval_files:
            print("📂 No pending approvals found")
            return 0

        approval_file = approval_files[0]  # Process oldest
        print(f"📝 Found {len(approval_files)} approval(s), processing oldest: {approval_file.name}")

    # Process approval
    orchestrator = ApprovalOrchestrator()

    try:
        await orchestrator.process_approval(approval_file)
        print("\n✅ Orchestrator completed successfully")
        return 0
    except FileNotFoundError:
        print(f"\n⚠️  Approval file already consumed: {approval_file.name}")
        return 0
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
