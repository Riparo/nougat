# Misuzu
!> **NOTICE: this project is still  a prototype, make sure what you do for each step you do**

Misuzu is an async framework which focus on best writing experience of API. The key features are the human friendly params definition, which is divided from the method's logic, and the automatic documents.

## Chinese Document First
## hello world

```python
from misuzu import Misuzu, Section

app = Misuzu(__name__)
main = Section('main')

@main.get("/")
async def index_get(request):
    return {"test": "hello world"}

app.register_section(main)
app.run()
```