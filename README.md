# HTML Display Block

<!-- block-metadata:start -->
[![Block version: unversioned](https://img.shields.io/badge/block-unversioned-lightgrey)](model.json)
[![BloxSmith compatibility: 1.0.9](https://img.shields.io/badge/BloxSmith-1.0.9-brightgreen)](compatibility.json)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Verified BloxSmith versions: **1.0.9** (bundled-block tests; see [test evidence](compatibility.json)).
<!-- block-metadata:end -->


## Role

`html_display` is a UI sink for rendering or previewing HTML payloads produced by upstream blocks.

## Files

- `block.py`: node card, inspector, and modal rendering plus display option wiring.
- `model.json`: HTML input and `allow_scripts` config.
- `inspector_panel.html`: HTML display inspector markup.
- `node_card.html`: block-owned canvas card body.
- `block_modal.html`: block-owned full HTML output modal.
- `assets/css/block_modal.css`: larger modal layout for reading long HTML payloads.
- `assets/js/block_modal.js`: modal action that opens the received HTML in a browser tab.

## Ports

- Inputs:
  - `html` (`id: 1`): optional HTML input; accepts `text/html`, `message/*`, and `application/json`.

The block has no outputs.

## Configuration

- `allow_scripts`: preserves the script-rendering preference in node state. The current inspector and modal previews escape captured HTML and do not execute received markup.

## Runtime Behavior

`execute_runtime()` is owned by this block and is used in both centralized and `zeromq_active` modes. It captures received payloads, appends repeated active messages into the node `last_message`, marks the content as `text/html`, and emits no outputs. The full HTML is kept in the node runtime result only; worker row previews are bounded and metadata stores counts instead of duplicating the full HTML. The orchestrator only schedules the block and persists the generic runtime result.

## UI Behavior

`render_node_card()`, `render_inspector_panel()`, and `render_modal()` read the generic `runtime` UI payload supplied by the editor. The inspector displays the latest HTML payload as escaped source and reflects the script permission checkbox state. Card and inspector payloads receive bounded previews only, while the modal can receive the complete runtime payload. The `allow_scripts` change is kept pending while edited and is persisted through the GraphController only when the user clicks **Apply**. The full modal lists the received HTML sources as escaped source, uses a wider reading layout, and exposes a **Preview HTML** action that opens the raw received HTML in a new browser tab.

## Editor Display

The canvas card is rendered by this block through `node_card.html`. The full output modal is rendered through `block_modal.html`. The shared editor shell keeps ports, dragging, status, graph links, and modal hosting generic.

## Modal

`block_modal.html` is owned by this block and declares `data-block-runtime-refresh="autonomous"` so runtime polling does not replace the open HTML viewer. It shows the received HTML output and also exposes a generic editable title field. Modal title edits stay pending until the user clicks **Apply**. The modal preview button is implemented in `assets/js/block_modal.js` and renders the received HTML from a Blob URL; when `allow_scripts` is false, the generated preview document injects a restrictive CSP to prevent script execution.

## Maintenance Notes

Do not duplicate HTML escaping, runtime sink behavior, or rendering policy in the orchestrator. Keep UI-facing options documented here and implemented through the block-owned templates and generic frontend shell.

## Compatibility policy

[compatibility.json](compatibility.json) records HackInvent's verified BloxSmith versions and test evidence. Only the versions listed above have been verified, using the block-owned suites in a **bundled-block test installation**. This is not a certification of managed-package installation, every browser/OS, or live provider availability. Other framework versions are unverified, not necessarily incompatible.

The block-version badge follows `model.json`, not a published Git tag. `unversioned` means that no block release version is declared; no number is inferred from the framework version. The framework still uses `model.json` for its runtime/install contract; the tester-owned JSON does not replace it. Official integration tests run in the private `bloxmith-blocs` workspace. Test helpers and the proprietary framework are not bundled in this public block repository.
