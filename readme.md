# nougat

![PyPI](https://img.shields.io/pypi/pyversions/nougat.svg) ![PyPI](https://img.shields.io/pypi/status/nougat.svg) ![PyPI](https://img.shields.io/pypi/v/nougat.svg) ![PyPI](https://img.shields.io/pypi/l/nougat.svg) ![CircleCI branch](https://img.shields.io/circleci/project/github/Kilerd/nougat/master.svg)

an asynchronous framework which focus on best writing experience of API. The key features are the human friendly definition of parameters, which is divided from the method's logic, and the automatic documents.

## installation

```bash
pip install nougat
```

## hello world

```python
from nougat import Nougat, Section

app = Nougat(__name__)
main = Section('main')

@main.get("/")
async def index_get(ctx):
    return "123"

app.use(main)
app.run(port=8000)
```

then, open http://127.0.0.1:8000, you can see the `123`

## Document

click [here](https://kilerd.github.io/nougat/) to see document.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Kilerd/nougat/blob/master/LICENSE) file for details.
