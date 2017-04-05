# 快速入门
## 安装
!> PYTHON3 ONLY: misuzu 只支持 Python 3.5 及以后的版本

misuzu 寄托在 pypi 上，因此可以使用 `pip` 进行安装
```bash
pip install misuzu
```

### windows 下的 misuzu 
因为 misuzu 是基于 `uvloop` 的，`uvloop` 又是 linux only 的，因此在 windows 环境下，会使用 `asyncio` 来代替 `uvloop`。 性能会下降，因此不建议在 windows 的生产环境下部署 misuzu。

## 最小的使用

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

## 调试模式
 TODO: watchdog and signal on windows

## 路由系统
在编写 API 时，权限是比较重要的一部分，尤其是在设计 RESTFUL API 时，因此 misuzu 提供了精准、优雅的路由定义方法。

在 misuzu 中，允许用户定义大部分请求方法： `HEAD`, `GET`, `POST`, `PUT`, `DELETE`, `HEAD`, `PATCH`, `OPTIONS`。 每一种请求方法都对应着一个装饰器来绑定 URL
```python

@app.get('/')
async def index(request):
    return Response("hello world.", content_type="text/html")

@app.post('/')
async def index_post(request):
    return Response("hello world with post mothod.", content_type="text/html")
```

### 带变量的路由
lalalal
## 参数定义

## 重定向 和 HTTP 错误

 TODO
## 请求类

## 回应类

## 使用 nginx 部署