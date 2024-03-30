namespace omniqhub.client.Models
{
    //public record class UploadDocumentsResponse(
    //string[] uploaded_files,
    //string? Error = null)
    //{
    //    public bool IsSuccessful => this is
    //    {
    //        Error: null,
    //        UploadedFiles.Length: > 0
    //    };

    //    public static UploadDocumentsResponse FromError(string error) =>
    //        new([], error);
    //}

    public class UploadDocumentsResponse
    {
        public string[] uploaded_files { get; set; }
        public bool is_successful { get; set; }
        public string error { get; set; }
    }
}
