using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using MudBlazor.Services;
using Microsoft.Extensions.Azure;
using omniqhub.client.Interop;
using System.Runtime.InteropServices.JavaScript;

var builder = WebAssemblyHostBuilder.CreateDefault(args);

//builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
builder.Services.AddHttpClient<ApiClient>(client =>
{
    //client.BaseAddress = new Uri(builder.HostEnvironment.BaseAddress);
    client.BaseAddress = new Uri("http://localhost:8080/");
});
builder.Services.AddMudServices();
builder.Services.AddLocalStorageServices();
builder.Services.AddSpeechSynthesisServices();
builder.Services.AddSpeechRecognitionServices();
builder.Services.AddTransient<IPdfViewer, WebPdfViewer>();

#pragma warning disable CA1416 // Validate platform compatibility
await JSHost.ImportAsync(
    moduleName: nameof(JavaScriptModule),
    moduleUrl: $"../js/iframe.js?{Guid.NewGuid()}" /* cache bust */);
#pragma warning restore CA1416 // Validate platform compatibility

await builder.Build().RunAsync();
