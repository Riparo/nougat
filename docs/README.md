# Misuzu
!> **NOTICE: this project is still  a prototype, make sure what you do for each step you do**

Misuzu is an async framework which focus on best writing experience of API. The key features are the human friendly params definition, which is divided from the method's logic, and the automatic documents.

## hello world

```python
from misuzu import Misuzu

app = Misuzu(__name__)

@app.get('/<name>')
@app.param('name', str)
async def index(request):
    return {'hello': request.params.name}

app.run()
```