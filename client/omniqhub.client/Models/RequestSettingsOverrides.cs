﻿namespace omniqhub.client.Models
{
    public record RequestSettingsOverrides
    {
        public Approach Approach { get; set; }
        public RequestOverrides Overrides { get; set; } = new();
    }
}
