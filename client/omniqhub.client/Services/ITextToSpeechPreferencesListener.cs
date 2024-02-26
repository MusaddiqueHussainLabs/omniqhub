namespace omniqhub.client.Services
{
    public interface ITextToSpeechPreferencesListener
    {
        void OnAvailableVoicesChanged(Func<Task> onVoicesChanged);

        void UnsubscribeFromAvailableVoicesChanged();
    }
}
