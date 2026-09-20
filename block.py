# -----------------------------------------------------------------------------
# Role: Implements the HTML display block runtime and UI contract.
# File Name: block.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-01-20
# -----------------------------------------------------------------------------

from __future__ import annotations

from html import escape
from typing import Any

from bloxsmith_app.block_api import (
    BlockDefinition,
    BlockRuntimeResult,
    render_inspector_template,
    render_node_card_template,
    TEXT_HTML,
)


HTML_DISPLAY_WORKER_PREVIEW_LIMIT = 300


# Functional behavior:
# FB1 - Render the HTML display inspector with the latest received HTML payload and source label.
# FB2 - Preserve the allow-scripts display option in node state.
# FB3 - Capture received runtime HTML as a block-owned sink result without transforming it.
# FB4 - Escape captured HTML in inspector and modal templates so received markup is displayed as data.
# FB5 - Offer a modal action that opens the received HTML as a rendered browser preview.
class HtmlDisplayBlock(BlockDefinition):
    """Autonomous block implementation for `HtmlDisplayBlock`."""
    kind = "html_display"

    def execute_runtime(self, context: Any) -> BlockRuntimeResult:
        """Capture the received HTML payload as this sink block's runtime result.

        Args:
            context: Runtime context populated by centralized or ZeroMQ active execution.

        Returns:
            Successful runtime result with no outputs and the received HTML kept as
            `text/html` for node cards, inspectors, and modals.
        """

        message = self._runtime_message(context)
        messages = self._received_messages(context, message)
        accumulated_message = "\n\n".join(messages)
        node_id = str(getattr(context, "node_id", "") or self.kind)
        log = (
            f"[html-display] {node_id}: {len(accumulated_message)} HTML character(s) received."
            if accumulated_message
            else f"[html-display] {node_id}: no HTML input received."
        )
        return BlockRuntimeResult(
            status="success",
            outputs=[],
            logs=[log],
            last_message=accumulated_message,
            content_type=TEXT_HTML,
            worker_received=self._worker_preview(accumulated_message),
            metadata={
                "content_type": TEXT_HTML,
                "display_received_count": len(messages),
            },
        )

    def render_node_card(self, *, node: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Render the HTML display canvas card body from the block-owned template.

        Args:
            node: Serialized HTML display node being rendered.
            payload: Optional UI payload that may contain the latest HTML output.

        Returns:
            Block UI payload used by the generic canvas shell.
        """

        payload = payload or {}
        display_output = self._display_output(node=node, payload=payload)
        return render_node_card_template(
            block=self,
            node=node,
            node_classes=["html-display-node"],
            replacements={
                "title": node.get("title") or self.default_title(),
                "preview": self._truncate(str(display_output or "En attente de HTML"), 60),
                "mode": "scripts on" if self._allow_scripts(node) else "scripts off",
            },
        )

    def render_inspector_panel(self, *, node: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Render the HTML Display inspector from generic runtime UI payload.

        Args:
            node: Serialized HTML display node.
            payload: Optional UI payload containing runtime output previews.

        Returns:
            Block inspector payload with rendered HTML and context metadata.
        """

        payload = payload or {}
        display_output = self._display_output(node=node, payload=payload)
        template = (self.directory / "inspector_panel.html").read_text(encoding="utf-8")
        html = render_inspector_template(
            template=(
                template
                .replace("{{ display_source }}", escape(self._display_source(node=node, payload=payload)))
                .replace("{{ display_output }}", escape(str(display_output or "No output available yet.")))
                .replace("{{ allow_scripts_checked }}", "checked" if self._allow_scripts(node) else "")
            ),
            node={**node, "type": self.kind, "kind": self.kind},
            payload=payload,
            show_duplicate=False,
        )
        return {"html": html, "context": {"node_id": str(node.get("id") or ""), "full_panel": True}}

    def render_modal(self, *, node: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Render the full HTML Display output modal from block-owned HTML.

        Args:
            node: Serialized HTML display node selected by the user.
            payload: Generic UI payload containing runtime input/output previews.

        Returns:
            Block modal payload consumed by the shared modal host.
        """

        payload = payload or {}
        items = self._display_items(node=node, payload=payload)
        template = (self.directory / "block_modal.html").read_text(encoding="utf-8")
        html = (
            template.replace("{{ title }}", escape(str(node.get("title") or self.default_title())))
            .replace("{{ summary }}", escape(self._modal_summary(items)))
            .replace("{{ items_html }}", self._render_modal_items(items))
            .replace("{{ clipboard_text }}", escape(self._modal_clipboard_text(items)))
            .replace("{{ preview_html }}", escape(self._modal_preview_html(items)))
            .replace("{{ script_mode }}", "scripts on" if self._allow_scripts(node) else "scripts off")
            .replace("{{ allow_scripts }}", "true" if self._allow_scripts(node) else "false")
            .replace("{{ preview_disabled }}", "" if items else "disabled")
        )
        return {
            "html": html,
            "context": {
                "node_id": str(node.get("id") or ""),
                "item_count": len(items),
            },
        }

    def _truncate(self, value: str, max_length: int) -> str:
        """Return a compact one-line HTML preview for the canvas card."""

        text = str(value or "").replace("\n", " ").strip()
        return text if len(text) <= max_length else f"{text[: max_length - 1]}..."

    def _runtime_message(self, context: Any) -> str:
        """Return the ordered input payload received by the HTML display sink."""

        message = str(getattr(context, "input_message", "") or "")
        if message:
            return message
        values = getattr(context, "inputs", {}) or {}
        if not isinstance(values, dict):
            return ""
        resolved: list[str] = []
        seen: set[str] = set()
        for raw_value in values.values():
            value = str(raw_value or "")
            if not value or value in seen:
                continue
            resolved.append(value)
            seen.add(value)
        return "\n\n".join(resolved)

    def _received_messages(self, context: Any, message: str) -> list[str]:
        """Append this execution payload to previously captured active HTML messages."""

        previous = getattr(context, "previous_result", {}) or {}
        raw_previous = previous.get("_display_received_messages") if isinstance(previous, dict) else None
        messages = [str(item) for item in raw_previous if str(item)] if isinstance(raw_previous, list) else []
        if not messages and isinstance(previous, dict) and str(previous.get("last_message") or ""):
            messages = [str(previous.get("last_message") or "")]
        if message:
            messages.append(message)
        return messages

    def _worker_preview(self, value: str) -> str:
        """Return a bounded worker row preview without duplicating full HTML."""

        text = str(value or "")
        if len(text) <= HTML_DISPLAY_WORKER_PREVIEW_LIMIT:
            return text
        hidden = len(text) - HTML_DISPLAY_WORKER_PREVIEW_LIMIT
        return f"{text[:HTML_DISPLAY_WORKER_PREVIEW_LIMIT]}... ({hidden} caracteres masques)"

    def _allow_scripts(self, node: dict[str, Any]) -> bool:
        """Return whether the node allows script execution in HTML viewers."""

        config = node.get("config")
        return bool(config.get("allow_scripts")) if isinstance(config, dict) else False

    def _runtime_payload(self, payload: dict[str, Any], node: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return the generic runtime payload supplied by the editor."""

        runtime = payload.get("runtime")
        if isinstance(runtime, dict):
            return runtime
        node_runtime = node.get("runtimeUi") if isinstance(node, dict) else None
        return node_runtime if isinstance(node_runtime, dict) else {}

    def _display_output(self, *, node: dict[str, Any], payload: dict[str, Any]) -> str:
        """Resolve the latest HTML output from the runtime payload."""

        runtime = self._runtime_payload(payload, node)
        if runtime.get("latest_message"):
            return str(runtime.get("latest_message") or "")
        return str(node.get("output") or "")

    def _display_source(self, *, node: dict[str, Any], payload: dict[str, Any]) -> str:
        """Resolve a readable source label from generic runtime inputs."""

        runtime = self._runtime_payload(payload, node)
        inputs = runtime.get("received_inputs")
        if isinstance(inputs, list) and inputs:
            first = inputs[0] if isinstance(inputs[0], dict) else {}
            return str(first.get("label") or "")
        return ""

    def _display_items(self, *, node: dict[str, Any], payload: dict[str, Any]) -> list[dict[str, str]]:
        """Resolve all values that should be shown in the full output modal."""

        runtime = self._runtime_payload(payload, node)
        inputs = runtime.get("received_inputs")
        if isinstance(inputs, list) and inputs:
            return [
                {
                    "label": str(item.get("label") or "Received input"),
                    "target_label": str(item.get("target_label") or item.get("targetLabel") or node.get("title") or ""),
                    "content": str(item.get("content") or ""),
                }
                for item in inputs
                if isinstance(item, dict) and str(item.get("content") or "")
            ]

        latest = str(runtime.get("latest_message") or "")
        if latest:
            return [{"label": "Runtime", "target_label": str(node.get("title") or ""), "content": latest}]

        output = str(node.get("output") or "")
        if output:
            return [{"label": "Output received", "target_label": str(node.get("title") or ""), "content": output}]
        return []

    def _modal_summary(self, items: list[dict[str, str]]) -> str:
        """Return the modal summary sentence for the resolved output items."""

        if not items:
            return "No HTML content received for this block."
        suffix = "s" if len(items) > 1 else ""
        return f"{len(items)} HTML content{suffix} received."

    def _render_modal_items(self, items: list[dict[str, str]]) -> str:
        """Render HTML output cards for the modal body."""

        if not items:
            return '<div class="ports-editor-empty">Run the workflow or load a run to see the full content.</div>'
        cards: list[str] = []
        for index, item in enumerate(items):
            label = escape(item.get("label") or f"Source {index + 1}")
            target = escape(item.get("target_label") or "")
            content = escape(item.get("content") or "")
            cards.append(
                '<article class="display-output-card">'
                '<div class="display-output-card-header">'
                f"<span>{label}</span>"
                f"<span>{target}</span>"
                "</div>"
                f'<pre class="display-output-content">{content}</pre>'
                "</article>"
            )
        return "".join(cards)

    def _modal_clipboard_text(self, items: list[dict[str, str]]) -> str:
        """Build the text copied by the generic modal copy button."""

        return "\n\n---\n\n".join(f"{item.get('label') or 'Source'}\n{item.get('content') or ''}" for item in items)

    def _modal_preview_html(self, items: list[dict[str, str]]) -> str:
        """Build the raw HTML opened by the block-owned browser preview button."""

        return "\n\n".join(str(item.get("content") or "") for item in items if str(item.get("content") or ""))
