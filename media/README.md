# HTML DISPLAY artwork

This image is a concept illustration of the `html_display` BloxSmith block.
The implemented function is: Displays incoming HTML content as a rendered preview.

- `cover.png`: selected original square PNG, copied byte for byte.
- `thumbnail.webp`: 320 × 320 WebP export for the README and catalog cards.
- Accent: cyan.
- Geometry reference: the scanner pilot cover. It is a visual reference only;
  its block-specific content was replaced.
- Creation: built-in image generation tool, 2026-09-28.
- License: [Apache-2.0](../LICENSE), like the rest of this block repository.

The image is not a Studio screenshot or a description of additional controls.
The artwork is documentation; its presence does not register it automatically
with Studio or the website. The block version and runtime contract are unchanged.

Export command (ImageMagick):

```sh
convert media/cover.png -thumbnail 320x320 -strip -quality 88 -define webp:method=6 media/thumbnail.webp
```

## Exact generation prompt

```text
Use case: stylized-concept.
Asset type: one square BloxSmith block cover illustration, to be read as a small catalog thumbnail.
Input image: the scanner pilot cover is a STYLE AND GEOMETRY REFERENCE ONLY. Use its centered graphite and steel industrial cube, exact front/top/right three-quarter perspective, reinforced corners, neat vents and ports, plain near-white background, subtle grounded shadow, upper-left light, scale and generous margins. Replace every subject-specific icon, display and accent from the reference; create a new original cover for html_display.
Primary request: visualize the real software block role accurately: Displays incoming HTML content as a rendered preview.
Main roof symbol: one large angle-bracket HTML symbol.
Front panel: a prominent upper title plate, and directly below it an incoming HTML source card points to a single browser preview window. Keep the concept legible at 320 pixels. Only a few large functional details; no microtext.
Color palette: one dominant restrained cyan accent, otherwise charcoal housing and brushed steel structural edges. The palette identifies a family but the symbols must distinguish the block without color.
Style/medium: polished, crisp industrial pixel-art product illustration with stepped edges and deliberate pixel clusters. Restrained glow, tactile surfaces, no photorealistic rendering.
Composition: one isolated complete near-cubical module on a 1:1 square canvas, about 84 percent of frame, no crop, no extra scene or props; match the pilot's geometry and consistent clean framing.
Text (verbatim): "HTML DISPLAY" exactly once in bold white uppercase pixel lettering on the front title plate. This is the ONLY writing in the picture. Spell it exactly; never add a subtitle, version, badge, copied text, fake small labels, watermark or slogan. The README carries the full technical name.
Accuracy constraints: website hosting, editing HTML, publishing pages, OCR. The picture should communicate function through simple symbols and one primary flow. Do not copy the pilot's icon, title, faders, waveform, code screen or scanning page unless actually relevant. No cats, people, desks, mascots, official third-party logos, detached modules or floating objects.
```
