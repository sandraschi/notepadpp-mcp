"""SEP-1577 agentic workflow: FastMCP 3.1 ctx.sample_step with Notepad++ portmanteau tools."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import Context, FastMCP

logger = logging.getLogger(__name__)


def _ok(**kwargs: Any) -> dict[str, Any]:
    return {
        "success": True,
        "operation": kwargs.get("operation", "agentic_notepad_workflow"),
        "summary": kwargs.get("summary", "Completed"),
        "result": kwargs.get("result", {}),
        "next_steps": kwargs.get("next_steps", []),
    }


def _err(**kwargs: Any) -> dict[str, Any]:
    return {
        "success": False,
        "error": kwargs.get("error", "unknown"),
        "error_code": kwargs.get("error_code", "ERROR"),
        "message": kwargs.get("message", ""),
        "recovery_options": kwargs.get("recovery_options", []),
    }


def register_agentic_notepad_workflow(app: FastMCP) -> None:
    """Register agentic_notepad_workflow on the FastMCP app (after other tools)."""

    @app.tool()
    async def agentic_notepad_workflow(
        workflow_prompt: str,
        available_tools: list[str],
        max_iterations: int = 5,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """AGENTIC_NOTEPAD_WORKFLOW — Multi-step Notepad++ automation via sampling with tools (FastMCP 3.1).

        Uses ctx.sample_step in a loop: the model selects tool calls, tools run, results return until
        the model answers with text or max_iterations is reached. Requires a reachable sampling endpoint
        (server-side Ollama via NOTEPADPP_SAMPLING_* or client LLM with sampling).

        Args:
            workflow_prompt: What to accomplish in natural language.
            available_tools: MCP tool names to allow (e.g. file_ops, text_ops, tab_ops, linting_ops).
            max_iterations: Maximum sample_step rounds.

        Returns:
            Structured dict with final_output, iterations, executed_tools, or error.
        """
        try:
            if not workflow_prompt.strip():
                return _err(
                    error="empty_prompt",
                    error_code="MISSING_PROMPT",
                    message="workflow_prompt is required",
                    recovery_options=["Provide a clear goal for Notepad++ automation"],
                )
            if not available_tools:
                return _err(
                    error="no_tools",
                    error_code="EMPTY_TOOLS",
                    message="available_tools cannot be empty",
                    recovery_options=["Include tool names such as file_ops, text_ops, tab_ops"],
                )
            if ctx is None or not hasattr(ctx, "sample_step"):
                return _err(
                    error="sampling_unavailable",
                    error_code="NO_CONTEXT",
                    message="FastMCP Context with sample_step not available",
                    recovery_options=[
                        "Use FastMCP 3.1+ with sampling configured",
                        "For HTTP bridge, ensure client supports tools+sampling",
                    ],
                )

            all_tools = await app.list_tools()
            name_to_tool = {t.name: t for t in all_tools if hasattr(t, "name")}
            tools_for_sampling = [name_to_tool[n] for n in available_tools if n in name_to_tool]
            missing = [n for n in available_tools if n not in name_to_tool]
            if missing:
                logger.warning("agentic_notepad_workflow: unknown tools: %s", missing)
            if not tools_for_sampling:
                return _err(
                    error="no_matching_tools",
                    error_code="TOOLS_NOT_FOUND",
                    message=f"No registered tools matched. Known: {list(name_to_tool.keys())}",
                    recovery_options=["Use names from list_tools / Tools Hub"],
                )

            system_prompt = (
                "You automate Notepad++ on Windows via MCP tools. "
                "Call tools to achieve the user's goal, then summarize results and next steps. Be concise."
            )
            messages: list = [{"role": "user", "content": workflow_prompt}]
            executed: list[str] = []
            iterations = 0
            step = None

            while iterations < max_iterations:
                iterations += 1
                logger.info("agentic_notepad_workflow step %s/%s", iterations, max_iterations)
                step = await ctx.sample_step(
                    messages,
                    system_prompt=system_prompt,
                    tools=tools_for_sampling,
                    execute_tools=True,
                    max_tokens=4096,
                )
                if hasattr(step, "history") and step.history:
                    messages = list(step.history)
                if hasattr(step, "tool_calls") and step.tool_calls:
                    for tc in step.tool_calls:
                        name = getattr(tc, "name", None) or getattr(tc, "tool_name", str(tc))
                        if name:
                            executed.append(str(name))
                is_tool = getattr(step, "is_tool_use", True)
                if not is_tool:
                    final = getattr(step, "text", "") or ""
                    return _ok(
                        operation="agentic_notepad_workflow",
                        summary=f"Completed in {iterations} round(s).",
                        result={
                            "final_output": final,
                            "iterations": iterations,
                            "executed_tools": list(dict.fromkeys(executed)),
                        },
                        next_steps=[
                            "Refine prompt or call file_ops/status_ops if something failed."
                        ],
                    )

            return _ok(
                operation="agentic_notepad_workflow",
                summary=f"Stopped after {max_iterations} iterations (limit).",
                result={
                    "final_output": getattr(step, "text", "") if step else "(no step)",
                    "iterations": iterations,
                    "executed_tools": list(dict.fromkeys(executed)),
                },
                next_steps=["Increase max_iterations or narrow the goal."],
            )
        except Exception as e:
            logger.exception("agentic_notepad_workflow failed")
            return _err(
                error=str(e),
                error_code="WORKFLOW_ERROR",
                message=str(e),
                recovery_options=["Check Notepad++ is running", "Verify sampling and tool names"],
            )
