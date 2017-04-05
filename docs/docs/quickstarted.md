# Installation

## misuzu on windows {docsify-ignore}

# Minimal Application

```python
from misuzu import Misuzu
from misuzu.response import Response
app = Misuzu(__name__)

@app.get("/")
@app.param('')
async def test(request):
    return Response("hello world.", content_type="text/html")

app.run()
```

# Debug Mode
 TODO: watchdog and signal on windows

# Routing

# Params Definition

# Redirects and Http Errors

# Request

# Response

# deploying with nginx