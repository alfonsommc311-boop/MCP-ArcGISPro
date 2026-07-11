using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Dialogs;

namespace MCPBridge
{
    /// <summary>
    /// Thin wrapper that runs the Python toolbox tools (Start/Stop/Status) shipped
    /// alongside the add-in. All real logic lives in MCP_Bridge.pyt + pro_bridge.py;
    /// the add-in just invokes those tools via geoprocessing, which executes in
    /// ArcGIS Pro's in-process Python — exactly where the bridge needs to run.
    /// </summary>
    internal static class BridgeRunner
    {
        // MCP_Bridge.pyt is packaged as content next to the add-in assembly.
        private static string ToolboxPath()
        {
            string dir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            return Path.Combine(dir, "MCP_Bridge.pyt");
        }

        /// <summary>Run a tool in the bundled Python toolbox by class name.</summary>
        /// <param name="toolName">StartBridge | StopBridge | BridgeStatus</param>
        public static async Task<bool> RunToolAsync(string toolName, bool showErrors = true)
        {
            string toolPath = Path.Combine(ToolboxPath(), toolName); // ...\MCP_Bridge.pyt\StartBridge

            if (!Directory.Exists(ToolboxPath()) && !File.Exists(ToolboxPath()))
            {
                if (showErrors)
                    MessageBox.Show("MCP_Bridge.pyt was not found next to the add-in:\n" + ToolboxPath(),
                                    "MCP Bridge");
                return false;
            }

            IGPResult result = await Geoprocessing.ExecuteToolAsync(
                toolPath,
                values: null,                 // these tools take no parameters
                environments: null,
                cancelableProgressor: null,
                flags: GPExecuteToolFlags.Default);   // runs in Pro's in-process Python

            if (result == null || result.IsFailed)
            {
                if (showErrors)
                {
                    string msg = result?.Messages != null
                        ? string.Join(Environment.NewLine, result.Messages.Select(m => m.Text))
                        : "Unknown error.";
                    MessageBox.Show("MCP Bridge tool '" + toolName + "' failed:\n" + msg, "MCP Bridge");
                }
                return false;
            }
            return true;
        }

        public static Task<bool> StartAsync(bool showErrors = true) => RunToolAsync("StartBridge", showErrors);
        public static Task<bool> StopAsync() => RunToolAsync("StopBridge");
        public static Task<bool> StatusAsync() => RunToolAsync("BridgeStatus");
    }
}
