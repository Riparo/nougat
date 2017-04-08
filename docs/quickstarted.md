# Installation

## misuzu on windows {docsify-ignore}

# Minimal Application

```python
from misuzu import Misuzu

app = Misuzu(__name__)


@app.get('/<name>')
@app.param('name', str)
async def index(request):

    return {
        'hello': request.params.name
    }


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