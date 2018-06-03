from typing import Callable, List, Dict, Awaitable, TYPE_CHECKING
import asyncio
if TYPE_CHECKING:
    from nougat import Nougat

SignalType = Callable[['Nougat'], Awaitable[None]]


class Signal:

    def __init__(self, app: 'Nougat'):

        self.app: 'Nougat' = app
        self.handlers: Dict[str, List[SignalType]] = {}

    def listen(self, signal_name: str):

        def add_signal_handler(func: SignalType):
            if signal_name not in self.handlers:
                self.handlers[signal_name] = []

            self.handlers[signal_name].append(func)

        return add_signal_handler

    async def activate(self, signal_name: str):

        for handler in self.handlers.get(signal_name, []):
            if asyncio.iscoroutinefunction(handler):
                await handler(self.app)
            else:
                handler(self.app)
