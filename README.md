# ArcGIS Pro MCP Bridge

Control ArcGIS Pro from Claude Desktop using the Model Context Protocol (MCP).  
Pure Python — no C#, no .NET SDK, no Visual Studio required.

---

## What It Does

Connects Claude Desktop (or any MCP client) to a live ArcGIS Pro session, enabling natural language control of:

- Add / remove layers (vector and raster)
- Run any ArcPy geoprocessing tool (buffer, clip, intersect, project, dissolve, and more)
- Check coordinate systems and reproject data
- Query and select features by attribute
- List layers, fields, feature classes, rasters, and tables
- Create layouts and export maps (PDF, PNG, JPG, TIF, SVG, EPS)
- Zoom to layers, toggle visibility, save projects
- Execute arbitrary ArcPy / arcpy.mp code

---

## Requirements

- ArcGIS Pro 3.x (tested on 3.6.1)
- Claude Desktop
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — lightweight Python package manager

> **Already using QGIS-MCP?** You already have `uv` installed. Skip straight to step 2.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Geo2004/MCP-ArcgisPro.git
```

### 2. Install uv (if not already installed)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`uv` handles the `mcp` package dependency automatically — no manual `pip install` needed.

### 3. Configure Claude Desktop

Add the following to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arcgis-pro": {
      "command": "C:/Users/<YourUsername>/.local/bin/uv.exe",
      "args": [
        "--directory",
        "C:/path/to/MCP-ArcgisPro",
        "run",
        "arcgis_mcp_server.py"
      ]
    }
  }
}
```

Replace `<YourUsername>` and the directory path with your actual values.

### 3. Start the bridge in ArcGIS Pro

Every session, before using Claude:

1. Open **ArcGIS Pro** and load a project (or create a new one)
2. Open a **Map**, **Scene**, or **Globe** so it is active
3. Go to the **Analysis** tab → click **Python** to open the Python window
4. Run:

```python
exec(open(r"C:/path/to/MCP-ArcgisPro/pro_bridge.py").read())
```

You should see:
```
[MCP Bridge] Project cached: C:\path\to\your.aprx
[MCP Bridge] Running in background thread. IPC: C:\Users\..\.arcgis_mcp
[MCP Bridge] Python window is free.  To stop: _bridge_active = False
```

### 4. Restart Claude Desktop

Restart Claude Desktop after updating the config. The ArcGIS Pro tools will appear automatically.

---

## Usage

Just talk to Claude naturally. Examples:

> *"Add the roads shapefile from C:/data to the map"*

> *"Check the coordinate system of parcels.shp and run a 500m buffer, dissolve all overlaps"*

> *"List all layers in my current map"*

> *"Export the layout as PNG to C:/output/map.png"*

> *"Select all features where KECAMATAN = 'Semarang Tengah' and count them"*

> *"Run a slope analysis on my DEM raster"*

---

## Available Tools (30)

| Category | Tools |
|---|---|
| **Connection** | `ping` |
| **Project** | `get_project_info`, `save_project` |
| **Map** | `get_active_map_name`, `create_map` |
| **Layers** | `list_layers`, `add_vector_layer`, `add_raster_layer`, `remove_layer`, `zoom_to_layer`, `set_layer_visibility` |
| **Data** | `describe_data`, `list_directory`, `list_fields`, `get_layer_features`, `get_unique_values` |
| **Workspace** | `set_workspace`, `get_workspace`, `list_feature_classes`, `list_rasters`, `list_tables` |
| **Selection** | `select_by_attribute`, `clear_selection`, `count_features` |
| **Geoprocessing** | `run_geoprocessing` *(any arcpy tool by dotted name)* |
| **Layout & Export** | `list_layouts`, `create_layout`, `export_layout` |
| **Advanced** | `execute_python` *(arbitrary arcpy/arcpy.mp code)* |

---

## How It Works

```
Claude Desktop
    ↓  stdio (MCP)
arcgis_mcp_server.py   ← runs via uv, any Python
    ↓  file-based IPC  (~/.arcgis_mcp/)
pro_bridge.py          ← runs in ArcGIS Pro's Python window
    ↓  arcpy.mp API
ArcGIS Pro (live session)
```

The bridge uses file-based IPC (command / result JSON files in `~/.arcgis_mcp/`) — no sockets, no named pipes, no compilation required.

---

## Known Limitations

- **Opening a map view automatically** is not possible via Python/ArcPy alone (requires ArcGIS Pro C# SDK). The user must open the map view manually once per session by double-clicking it in the Catalog pane. All other operations work without an open view.
- **ArcGIS Online / Enterprise publishing** is not yet implemented.
- **Interactive editing** (sketch tools, attribute forms) requires the ArcGIS Pro UI and cannot be automated.

---

## Stopping the Bridge

In the ArcGIS Pro Python window:

```python
_bridge_active = False
```

Or simply close the Python window or restart ArcGIS Pro.

---

## License

MIT
