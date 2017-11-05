---
nav: chinese
title: 首页
---
# Nougat
Nougat 是一款基于 Python3.6 和 Curio 的异步 web 框架。主要目的是提升异步环境下的 Web 编写体验。

Nougat 一开始的初衷是优化 Restful API 的编写，主要目标在于分离 API 参数的定义和业务逻辑的分离，实现高度解耦化。

Nougat 的另外一个目的在于可供一份自动化的 API 文档，并且可以选择性地输出成预设的模版。
 
不过，随着 Nougat 的发展，Nougat 逐渐被分离成两个部分，基础由带路由组件和基于中间件的基础框架；另一部分由 Restful 扩展组成。这样做的目的在于可以使 Nougat 更加大众化，并且可以提供较高的扩展性。

选择 Curio 的原因在于 Curio 提供了一种较为直接的异步处理手法（当然啦，在日常的使用中是比较难体验出来的），放弃了 asyncio 中使用的那种基于回调的 Future Task 处理手法。这一选择带来的方便之处在于使 async/await 的处理更加直接，同时也打来了不少弊端：生态圈略差，可用的库比较少、在同步和异步代码之间做交互比较麻烦（这点在做已有同步库的 Curio 支持时就很明显了）
## 安装
Nougat 依赖于 Python3.6，并且不提供向下兼容模块，同时托管于 Pypi，可以通过一下指令下载到稳定版本：
```bash
pip3 install nougat
```
#### 开发者版本
如果你想体验 Nougat 的最新特性，你可以直接从 Github 代码中安装：
<p class="warning">
  Develop 版本可能含有不知名的 BUG 和某些不稳定因素，请慎重考虑是否需要使用开发者版本
</p>
```bash
pip3 install git@github.com:Kilerd/nougat.git@develop
```

### 最简单的使用
```python
from nougat import Nougat, Routing, get

app = Nougat()

class MainRouting(Routing):

    @get('/')
    async def index(self):
        return 'Hello world'

app.route(MainRouting)

app.run(debug=True)
```

### 简单教程
从上述例子中，可以看到有几个类是十分重要的：
 - `Nougat` 这个是整个框架的入口，控制着所有的中间件、守护函数、路由器，同时也作为启动服务的入口
 - `Routing` 用于定义一组路由，可以简单的理解为`Blueprint`

在创建了`Nougat`的实例后，需要向实例中注册路由才可生效。`app.route(MainRouting)`就是把`MainRouting`注册到`app`这个实例中，注意这里传入的是类原型而不是类实例

`app.run(debug=True)` 以调试模式启动服务器

#### 用 Nougat 做开发的一般步骤
 1. 创建`Nougat`实例
 2. 编写路由，并用`Routing`按模块组织起来
 3. 编写若干中间件
 4. 向`Nougat`注册中间件
 5. 向`Nougat`注册路由
 6. 启动服务器

### Nougat 类

Nougat 中最重要的就是 `Nougat` 类。它管理着你应用中的所有东西：中间件、路由器、守护函数等等，并且由它来启动或停止服务器
```python
app = Nougat()
```
#### 注册中间件
`app.use()` 函数用于向实例中注册中间件，详情内容请看 中间件部分
```python
async def middleware(context, next):

    await next()

app.use(middleware)
```
#### 注册守护函数
守护函数的意义在于给予路由的控制器独立的判断函数，守护函数是由依赖注入来实现的

`app.guarders()` 用于注册守护函数
```python
async def some_guarder():
    pass

app.guarders(some_guarder)  # OK
app.guarders([some_guarder])  # Perfect
```
#### 注册路由
```python

class OneRouting(Routing):
    pass

app.route(OneRouting)
```

#### 启动服务器
```python
app.run(debug=True)
```
### 配置文件


## Routing
### Request & Response
### Decorators 装饰器
### 高级使用

## 中间件
### 例子

#### 记录处理时间

## 守护者 Guarder

