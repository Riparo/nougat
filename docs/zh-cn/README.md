# Nougat
!> **注意: 该项目仍处于原型设计阶段，请确保你做的每一件事将会发生什么**

Nougat 是一个专注于 API 编写的异步框架。其最主要的特性是人性化的 API 参数定义方式，它做到了让参数定义和业务处理逻辑分离。另外一个特性是框架提供了自动生成 API 文档的功能。

## 为什么选择 Nougat
Nougat 使用了uvloop 作为底层的异步实现，相比于标准库中的 asyncio 性能更高。而且异步的实现方式可以更好的利用 CPU ，相比于多线程减少了 CPU 调度的时间。
其次，Nougat 专注如何更加高效地编写 API，努力成为一个偏执的框架。

## HELLO WORLD
```python
from nougat import Nougat, Section

app = Nougat(__name__)
main = Section('main')

@main.get("/")
async def index_get(request):
    return {"test": "hello world"}

app.register_section(main)
app.run()
```

以上代码简单地显示出了 Nougat 的代码组织模式，它看起来与 Flask 和 Sanic 极其相似的。是的，在使用 Nougat 的时候，会大量地使用装饰器，因为这样会相当 Pythonic。