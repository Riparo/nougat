# 中间件 Middleware

## 基本使用
```python
from nougat import BaseMiddleware

class MyMiddleware(BaseMiddleware):

    def on_request(self, request):
        ...
    
    def on_response(self, response):
        ...
```

以上代码实现了一个中间件的定义：
 - 继承于 `BaseMiddleware`
 - 重写 `on_request` 和 `on_response` 方法

## 请求中间件 on_request

该方法触发于处理函数 handler 之前，只可以操作 request 对象。

## 响应中间件 on_response

该方法触发于处理函数 handler 之后，只可以操作 response 对象。


## 注册中间件
中间件可以注册在 Nougat 或者 Section 中，都是调用 `register_middleware` 方法

### 中间件执行顺序

中间件链(chain) 保证了中间件是按注册顺序执行的： 首先执行 Nougat 中的中间件，再执行 Section 中的中间件
```python
app.register_middleware(a1)
app.register_middleware(a2)

section.register_middleware(s1)
section.register_middleware(s2)

app.register_section(section)
```

以上代码的中间件执行顺序为(如同递归)：

`a1.on_request` -> `a2.on_request` -> `s1.on_request` -> `s2.on_request` -> `handler` -> `s2.on_response` -> `s1.on_response` -> `a2.on_response` -> `a1.on_response`

**中间件的 `__init__` 方法会正常被调用**

## 一个记录处理函数执行时间的简单中间件
```python
from nougat import BaseMiddleware
from time import time
class MyMiddleware(BaseMiddleware):

    def on_request(self, request):
        self.start_time = time()
    
    def on_response(self, response):
        end_time = time()
        process_time = end_time - self.start_time

        # write process_time in cookies or header or whatever you want
```
