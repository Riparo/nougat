# 部件 Section

## 基本使用
`main = Section('mian')`

## 参数

- 部件名称
  部件名称用以区分不同的模块，允许在其他部件中使用部件名称获得内部路由的URL


## 中间件

**详情请看[中间件页面](/zh-cn/middleware)**

部件中的中间件不同于 Nougat 中的中间件：
 - Nougat 的中间件是永远都会执行的
 - 部件的中间件只有当部件中某个处理函数被触发时才触发。

例如：

路由 `/` 由 部件 `main` 创建， 路由 `/user` 由 部件 `user` 创建：
 - 当访问 `/` 时， Nougat 和 部件 `main` 的中间件被触发
 - 当访问 `/user` 时， Nougat 和 部件 `user` 的中间件被触发
 - 当访问 `/not` 时， Nougat 的中间件被触发

### 注册中间件
通过部件中的`register_middleware`方法进行注册

## 向 Nougat 注册部件
```python
app.register_section(section)
```
