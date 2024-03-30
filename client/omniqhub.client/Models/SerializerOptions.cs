namespace omniqhub.client.Models
{
    public static class SerializerOptions
    {
        public static JsonSerializerOptions Default { get; } =
            new JsonSerializerOptions(JsonSerializerDefaults.Web);
    }
}
