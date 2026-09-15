# Directional Dilate 1.0.0

Class / gizmo name: `DRG_DirectionalDilate`

## Controls

- **Size** — positive values dilate/grow light pixels; negative values erode/shrink them.
- **Direction** — Both, Horizontal, Vertical.
- **Channels** — choose all channels or any channel set supported by Nuke.
- **Filter** — box, triangle, quadratic or gaussian through FilterErode.
- **Mix** — blend between original and processed result.

## Implementation

The gizmo uses a single internal `FilterErode` node because its size control supports width and height independently. The internal sign is inverted so the public Size control follows the familiar Dilate convention: positive grows light pixels. Horizontal feeds Size only to X; Vertical only to Y; Both feeds both axes.
