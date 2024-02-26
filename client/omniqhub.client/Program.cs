using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using MudBlazor.Services;
using omniqhub.client.Services;

namespace omniqhub.client
{
    public class Program
    {
        public static async Task Main(string[] args)
        {
            var builder = WebAssemblyHostBuilder.CreateDefault(args);
            builder.RootComponents.Add<App>("#app");
            builder.RootComponents.Add<HeadOutlet>("head::after");

            builder.Services.AddHttpClient<ApiClient>(client =>
            {
                client.BaseAddress = new Uri(builder.HostEnvironment.BaseAddress);
            });

            
            builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
            builder.Services.AddScoped<OpenAIPromptQueue>();
            builder.Services.AddMudServices();
            builder.Services.AddLocalStorageServices();
            builder.Services.AddSessionStorageServices();
            builder.Services.AddSpeechSynthesisServices();
            builder.Services.AddSpeechRecognitionServices();
            builder.Services.AddSingleton<ITextToSpeechPreferencesListener, TextToSpeechPreferencesListenerService>();
            builder.Services.AddTransient<IPdfViewer, WebPdfViewer>();

            builder.Services.AddOidcAuthentication(options =>
            {
                // Configure your authentication provider options here.
                // For more information, see https://aka.ms/blazor-standalone-auth
                builder.Configuration.Bind("Local", options.ProviderOptions);
            });

            await builder.Build().RunAsync();
        }
    }
}
