namespace omniqhub.client.Models
{
    public class RequestSettingsOverrides
    {
        public Approach Approach { get; set; }
        public RequestOverrides Overrides { get; set; } = new();
    }
}
