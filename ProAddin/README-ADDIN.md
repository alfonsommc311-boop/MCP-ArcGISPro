# MCP Bridge — ArcGIS Pro Add-in (C#) skeleton

A thin ribbon shell over the Python toolbox. The add-in adds a **MCP Bridge** ribbon
tab with **Start / Stop / Status** buttons and **auto-starts the bridge when a project
opens**. All real work stays in Python (`MCP_Bridge.pyt` → `pro_bridge.py`); the C#
just invokes those tools via geoprocessing (in-process Python, where the bridge runs).

```
Ribbon button / ProjectOpenedEvent  (C#)
        │  Geoprocessing.ExecuteToolAsync("...\MCP_Bridge.pyt\StartBridge")
        ▼
MCP_Bridge.pyt  (Python toolbox)  →  exec pro_bridge.py  →  daemon poll thread
```

## Files

| File | Role |
|---|---|
| `Config.daml` | Add-in manifest: module + ribbon tab + 3 buttons |
| `Module1.cs` | Auto-loaded module; subscribes to `ProjectOpenedEvent` for auto-start |
| `BridgeRunner.cs` | Runs the `.pyt` tools via `Geoprocessing.ExecuteToolAsync` |
| `Buttons.cs` | `StartBridgeButton` / `StopBridgeButton` / `StatusBridgeButton` |
| `MCPBridge.csproj` | Reference project (prefer the VS Pro SDK template — see below) |

## Build (recommended path)

1. Install **Visual Studio 2022** + the **ArcGIS Pro SDK for .NET** (matching Pro 3.4).
2. New Project → **ArcGIS Pro Module Add-in** (this wires the Esri build targets that
   package the `.esriAddinX`). Name it `MCPBridge`.
3. **Replace** the generated `Config.daml` and `Module1.cs` with the ones here, and
   **add** `BridgeRunner.cs` + `Buttons.cs`.
4. **Copy** `MCP_Bridge.pyt` and `pro_bridge.py` into the project and set each to
   *Build Action = Content*, *Copy to Output = Copy always* (so they're packaged and
   land next to the DLL — that's how `BridgeRunner` finds the toolbox).
5. Build. Double-click the produced **`MCPBridge.esriAddinX`** to install into ArcGIS Pro.

## Verify

- Open ArcGIS Pro → a project → the bridge should auto-start (ribbon **MCP Bridge** tab → **Status** → RUNNING).
- Toggle auto-start off in code via `Module1.AutoStartOnProjectOpen = false` if you want manual-only.

## Notes / TODO before shipping

- **Signing:** sign the add-in for trusted distribution (Pro warns on unsigned add-ins).
- **Versions:** test against the Pro versions you support (3.2 = .NET 6, 3.3+ = .NET 8).
- **Robustness:** `StartBridge` is idempotent; consider a heartbeat/health indicator on the button.
- **Packaging the Python:** alternatively install the `.pyt`/bridge to a fixed location and point `BridgeRunner.ToolboxPath()` there, instead of bundling.
