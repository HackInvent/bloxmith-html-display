#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Role: Verifies HTML display block behavior for the HTML display block.
# File Name: F5.10_html_display_block.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-02-26
# -----------------------------------------------------------------------------

"""F5.10 - Bloc Affichage HTML.

Le test connecte une source texte contenant du HTML à `html_display` et vérifie
que le bloc reçoit le HTML avec le content type attendu via son runtime autonome.
"""

# Test cases:
# - FB1/FB3 - Run text -> html_display and verify the block-owned runtime HTML result.
# - FB2 - Render the HTML display inspector and verify allow-scripts state is preserved.
# - FB2 - Render the HTML display modal from block-owned HTML and generic runtime payload.
# - FB4 - Render inspector and modal with escaped received markup so scripts cannot execute in block templates.
# - FB5 - Render the modal preview action and block-owned modal assets.
# - FB3 - Verify centralized and zeromq_active modes preserve received HTML for the frontend display viewer.

from ui_smoke_common import (
    create_run_api,
    data_edge,
    expect,
    graph_payload,
    http_json,
    isolated_server,
    text_node,
    wait_for_run_terminal,
)


def html_display_node() -> dict:
    return {
        "id": "html-display-1",
        "kind": "html_display",
        "title": "Affichage HTML",
        "position": {"x": 420, "y": 120},
        "inputs": [
            {"id": 1, "name": "html", "title": "HTML", "accepts": ["text/html", "message/*"], "multiplicity": "many"}
        ],
        "outputs": [],
        "config": {"allow_scripts": False},
    }


def main() -> None:
    html = (
        '<section><h1>Hello HTML</h1><img src="exports/images/example.png" alt="demo">'
        "<script>window.__html_display_test = true</script>"
        + ("<p>long html payload</p>" * 80)
        + "</section>"
    )
    with isolated_server() as server:
        rendered = http_json(
            server.base_url,
            "/api/blocks/html_display/inspector-panel",
            method="POST",
            payload={
                "node": {"id": "html-display-1", "kind": "html_display", "title": "HTML", "config": {"allow_scripts": True}},
                "runtime": {
                    "received_inputs": [
                        {
                            "label": "Text.out",
                            "target_label": "HTML.html",
                            "content": html,
                        }
                    ],
                    "latest_message": html,
                },
            },
        )
        inspector = str(rendered.get("html") or "")
        expect("allow" in inspector.lower() and "checked" in inspector, "L'inspecteur html_display doit préserver allow-scripts.")
        expect("<script>" not in inspector and "&lt;script&gt;" in inspector, "L'inspecteur html_display doit afficher le HTML comme source échappée.")

        modal = http_json(
            server.base_url,
            "/api/blocks/html_display/modal",
            method="POST",
            payload={
                "node": {"id": "html-display-1", "kind": "html_display", "title": "HTML", "config": {"allow_scripts": True}},
                "runtime": {
                    "received_inputs": [
                        {
                            "label": "Text.out",
                            "target_label": "HTML.html",
                            "content": html,
                        }
                    ],
                    "latest_message": html,
                },
            },
        )
        modal_html = str(modal.get("html") or "")
        modal_assets = modal.get("assets") or []
        expect("Hello HTML" in modal_html and "data-close-block-modal" in modal_html, "Le modal html_display doit être rendu par le bloc.")
        expect('data-block-runtime-refresh="autonomous"' in modal_html, "Le modal html_display doit gérer son refresh runtime.")
        expect("data-block-apply" in modal_html, "Le modal html_display doit exposer le bouton Appliquer.")
        expect("<script>" not in modal_html and "&lt;script&gt;" in modal_html, "Le modal html_display doit afficher le HTML comme source échappée.")
        expect("data-html-display-open-preview" in modal_html, "Le modal html_display doit proposer la visualisation HTML.")
        expect("data-html-display-preview-source" in modal_html, "Le modal html_display doit exposer la source de preview.")
        expect(
            {"kind": "css", "path": "assets/css/block_modal.css"} in modal_assets,
            "Le modal html_display doit déclarer son CSS block-owned.",
        )
        expect(
            {"kind": "js", "path": "assets/js/block_modal.js"} in modal_assets,
            "Le modal html_display doit déclarer son JS block-owned.",
        )

        document = graph_payload(
            "F5 HTML Display",
            [
                text_node("text-1", "HTML source", html, 80, 120),
                html_display_node(),
            ],
            [data_edge("edge-text-html-display", "text-1", 1, "html-display-1", 1)],
        )
        for runtime_mode in ("centralized", "zeromq_active"):
            created = create_run_api(server, document, runtime_mode=runtime_mode)
            run = wait_for_run_terminal(server, str(created.get("run_id") or ""))

            expect(run.get("status") == "success", f"Le run html_display doit réussir en {runtime_mode}.")
            result = run.get("results", {}).get("html-display-1", {})
            expect("virtual_display" not in result, f"html_display ne doit pas utiliser virtual_display en {runtime_mode}.")
            expect(result.get("content_type") == "text/html", f"html_display doit exposer text/html en {runtime_mode}.")
            expect("<img" in str(result.get("last_message") or ""), f"Le HTML reçu ne contient pas l'image en {runtime_mode}.")
            worker_received = str(run.get("worker_rows", {}).get("html-display-1", {}).get("received") or "")
            expect("Hello HTML" in worker_received, f"Worker row HTML non alimentée en {runtime_mode}.")
            expect(len(worker_received) < len(html), f"Worker row HTML doit rester une preview en {runtime_mode}.")
            expect("_display_received_messages" not in result, f"html_display ne doit pas dupliquer les gros textes en metadata en {runtime_mode}.")
            expect(result.get("display_received_count") == 1, f"html_display doit exposer un compteur de messages en {runtime_mode}.")
    print("[ok] F5.10_html_display_block")


if __name__ == "__main__":
    main()
