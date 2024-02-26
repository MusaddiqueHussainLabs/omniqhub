namespace omniqhub.client.Models
{
    public record PromptResponse(string Prompt, string Response, bool IsComplete = false);
}
