// Copyright (c) Microsoft. All rights reserved.

namespace shared.Models;

public record class ImageResponse(
    DateTimeOffset Created,
    List<Uri> ImageUrls);
