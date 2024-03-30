using System.Runtime.InteropServices.JavaScript;

namespace omniqhub.client.Interop
{
    internal sealed partial class JavaScriptModule
    {
        [JSImport("listenForIFrameLoaded", nameof(JavaScriptModule))]
        public static partial Task RegisterIFrameLoadedAsync(
            string selector,
            [JSMarshalAs<JSType.Function>] Action onLoaded);

        [JSImport("scrollIntoView", nameof(JavaScriptModule))]
        public static partial Task ScrollIntoView(string id);
    }
}
