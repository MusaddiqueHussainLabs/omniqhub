using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace shared.Json
{
    public static class SerializerOptions
    {
        public static JsonSerializerOptions Default { get; } =
            new JsonSerializerOptions(JsonSerializerDefaults.Web);
    }
}
