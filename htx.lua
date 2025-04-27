{
    ["routing"] = {

        -- Route from http://example.com to localhost:8000
        {
            ["host"] = "example.com",
            ["path"] = {
                { ["path"] = "/", ["target"] = "http://localhost:8000" },
                {
                    ["path"] = "/.passwd",
                    ["target"] = function (source, headers, body)
                        if headers["Authorization"] == "ohk" then
                            return { ["target"] = "http://localhost:8000" }
                        end
                        return { ["target"] = { ["code"] = 403, ["body"] = "Forbidden! I hate you!" } }
                    end,
                },
            }
        }
    },
    ["inspect"] = function(source, headers, body)
        if body == "hello world" then
            return { ["target"] = { ["code"] = 500, ["body"] = "goodbye world" } }
        end
    end,
}
