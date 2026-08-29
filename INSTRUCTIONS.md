# ArcGIS Pro MCP Bridge — Claude Instructions

You have access to an ArcGIS Pro MCP bridge that controls a running ArcGIS Pro session.
Follow these rules every time you work with ArcGIS Pro tools.

---

## 1. Always Start with a Status Check

Before doing anything, call `ping()` and read the `status` field:

| Status | Meaning | Action |
|---|---|---|
| `ready` | Map/Scene/Globe is open and active | Proceed directly |
| `map_not_opened` | Map exists but no view is open | Proceed with non-view ops; remind user to open the map for zoom/visual results |
| `no_maps` | Blank project, nothing created yet | Ask the user what they want (Map, Scene, or Globe), then create it |

---

## 2. If No Map Exists — Ask First, Then Create

Never silently create a map without knowing the user's intent. Ask:

> "Your project has no maps yet. What would you like to create?
> - **Map** — standard 2D map (most common)
> - **Scene** — 3D local scene
> - **Globe** — 3D global view"

Then use `create_map(name=..., map_type=...)` based on their answer.
If the user's request implies 2D work (layers, buffers, analysis), default to **Map**.

---

## 3. Verify Files Before Using Them

Before adding a layer or running geoprocessing on a file:
- Use `list_directory(path)` to confirm the file exists and get the exact filename
- Use `describe_data(path)` to get the coordinate system before any metric operations

Never guess file names. If the user says `"Rusun_Jateng.shp"` but the directory shows `"Rusun_Jateng_DIY.shp"`, use the correct name.

---

## 4. Always Check Coordinate System Before Metric Geoprocessing

Before running any tool that uses distance units (Buffer, Near, etc.):
1. Call `describe_data(path)` and check `spatialReference.type`
2. If **Geographic** (degrees) → reproject first using `run_geoprocessing("management.Project", ...)`
3. Choose the correct UTM zone for the data's location
4. Then run the metric operation on the reprojected output

---

## 5. Standard End-to-End Workflow

For a typical "load → process → present" request, follow this sequence:

```
ping()                          ← check status
  ↓
list_directory() / describe_data()  ← verify files + CRS
  ↓
add_vector_layer() / add_raster_layer()  ← load data
  ↓
run_geoprocessing(...)          ← reproject if needed, then process
  ↓
add_vector_layer(result)        ← add output to map
  ↓
zoom_to_layer(result)           ← zoom if view is open
  ↓
create_layout() → export_layout()  ← export as PDF/PNG if requested
```

---

## 6. Zoom and View Rules

- `zoom_to_layer` only works if a map view is open in ArcGIS Pro
- If no view is open, the tool returns a `warning` (not an error) — relay this to the user:
  > "The layer was added successfully. Open the map in ArcGIS Pro (double-click it in the Catalog pane) to see it."
- Never retry `zoom_to_layer` in a loop if no view is open — it won't change

---

## 7. When a Specific Tool Doesn't Exist

If a workflow step isn't covered by the available tools, use `execute_python(code)`.
This runs arbitrary arcpy / arcpy.mp code directly in the bridge. Example:

```python
# Create a local scene
result = proj.createMap("My Scene", "SCENE")
```

Use `execute_python` as a last resort, not a first choice.

---

## 8. Editing Data — Confirm Before Bulk Updates

`update_features` sets the same field value(s) on every row matching `where_clause`, with no undo.

Before calling it:
- State the exact `where_clause` and the field/value changes in plain language
- Get explicit confirmation from the user first
- Be especially careful with `where_clause=""` — that updates every row in the layer
- For per-row computed values (e.g. incrementing a field), use `execute_python` with an `UpdateCursor` instead — `update_features` only sets constant values

---

## 9. Publishing — Always Confirm First

`publish_web_layer` creates or overwrites content on the user's ArcGIS Online / Enterprise portal (whichever is active in ArcGIS Pro). This is visible to others if shared publicly, and can overwrite an existing service if `overwrite=True`.

Before calling it, confirm with the user:
- The exact service name
- Whether it should be public or private (default is private)
- Whether it's OK to overwrite if a service with that name already exists

If `ping()` or the tool's error indicates no active portal, tell the user to sign in via ArcGIS Pro's Settings > Portals first — this bridge cannot sign in on their behalf.

**Known limitation (confirmed, not a guess):** `publish_web_layer` fails with a generic `ERROR 999999` every time, caused by this bridge's background-thread architecture — proven with a controlled test comparing the identical call from the bridge (fails instantly) vs. from the Pro Python window's console directly (succeeds, ~10s). Don't retry this tool repeatedly on a 999999 failure. Tell the user to either publish through the Pro UI directly, or offer to write them a short standalone script to paste into the Python window console (same arcpy calls, no bridge involved) — both work.

---

## 10. Be Transparent About What You Did

After completing a workflow, summarize:
- What layers were added
- What geoprocessing was run (tool, parameters, output path)
- The CRS used for analysis
- Where output files were saved
- Whether the map view is open or needs to be opened manually
- Any data edited (`update_features`) or content published (`publish_web_layer`)
