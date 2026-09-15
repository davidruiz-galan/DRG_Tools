# How to add the next DRG tool

Keep every new tool inside the same `DRG_Tools` repository. Do not create a second independent installation unless the tool genuinely needs one.

## A new Gizmo

1. Name the class/file with the `DRG_` prefix, for example `DRG_EdgeExtend.gizmo`.
2. Save it in `gizmos/`.
3. Add an icon to `icons/`, for example `DRG_EdgeExtend.png`.
4. Add a small creation function in `python/drg_tools/tools.py`:

```python
def create_edge_extend():
    return nuke.createNode("DRG_EdgeExtend")
```

5. Register it in the appropriate category in the root `menu.py`.
6. Add documentation and a changelog entry.
7. Increment the **suite** version in `python/drg_tools/config.py` and `VERSION`.

## A new Python tool

Create a focused module under `python/drg_tools/`, for example `edge_tools.py`. Keep reusable helpers separate rather than duplicating code between tools.

## A new BlinkScript tool

Create `blink/` when the first BlinkScript tool is added, register that folder in the root `init.py`, and keep any wrapper gizmo in `gizmos/`.

## Naming rules

- Public class names: `DRG_ToolName`
- Python package: `drg_tools`
- Files: descriptive and stable
- User-visible menu labels: readable names without the technical prefix when appropriate

## Versioning

Suite releases use `MAJOR.MINOR.PATCH`:
- PATCH: bug fix only.
- MINOR: backwards-compatible new tool or feature.
- MAJOR: breaking change.

Individual tools can keep their own versions in `config.py`, but users install one DRG Tools release.

## Release metadata
Also update DRG_Tools/manifest.json and confirm tool versions match config.py. Paths above are relative to the DRG_Tools runtime folder. Developer documentation lives at repository root in dev/.

