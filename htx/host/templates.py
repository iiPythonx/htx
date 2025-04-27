# Copyright (c) 2025 iiPython

# Templating
GATEWAY_ISSUE = """
<!doctype html>
<html lang = "en">
    <head>
        <meta charset = "utf-8">

        <!-- CSS -->
        <style>
            body, html {{
                margin: 0px;
                height: 100%;
                color: #fff;
                background: #000;
            }}
            body {{
                font-family: monospace;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                gap: 10px;
            }}
            div {{
                padding: 2px 10px;
                background-color: gray;
            }}
        </style>

        <title>HTX · {code}</title>
    </head>
    <body>
        <div>{title}</div>
        <span>{message}</span>
    </body>
</html>
"""
