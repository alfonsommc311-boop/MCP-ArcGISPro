using ArcGIS.Desktop.Core.Events;
using ArcGIS.Desktop.Framework;
using ArcGIS.Desktop.Framework.Contracts;

namespace MCPBridge
{
    /// <summary>
    /// Add-in module. Auto-loaded at startup (autoLoad="true" in Config.daml) so it
    /// can subscribe to ProjectOpenedEvent and auto-start the MCP bridge — giving the
    /// "zero clicks" experience: open a project and the bridge is already listening.
    /// </summary>
    internal class Module1 : Module
    {
        private static Module1 _this = null;

        /// <summary>Singleton accessor (id must match insertModule id in Config.daml).</summary>
        public static Module1 Current =>
            _this ??= (Module1)FrameworkApplication.FindModule("MCPBridge_Module");

        // Set false if you prefer manual start only (button on the ribbon).
        public static bool AutoStartOnProjectOpen { get; set; } = true;

        protected override bool Initialize()
        {
            ProjectOpenedEvent.Subscribe(OnProjectOpened);
            return base.Initialize();
        }

        protected override void Uninitialize()
        {
            ProjectOpenedEvent.Unsubscribe(OnProjectOpened);
            base.Uninitialize();
        }

        private void OnProjectOpened(ProjectEventArgs args)
        {
            if (!AutoStartOnProjectOpen)
                return;

            // Fire-and-forget: StartBridge is idempotent (it no-ops if already running).
            // ExecuteToolAsync manages its own threading context.
            _ = BridgeRunner.StartAsync(showErrors: false);
        }

        /// <summary>Called by Pro when the user tries to close the app / project.</summary>
        protected override bool CanUnload()
        {
            // Best-effort stop so the daemon thread doesn't linger.
            _ = BridgeRunner.StopAsync();
            return true;
        }
    }
}
