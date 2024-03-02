// Copyright (c) Microsoft. All rights reserved.

namespace shared.Models;

public record class ChatChunkResponse(
    int Length,
    string Text);
