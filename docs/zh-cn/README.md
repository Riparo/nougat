# Misuzu
!> **注意: 该项目仍处于原型设计阶段，请确保你做的每一件事将会发生什么**

Misuzu 是一个专注于 API 编写的异步框架。其最主要的特性是人性化的 API 参数定义方式，它做到了让参数定义和业务处理逻辑分离。另外一个特性是框架提供了自动生成 API 文档的功能。

## 为什么选择 Misuzu
Misuzu 使用了uvloop 作为底层的异步实现，相比于标准库中的 asyncio 性能更高。而且异步的实现方式可以更好的利用 CPU ，相比于多线程减少了 CPU 调度的时间。
其次，Misuzu 专注如何更加高效地编写 API，努力成为一个偏执的框架。

## HELLO WORLD
```python
from misuzu import Misuzu
from misuzu.response import Response
app = Misuzu(__name__)

@app.get("/")
async def test(request):
    return Response("hello world.", content_type="text/html")

app.run()
```

以上代码简单地显示出了 Misuzu 的代码组织模式，它看起来与 Flask 和 Sanic 极其相似的。是的，在使用 Misuzu 的时候，会大量地使用装饰器，因为这样会相当 Pythonic。