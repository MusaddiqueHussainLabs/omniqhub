// Copyright (c) Microsoft. All rights reserved.

namespace shared.Models;

public readonly record struct Section(
    string Id,
    string Content,
    string SourcePage,
    string SourceFile,
    string? Category = null);
