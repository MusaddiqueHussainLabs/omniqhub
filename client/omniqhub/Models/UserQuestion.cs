// Copyright (c) Microsoft. All rights reserved.

namespace omniqhub.Models;

public readonly record struct UserQuestion(
    string Question,
    DateTime AskedOn);
