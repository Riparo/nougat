# Misuzu
**NOTICE: this project is still  a prototype, make sure what you do for each step you do**

Misuzu is an async framework which focus on best writing experience of API. The key features are the human friendly params definition, which is divided from the method's logic, and the automatic documents.



## Support

Python 3.5 or newer

uvloop, which is the basemen of misuzu for providing fast async event loop, is linux only, would be replace with asyncio in windows.

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

## Document

coming soon.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Kilerd/misuzu/blob/master/LICENSE) file for details

## Acknowledgments

- uvloop
- httptools