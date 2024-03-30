using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Net.Mime;

namespace omniqhub.client.Services
{
    public sealed class ApiClient(HttpClient httpClient)
    {
        MultipartFormDataContent multipartContent = new();
        public async Task<ImageResponse?> RequestImageAsync(PromptRequest request)
        {
            var response = await httpClient.PostAsJsonAsync(
                "api/images", request, SerializerOptions.Default);

            response.EnsureSuccessStatusCode();

            return await response.Content.ReadFromJsonAsync<ImageResponse>();
        }

        public async Task<bool> ShowLogoutButtonAsync()
        {
            var response = await httpClient.GetAsync("api/enableLogout");
            response.EnsureSuccessStatusCode();

            return await response.Content.ReadFromJsonAsync<bool>();
        }

        public async Task<AuthResponse?> Login(LoginCommand request)
        {
            multipartContent.Add(new StringContent(request.Email, Encoding.UTF8, MediaTypeNames.Text.Plain), "username");
            multipartContent.Add(new StringContent(request.Password, Encoding.UTF8, MediaTypeNames.Text.Plain), "password");

            var response = await httpClient.PostAsync(
                "api/v1/login", multipartContent);

            //response.EnsureSuccessStatusCode();

            if(response.IsSuccessStatusCode)
            {
                return await response.Content.ReadFromJsonAsync<AuthResponse>();
            }
            return null;
        }

        public async Task<UploadDocumentsResponse> UploadDocumentsAsync(
            IReadOnlyList<IBrowserFile> files,
            long maxAllowedSize)
        {
            try
            {
                using var content = new MultipartFormDataContent();

                foreach (var file in files)
                {
                    // max allow size: 10mb
                    var max_size = maxAllowedSize * 1024 * 1024;
                    #pragma warning disable CA2000 // Dispose objects before losing scope
                    var fileContent = new StreamContent(file.OpenReadStream(max_size));
                    #pragma warning restore CA2000 // Dispose objects before losing scope
                    fileContent.Headers.ContentType = new MediaTypeHeaderValue(file.ContentType);

                    content.Add(fileContent, "files", file.Name);
                }

                var response = await httpClient.PostAsync("api/v1/documents", content);

                //response.EnsureSuccessStatusCode();
                if(response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<UploadDocumentsResponse>();

#pragma warning disable CS8603 // Possible null reference return.
                    return result;
#pragma warning restore CS8603 // Possible null reference return.
                }
                
                UploadDocumentsResponse uploadDocumentsResponse = new UploadDocumentsResponse();
                uploadDocumentsResponse.error = "Unable to upload files, unknown error.";
                return uploadDocumentsResponse;

            }
            catch (Exception ex)
            {
                UploadDocumentsResponse uploadDocumentsResponse = new UploadDocumentsResponse();
                uploadDocumentsResponse.error = ex.ToString();
                return uploadDocumentsResponse;
            }
        }

        public async Task<DocumentResponse[]?> GetDocumentsAsync()
        {
            var response = await httpClient.GetAsync("api/v1/documents");

            if (response.IsSuccessStatusCode)
            {
                string jsonResponse = await response.Content.ReadAsStringAsync();
#pragma warning disable CS8600 // Converting null literal or possible null value to non-nullable type.
                DocumentResponse[] documentResponses = JsonSerializer.Deserialize<DocumentResponse[]>(jsonResponse);
#pragma warning restore CS8600 // Converting null literal or possible null value to non-nullable type.

                return documentResponses;

            }
            return null;
        }

        public Task<AnswerResult<ChatRequest>> ChatConversationAsync(ChatRequest request) => PostRequestAsync(request, "api/v1/chat");

        private async Task<AnswerResult<TRequest>> PostRequestAsync<TRequest>(
            TRequest request, string apiRoute) where TRequest : ApproachRequest
        {
            var result = new AnswerResult<TRequest>(
                IsSuccessful: false,
                Response: null,
                Approach: request.Approach,
                Request: request);

            var json = JsonSerializer.Serialize(
                request,
                SerializerOptions.Default);

            using var body = new StringContent(
                json, Encoding.UTF8, "application/json");

            var response = await httpClient.PostAsync(apiRoute, body);

            if (response.IsSuccessStatusCode)
            {
                var answer = await response.Content.ReadFromJsonAsync<ApproachResponse>();
                return result with
                {
                    IsSuccessful = answer is not null,
                    Response = answer
                };
            }
            else
            {
                var answer = new ApproachResponse(
                    $"HTTP {(int)response.StatusCode} : {response.ReasonPhrase ?? "☹️ Unknown error..."}",
                    null,
                    [],
                    null,
                    "Unable to retrieve valid response from the server.");

                return result with
                {
                    IsSuccessful = false,
                    Response = answer
                };
            }
        }
    }
}
