namespace omniqhub.client.Models
{
    public record SupportingContentRecord(string Title, string Content);

    public record SupportingImageRecord(string Title, string Url);

    public record ApproachResponse(
        string answer,
        string? thoughts,
        SupportingContentRecord[]? data_points, // title, content
        SupportingImageRecord[]? images, // title, url
        string citation_base_url,
        string? error = null);

}
