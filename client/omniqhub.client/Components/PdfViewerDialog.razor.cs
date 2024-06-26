﻿using omniqhub.client.Interop;

namespace omniqhub.client.Components
{
    public sealed partial class PdfViewerDialog
    {
        private bool _isLoading = true;
        private string _pdfViewerVisibilityStyle => _isLoading ? "display:none;" : "display:default;";

        [Parameter] public required string FileName { get; set; }
        [Parameter] public required string BaseUrl { get; set; }

        [CascadingParameter] public required MudDialogInstance Dialog { get; set; }

        protected override async Task OnInitializedAsync()
        {
            await base.OnInitializedAsync();
            await JavaScriptModule.RegisterIFrameLoadedAsync(
                "#pdf-viewer",
                () =>
                {
                    _isLoading = false;
                    StateHasChanged();
                });
        }

        private void OnCloseClick() => Dialog.Close(DialogResult.Ok(true));
    }
}
