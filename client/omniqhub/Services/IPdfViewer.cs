// Copyright (c) Microsoft. All rights reserved.

namespace omniqhub.Services;

public interface IPdfViewer
{
    ValueTask ShowDocumentAsync(string name, string baseUrl);
}
