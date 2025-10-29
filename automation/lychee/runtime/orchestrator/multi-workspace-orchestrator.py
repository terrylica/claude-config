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
SUMMARIES_DIR = STATE_DIR / "summaries"  # Phase 4 - v4.0.0
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


def emit_progress(
    workspace_id: str,
    session_id: str,
    workflow_id: str,
    status: str,
    stage: str,
    progress_percent: int,
    message: str
) -> None:
    """
    Emit progress update to state/progress/ directory.

    Args:
        workspace_id: Workspace hash
        session_id: Session UUID
        workflow_id: Workflow identifier
        status: running, completed, or error
        stage: starting, rendering, executing, waiting, or completed
        progress_percent: 0-100 completion percentage
        message: Human-readable progress message (max 200 chars)

    Raises:
        All errors propagate (fail-fast)
    """
    progress_dir = STATE_DIR / "progress"
    progress_file = progress_dir / f"{workspace_id}_{session_id}_{workflow_id}.json"

    progress_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "workflow_id": workflow_id,
        "status": status,
        "stage": stage,
        "progress_percent": progress_percent,
        "message": message[:200],  # Enforce max length
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Write atomically (write to temp file, then rename)
    temp_file = progress_file.with_suffix(".tmp")
    with open(temp_file, "w") as f:
        json.dump(progress_data, f, indent=2)
    temp_file.rename(progress_file)

    print(f"   📊 Progress: {stage} ({progress_percent}%) - {message[:50]}")


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


class WorkflowOrchestrator:
    """
    Processes workflow selections and executes multi-workflow pipelines (Phase 4 - v4.0.0).

    Loads workflow registry, renders Jinja2 templates, invokes Claude CLI,
    emits execution results.
    """

    def __init__(self):
        self.correlation_id = None
        self.workspace_hash = None
        self.session_id = None
        self.registry = None

    async def process_selection(self, selection_file: Path) -> None:
        """
        Process WorkflowSelection file and execute workflows.

        Args:
            selection_file: Path to WorkflowSelection JSON

        Raises:
            All errors propagate (fail-fast)
        """
        try:
            # Read and validate selection
            selection = self._read_selection(selection_file)
            self.session_id = selection["session_id"]
            self.correlation_id = selection.get("correlation_id", os.environ.get("CORRELATION_ID", "unknown"))

            # Load registry if not already loaded
            if workflow_registry is None:
                raise RuntimeError("Workflow registry not loaded - call load_workflow_registry() first")
            self.registry = workflow_registry

            # Validate workspace
            workspace_path = validate_workspace_path(Path(selection["workspace_path"]))
            self.workspace_hash = compute_workspace_hash(workspace_path)

            # Log orchestrator started
            log_event(
                self.correlation_id,
                self.workspace_hash,
                self.session_id,
                "orchestrator",
                "selection.received",
                {"selection_file": selection_file.name, "workflow_ids": selection["workflows"]}
            )

            # Get workflows to execute
            workflow_ids = selection["workflows"]
            print(f"🚀 Processing {len(workflow_ids)} workflow(s): {workflow_ids}")

            # Resolve dependencies (Phase 4: no-op, returns input order)
            ordered_workflow_ids = resolve_workflow_dependencies(workflow_ids, self.registry)

            # Build template context
            # Priority: Use summary_data from selection if available, otherwise load from file
            if "summary_data" in selection:
                summary = selection["summary_data"]
                print(f"   ℹ️  Using summary data from selection file")
            else:
                # Fallback: Load SessionSummary from file
                summary = self._read_session_summary(self.session_id, self.workspace_hash)
                print(f"   ℹ️  Loaded summary from file")

            context = self._build_template_context(summary, workspace_path)

            # Execute workflows sequentially
            for workflow_id in ordered_workflow_ids:
                print(f"\n📋 Executing workflow: {workflow_id}")
                await self._execute_workflow(workflow_id, context, workspace_path)

            # Log orchestrator completed
            log_event(
                self.correlation_id,
                self.workspace_hash,
                self.session_id,
                "orchestrator",
                "orchestrator.completed",
                {"workflow_count": len(workflow_ids)}
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
            # Always cleanup consumed selection
            self._cleanup_selection(selection_file)

    async def _execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any],
        workspace_path: Path
    ) -> None:
        """
        Execute single workflow.

        Args:
            workflow_id: Workflow identifier
            context: Template rendering context
            workspace_path: Validated workspace path

        Raises:
            All errors propagate (fail-fast)
        """
        start_time = asyncio.get_event_loop().time()

        # Get workflow from registry
        if workflow_id not in self.registry["workflows"]:
            raise ValueError(f"Workflow not found in registry: {workflow_id}")

        workflow = self.registry["workflows"][workflow_id]
        workflow_name = workflow["name"]
        print(f"   📝 Workflow: {workflow['icon']} {workflow_name}")

        # Log workflow started
        log_event(
            self.correlation_id,
            self.workspace_hash,
            self.session_id,
            "orchestrator",
            "workflow.started",
            {"workflow_id": workflow_id, "workflow_name": workflow_name}
        )

        # Emit progress: starting
        emit_progress(
            workspace_id=self.workspace_hash,
            session_id=self.session_id,
            workflow_id=workflow_id,
            status="running",
            stage="starting",
            progress_percent=0,
            message=f"Starting workflow: {workflow_name}"
        )

        # Create state file to prevent feedback loop (headless session won't trigger new workflow menu)
        state_file_created = False
        try:
            AUTOFIX_STATE_FILE.write_text(json.dumps({
                "session_id": self.session_id,
                "workspace_path": str(workspace_path),
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "orchestrator_pid": os.getpid(),
                "correlation_id": self.correlation_id
            }, indent=2))
            state_file_created = True
            print(f"   📝 Created state file to prevent feedback loop: {AUTOFIX_STATE_FILE}")

            # Log state file created
            log_event(
                self.correlation_id,
                self.workspace_hash,
                self.session_id,
                "orchestrator",
                "state_file.created",
                {"state_file": str(AUTOFIX_STATE_FILE), "workflow_id": workflow_id}
            )
        except Exception as e:
            print(f"   ⚠️  Failed to create state file: {e}", file=sys.stderr)

        # Render Jinja2 template
        try:
            prompt = render_workflow_prompt(workflow, context)
            print(f"   ✅ Template rendered ({len(prompt)} chars)")

            # Log template rendered
            log_event(
                self.correlation_id,
                self.workspace_hash,
                self.session_id,
                "orchestrator",
                "workflow.template_rendered",
                {"workflow_id": workflow_id, "template_length": len(prompt)}
            )

            # Emit progress: rendering
            emit_progress(
                workspace_id=self.workspace_hash,
                session_id=self.session_id,
                workflow_id=workflow_id,
                status="running",
                stage="rendering",
                progress_percent=25,
                message=f"Template rendered ({len(prompt)} chars)"
            )

        except TemplateError as e:
            print(f"   ❌ Template rendering failed: {e}", file=sys.stderr)
            # Emit failed execution result
            await self._emit_execution_result(
                workspace_path=workspace_path,
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                status="error",
                exit_code=-1,
                stdout="",
                stderr=f"Template rendering failed: {str(e)}",
                duration=0.0,
                workflow_metadata=workflow
            )
            raise

        # Invoke Claude CLI
        completion_status = "success"
        exit_code = 0
        stdout_text = ""
        stderr_text = ""
        headless_session_id = None

        try:
            print(f"   🔧 Starting Claude CLI...")
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
                self.session_id,
                "orchestrator",
                "claude_cli.started",
                {"pid": process.pid, "workflow_id": workflow_id, "timeout_seconds": CLAUDE_CLI_TIMEOUT}
            )

            # Emit progress: executing
            emit_progress(
                workspace_id=self.workspace_hash,
                session_id=self.session_id,
                workflow_id=workflow_id,
                status="running",
                stage="executing",
                progress_percent=50,
                message=f"Claude CLI executing (PID: {process.pid})"
            )

            # Wait for completion (no heartbeat for workflow execution - keep it simple)
            print(f"   ⏳ Waiting for completion (timeout: {CLAUDE_CLI_TIMEOUT}s)...")

            # Emit progress: waiting
            emit_progress(
                workspace_id=self.workspace_hash,
                session_id=self.session_id,
                workflow_id=workflow_id,
                status="running",
                stage="waiting",
                progress_percent=75,
                message=f"Waiting for Claude CLI completion (timeout: {CLAUDE_CLI_TIMEOUT}s)"
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=CLAUDE_CLI_TIMEOUT
                )
            except asyncio.TimeoutError:
                completion_status = "timeout"
                exit_code = -1
                stderr_text = f"Process exceeded {CLAUDE_CLI_TIMEOUT}-second timeout"
                print(f"   ⏱️  TIMEOUT: Exceeded {CLAUDE_CLI_TIMEOUT}s limit")

                # Kill hanging process
                try:
                    process.kill()
                    print(f"   🛑 Killed hanging process (PID: {process.pid})")
                except Exception as kill_error:
                    print(f"   ⚠️  Failed to kill process: {kill_error}", file=sys.stderr)

                raise

            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
            stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
            exit_code = process.returncode

            # Extract headless session ID from JSON output
            headless_session_id = None
            try:
                if stdout_text:
                    result_json = json.loads(stdout_text)
                    headless_session_id = result_json.get("session_id")
                    if headless_session_id:
                        print(f"   📋 Headless session ID: {headless_session_id}")
            except json.JSONDecodeError:
                print(f"   ⚠️  Could not parse JSON output to extract headless session ID")

            print(f"   ✓ Process completed")
            print(f"   📊 Exit code: {exit_code}")
            print(f"   📊 Stdout length: {len(stdout_text)} chars")
            print(f"   📊 Stderr length: {len(stderr_text)} chars")

            if exit_code != 0:
                completion_status = "error"
                print(f"   ❌ Claude CLI failed with exit code {exit_code}")
                if stderr_text:
                    print(f"   Error preview: {stderr_text[:200]}")
            else:
                print(f"   ✅ Claude CLI completed successfully")
                if stdout_text:
                    print(f"   Output preview: {stdout_text[:200]}")

        except Exception as e:
            completion_status = "error"
            exit_code = -1
            stderr_text = f"Unexpected error: {str(e)}"
            print(f"   ❌ Claude CLI error: {type(e).__name__}: {e}")

        finally:
            # Calculate duration
            duration = asyncio.get_event_loop().time() - start_time
            print(f"   ⏱️  Duration: {duration:.1f}s")

            # Emit execution result
            await self._emit_execution_result(
                workspace_path=workspace_path,
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                status=completion_status,
                exit_code=exit_code,
                stdout=stdout_text,
                stderr=stderr_text,
                duration=duration,
                workflow_metadata=workflow,
                headless_session_id=headless_session_id
            )

            # Log workflow completed
            log_event(
                self.correlation_id,
                self.workspace_hash,
                self.session_id,
                "orchestrator",
                "workflow.completed",
                {
                    "workflow_id": workflow_id,
                    "status": completion_status,
                    "exit_code": exit_code,
                    "duration_seconds": round(duration, 1)
                }
            )

            # Emit progress: completed
            emit_progress(
                workspace_id=self.workspace_hash,
                session_id=self.session_id,
                workflow_id=workflow_id,
                status=completion_status,
                stage="completed",
                progress_percent=100,
                message=f"Workflow completed: {completion_status} (exit {exit_code})"
            )

            # Remove state file (allow future workflows to trigger)
            if state_file_created and AUTOFIX_STATE_FILE.exists():
                try:
                    AUTOFIX_STATE_FILE.unlink()
                    print(f"   🗑️  Removed state file: {AUTOFIX_STATE_FILE}")

                    # Log state file removed
                    log_event(
                        self.correlation_id,
                        self.workspace_hash,
                        self.session_id,
                        "orchestrator",
                        "state_file.removed",
                        {"state_file": str(AUTOFIX_STATE_FILE), "workflow_id": workflow_id}
                    )
                except Exception as e:
                    print(f"   ⚠️  Failed to remove state file: {e}", file=sys.stderr)

    async def _emit_execution_result(
        self,
        workspace_path: Path,
        workflow_id: str,
        workflow_name: str,
        status: str,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration: float,
        workflow_metadata: Dict[str, Any],
        headless_session_id: Optional[str] = None
    ) -> None:
        """
        Emit WorkflowExecution result file.

        Args:
            workspace_path: Workspace path
            workflow_id: Workflow identifier
            workflow_name: Workflow display name
            status: Execution status (success/error/timeout)
            exit_code: Claude CLI exit code
            stdout: Standard output
            stderr: Standard error
            duration: Execution duration in seconds
            workflow_metadata: Workflow manifest data
            headless_session_id: Session ID from headless Claude CLI execution

        Raises:
            All errors propagate (fail-fast)
        """
        # Create executions directory
        EXECUTIONS_DIR.mkdir(parents=True, exist_ok=True)

        # Generate execution file
        execution_file = EXECUTIONS_DIR / f"execution_{self.session_id}_{self.workspace_hash}_{workflow_id}.json"

        execution_data = {
            "correlation_id": self.correlation_id,
            "workspace_path": str(workspace_path),
            "workspace_id": self.workspace_hash,
            "session_id": self.session_id,
            "headless_session_id": headless_session_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "status": status,
            "exit_code": exit_code,
            "duration_seconds": round(duration, 1),
            "stdout": stdout,
            "stderr": stderr,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "estimated_duration": workflow_metadata.get("estimated_duration"),
                "risk_level": workflow_metadata.get("risk_level"),
                "category": workflow_metadata.get("category"),
                "icon": workflow_metadata.get("icon")
            }
        }

        execution_file.write_text(json.dumps(execution_data, indent=2))
        print(f"   📄 Execution result written: {execution_file.name}")

        # Log execution created
        log_event(
            self.correlation_id,
            self.workspace_hash,
            self.session_id,
            "orchestrator",
            "execution.created",
            {"execution_file": execution_file.name, "workflow_id": workflow_id, "status": status}
        )

    def _read_selection(self, selection_file: Path) -> Dict[str, Any]:
        """Read and validate WorkflowSelection file."""
        with selection_file.open() as f:
            selection = json.load(f)

        # Validate required fields
        required = ["workspace_path", "workspace_id", "session_id", "workflows", "timestamp"]
        missing = [f for f in required if f not in selection]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return selection

    def _read_session_summary(self, session_id: str, workspace_hash: str) -> Dict[str, Any]:
        """
        Read SessionSummary file for template context.

        Args:
            session_id: Session identifier
            workspace_hash: Workspace hash

        Returns:
            SessionSummary data

        Raises:
            FileNotFoundError: Summary file not found
        """
        summary_file = SUMMARIES_DIR / f"summary_{session_id}_{workspace_hash}.json"

        if not summary_file.exists():
            raise FileNotFoundError(
                f"SessionSummary not found: {summary_file}\n"
                f"Summary may have been consumed by bot.\n"
                f"Workaround: Bot should include summary_data in selection file."
            )

        with open(summary_file) as f:
            return json.load(f)

    def _build_template_context(
        self,
        summary: Dict[str, Any],
        workspace_path: Path
    ) -> Dict[str, Any]:
        """
        Build Jinja2 template context from SessionSummary.

        Args:
            summary: SessionSummary data
            workspace_path: Workspace path

        Returns:
            Template context dictionary
        """
        context = {
            "workspace_path": str(workspace_path),
            "session_id": summary.get("session_id"),
            "correlation_id": summary.get("correlation_id"),
            "git_status": summary.get("git_status", {}),
            "lychee_status": summary.get("lychee_status", {})
        }

        print(f"   🔧 Built template context:")
        print(f"      workspace: {context['workspace_path']}")
        print(f"      session: {context['session_id']}")
        print(f"      git_branch: {context['git_status'].get('branch', 'unknown')}")
        print(f"      lychee_errors: {context['lychee_status'].get('error_count', 0)}")

        return context

    def _cleanup_selection(self, selection_file: Path) -> None:
        """Delete consumed selection file."""
        try:
            selection_file.unlink()
            print(f"🗑️  Consumed: {selection_file.name}")
        except FileNotFoundError:
            pass


async def main() -> int:
    """
    One-shot execution: process selection or approval file and exit.

    Dual-mode:
    - v4: Process WorkflowSelection files (selections/)
    - v3: Process Approval files (approvals/) - backward compatibility
    """
    global workflow_registry

    print("=" * 70)
    print("Multi-Workspace Workflow Orchestrator - One-Shot Mode")
    print("=" * 70)
    print(f"Version: 4.0.0")
    print(f"Timeout: {CLAUDE_CLI_TIMEOUT}s ({CLAUDE_CLI_TIMEOUT // 60} minutes)")
    print()

    # Phase 4: Load workflow registry
    print("📋 Loading workflow registry...")
    try:
        workflow_registry = load_workflow_registry()
    except Exception as e:
        print(f"❌ Failed to load workflow registry: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"   Registry path: {WORKFLOWS_REGISTRY}", file=sys.stderr)
        return 1

    # Parse CLI arguments - accept file path
    if len(sys.argv) < 2:
        print("Usage: orchestrator.py <selection-file-or-approval-file>", file=sys.stderr)
        print("  Examples:", file=sys.stderr)
        print(f"    {sys.argv[0]} state/selections/selection_*.json", file=sys.stderr)
        print(f"    {sys.argv[0]} state/approvals/approval_*.json", file=sys.stderr)
        return 1

    input_file = Path(sys.argv[1]).resolve()
    if not input_file.exists():
        print(f"❌ File not found: {input_file}", file=sys.stderr)
        return 1

    # Route based on file type (dual-mode)
    if "selection_" in input_file.name:
        # v4: Process WorkflowSelection
        print(f"📝 Processing selection: {input_file.name}")
        orchestrator = WorkflowOrchestrator()

        try:
            await orchestrator.process_selection(input_file)
            print("\n✅ Orchestrator completed successfully")
            return 0
        except FileNotFoundError as e:
            print(f"\n⚠️  {e}")
            return 1
        except Exception as e:
            print(f"\n❌ Fatal error: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return 1

    elif "approval_" in input_file.name:
        # v3: Process Approval (backward compatibility)
        print(f"📝 Processing approval (v3 backward compat): {input_file.name}")
        orchestrator = ApprovalOrchestrator()

        try:
            await orchestrator.process_approval(input_file)
            print("\n✅ Orchestrator completed successfully")
            return 0
        except FileNotFoundError:
            print(f"\n⚠️  Approval file already consumed: {input_file.name}")
            return 0
        except Exception as e:
            print(f"\n❌ Fatal error: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return 1

    else:
        print(f"❌ Unknown file type: {input_file.name}", file=sys.stderr)
        print("   Expected: selection_*.json or approval_*.json", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
