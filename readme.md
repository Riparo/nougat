# nougat

![PyPI](https://img.shields.io/pypi/pyversions/nougat.svg) ![PyPI](https://img.shields.io/pypi/status/nougat.svg) ![PyPI](https://img.shields.io/pypi/v/nougat.svg) ![PyPI](https://img.shields.io/pypi/l/nougat.svg) [![Build Status](https://travis-ci.org/NougatWeb/nougat.svg?branch=master)](https://travis-ci.org/NougatWeb/nougat)

Nougat is an asynchronous web framework based on Python3.6, which focus on enhancing the experience of asynchronous web developing

## Installation
Nougat relays on Python3.6 and DOES NOT support the elder version, which is hosted at Pypi. So you can install stable version through:
```bash
pip3 install nougat
```
#### Develop Version
if you wanna test the new feature of Nougat, you can install it from Github:
**In Develop Version it would has some unknown bugs and unstable factors, SO PLEASE CHOOSE IT DELIBERATELY!**
```bash
pip3 install git@github.com:Kilerd/nougat.git@develop
```

### Minimal Usage
```python
from nougat import Nougat

app = Nougat()

async def m(req, res, next):
    res.content = "hello world"
    await next()

app.use(m)

app.run(debug=True)
```


## Document

click [here](https://kilerd.github.io/nougat/) to see document.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Kilerd/nougat/blob/master/LICENSE) file for details.
