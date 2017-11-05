# Nougat
Nougat is an asynchronous web framework based on Python3.6 and curio, which focus on enhancing the experience of asynchronous web developing

At the beginning, the main point of Nougat is changing the way of writing Restful API by dividing the definition of parameters and the logic of controller

Another point is that Nougat can provide an automatical generator for API document, which has a lots templates
 
However, with the development of Nougat, it was seperated into two parts - the basic framework with Router and Middleware and the Restful Extension, which can let itself more popular and be highly extendable.

The reason choosing curio as event loop framework is that curio provides a straightforward way to handle asynchronous function, forgoing the Callback based Future task of asyncio. 
## Installation
Nougat relays on Python3.6 and DOES NOT support the elder version, which is hosted at Pypi. So you can install stable version through:
```bash
pip3 install nougat
```
#### Develop Version
if you wanna test the new feature of Nougat, you can install it from Github:
<p class="warning">
  In Develop Verson it would has some unknown bugs and unstable factors, SO PLEASE CHOOSE IT DELIBERATELY!
</p>
```bash
pip3 install git@github.com:Kilerd/nougat.git@develop
```

### Minimal Usage
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

### Get Started
from the above sample, we can see something important:
 - `Nougat` the entrance of entire framework, controlling all middlewares, guarders and router. At the same time, it also is used to start the server.
 - `Routing` used to define some route, which is similar as `Blueprint`

after creating the instance of `Nougat`, the routing would be activated only after registering to Nougat application. `app.route(MainRouting)` means registering `MainRouting` to `app`. notices that the parameter is class propotype, not the class instance.
`app.run(debug=True)` is used to start server with debug mode.

#### the steps of using Nougat
 1. Create`Nougat`instance
 2. Write Routes and group them into `Routing`
 3. Write some middlewares
 4. Register middlewares to `Nougat`
 5. Register routings to `Nougat`
 6. Start the server

### Nougat Class

the most import class in Nougat is `Nougat`. it controlls almost everythings: middlewares, routes and guardrs etc, and starts or stops the server
```python
app = Nougat()
```
#### Register middlewares to `Nougat`
`app.use()` is used to register middleware, the detail of middleware, please read the middleware part
```python
async def middleware(context, next):

    await next()

app.use(middleware)
```
#### Register guarders to `Nougat`
The meaning of guarder function is controlling the controller distinctly, which is based Dependency Injection.
`app.guarders()` is used to register guarder function
```python
async def some_guarder():
    pass

app.guarders(some_guarder)  # OK
app.guarders([some_guarder])  # Perfect
```
#### Register routings to `Nougat`
```python

class OneRouting(Routing):
    pass

app.route(OneRouting)
```

#### Start Server
```python
app.run(debug=True)
```
### Configuration


## Routing
### Request & Response
### Decorators
### Advanced Usage

## Middleware
### Sample

#### Logging the process time

## Guarder

