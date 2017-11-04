from watchdog.observers import Observer
from watchdog.events import FileSystemEvent
import curio

EVENT_TYPE_MOVED = 'moved'
EVENT_TYPE_DELETED = 'deleted'
EVENT_TYPE_CREATED = 'created'
EVENT_TYPE_MODIFIED = 'modified'


class AsyncFileSystemHandler:

    def __init__(self, queue):

        self.__queue = queue

    async def on_any_event(self, event):
        print("event happened")

    async def on_created(self, event):
        pass

    async def on_modified(self, event):
        pass

    async def on_moved(self, event):
        pass

    async def on_deleted(self, event):
        pass

    def dispatch(self, event):
        _method_map = {
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
        }
        curio.spawn(self.on_any_event(event))
        # self._loop.call_soon_threadsafe(asyncio.async, self.on_any_event(event))
        # self._loop.call_soon_threadsafe(asyncio.async, _method_map[event.event_type](event))


class AsyncFileWatcher:

    def __init__(self, path, event_handler, recursive=True):
        self._path = path
        self._event_handler = event_handler
        self.recursive = recursive

        self._observer = Observer()
        self._observer.schedule(self._event_handler, self._path, self.recursive)

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()


class AsyncFolderWatcher:

    def __init__(self, path, kernel, queue=None):
        self.__path =path
        self.__queue = queue or curio.Queue()
        self.__observer = None
        self.__kernel = kernel

    async def on_any_event(self, event):
        print("on any event happened")

    async def on_created(self, event):
        pass

        print("on created event happened")

    async def on_modified(self, event):
        pass

        print("on modified event happened")

    async def on_moved(self, event):
        pass
        print("on moved event happened")

    async def on_deleted(self, event):
        pass
        print("on deleted event happened")

    def dispatch(self, event):
        print("doing this")

        self.__kernel.run(self.on_any_event, event)

    async def worker(self):
        await self.__queue.get()
        print("event on")

    async def start(self, recursive=True):

        await curio.spawn(self.worker)

        self.__observer = Observer()
        self.__observer.schedule(self, self.__path, recursive)

        self.__observer.start()

    async def stop(self):

        self.__observer.stop()
        self.__observer.join()
