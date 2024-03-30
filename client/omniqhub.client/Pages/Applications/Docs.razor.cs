using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.Components;
using Microsoft.JSInterop;
using MudBlazor;

namespace omniqhub.client.Pages.Applications
{
    public sealed partial class Docs : IDisposable
    {
        private const long MaxIndividualFileSize = 1_024L * 1_024;

        private MudForm _form = null!;
        private MudFileUpload<IReadOnlyList<IBrowserFile>> _fileUpload = null!;
        private Task _getDocumentsTask = null!;
        private bool _isLoadingDocuments = false;
        private string _filter = "";

        // Store a cancelation token that will be used to cancel if the user disposes of this component.
        private readonly CancellationTokenSource _cancellationTokenSource = new();
        private readonly HashSet<DocumentResponse> _documents = [];

        [Inject]
        public required ApiClient Client { get; set; }

        [Inject]
        public required ISnackbar Snackbar { get; set; }

        [Inject]
        public required ILogger<Docs> Logger { get; set; }

        [Inject]
        public required IJSRuntime JSRuntime { get; set; }

        [Inject]
        public required IPdfViewer PdfViewer { get; set; }

        private bool FilesSelected => _fileUpload is { Files.Count: > 0 };

        protected override void OnInitialized() =>
            _getDocumentsTask = GetDocumentsAsync();
        //protected override void OnInitialized()
        //{
        //    base.OnInitialized();
        //}

        private bool OnFilter(DocumentResponse document) => document is not null
            && (string.IsNullOrWhiteSpace(_filter) || document.name.Contains(_filter, StringComparison.OrdinalIgnoreCase));

        private async Task GetDocumentsAsync()
        {
            _isLoadingDocuments = true;

            try
            {
                var documents = await Client.GetDocumentsAsync();
                _documents.Clear();

                foreach (var document in documents)
                {
                    _documents.Add(document);
                }
            }
            finally
            {
                _isLoadingDocuments = false;
                StateHasChanged();
            }
        }

        private async Task SubmitFilesForUploadAsync()
        {
            if (_fileUpload is { Files.Count: > 0 })
            {
                var result = await Client.UploadDocumentsAsync(
                    _fileUpload.Files, MaxIndividualFileSize);

                Logger.LogInformation("Result: {x}", result);

                if (result.is_successful)
                {
                    Snackbar.Add(
                        $"Uploaded {result.uploaded_files.Length} documents.",
                        Severity.Success,
                        static options =>
                        {
                            options.ShowCloseIcon = true;
                            options.VisibleStateDuration = 10_000;
                        });

                    await _fileUpload.ResetAsync();
                }
                else
                {
                    Snackbar.Add(
                        result.error,
                        Severity.Error,
                        static options =>
                        {
                            options.ShowCloseIcon = true;
                            options.VisibleStateDuration = 10_000;
                        });
                }
                _getDocumentsTask = GetDocumentsAsync();
            }
        }

        private ValueTask OnShowDocumentAsync(DocumentResponse document) =>
            PdfViewer.ShowDocumentAsync(document.name, document.url.ToString());

        public void Dispose() => _cancellationTokenSource.Cancel();
    }
}
