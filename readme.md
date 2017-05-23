# misuzu

![PyPI](https://img.shields.io/pypi/pyversions/misuzu.svg) ![PyPI](https://img.shields.io/pypi/status/misuzu.svg) ![PyPI](https://img.shields.io/pypi/v/misuzu.svg) ![PyPI](https://img.shields.io/pypi/l/misuzu.svg) ![CircleCI branch](https://img.shields.io/circleci/project/github/Kilerd/misuzu/master.svg)

an asynchronous framework which focus on best writing experience of API. The key features are the human friendly definition of parameters, which is divided from the method's logic, and the automatic documents.

## installation

```bash
pip install misuzu
```

## hello world

```python
from misuzu import Misuzu, Section

app = Misuzu(__name__)
main = Section('main')

@main.get("/")
async def index_get(ctx):
    return "123"

app.use(main)
app.run(port=8000)
```

then, open http://127.0.0.1:8000, you can see the `123`

## Document

click [here](https://kilerd.github.io/misuzu/) to see document.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Kilerd/misuzu/blob/master/LICENSE) file for details.
