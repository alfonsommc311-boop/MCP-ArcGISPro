using ArcGIS.Desktop.Framework.Contracts;

namespace MCPBridge
{
    /// <summary>Ribbon button: start the MCP bridge.</summary>
    internal class StartBridgeButton : Button
    {
        protected override void OnClick()
        {
            _ = BridgeRunner.StartAsync();
        }
    }

    /// <summary>Ribbon button: stop the MCP bridge.</summary>
    internal class StopBridgeButton : Button
    {
        protected override void OnClick()
        {
            _ = BridgeRunner.StopAsync();
        }
    }

    /// <summary>Ribbon button: report bridge status (RUNNING/STOPPED) in GP messages.</summary>
    internal class StatusBridgeButton : Button
    {
        protected override void OnClick()
        {
            _ = BridgeRunner.StatusAsync();
        }
    }
}
