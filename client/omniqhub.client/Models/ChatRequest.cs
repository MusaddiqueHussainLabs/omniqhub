﻿namespace omniqhub.client.Models
{
    public record class ChatRequest(
    ChatTurn[] History,
    Approach Approach,
    RequestOverrides? Overrides = null) : ApproachRequest(Approach)
    {
        public string? LastUserQuestion => History?.LastOrDefault()?.User;
    }
}
