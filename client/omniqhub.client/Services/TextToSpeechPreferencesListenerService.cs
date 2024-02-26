using Microsoft.JSInterop;

namespace omniqhub.client.Services
{
    public sealed class TextToSpeechPreferencesListenerService(
    ISpeechSynthesisService speechSynthesisService) : ITextToSpeechPreferencesListener
    {
        public void OnAvailableVoicesChanged(Func<Task> onVoicesChanged) =>
            speechSynthesisService.OnVoicesChanged(onVoicesChanged);

        public void UnsubscribeFromAvailableVoicesChanged() =>
            speechSynthesisService.UnsubscribeFromVoicesChanged();
    }
}
