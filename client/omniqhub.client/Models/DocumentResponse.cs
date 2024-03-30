namespace omniqhub.client.Models
{
    //public record class DocumentResponse(
    //string Name,
    //string ContentType,
    //long Size,
    //DateTimeOffset? LastModified,
    //Uri Url,
    //DocumentProcessingStatus Status,
    //EmbeddingType EmbeddingType);

    public class DocumentResponse
    {
        public string name { get; set; } = string.Empty;
        public string content_type { get; set; } = string.Empty;
        public long size { get; set; }
        public DateTimeOffset? last_modified { get; set; }
        public DocumentProcessingStatus status { get; set; }
        public Uri? url { get; set; }
    }

}
