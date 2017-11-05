# from watchdog.observers import Observer
import curio

EVENT_TYPE_MOVED = 'moved'
EVENT_TYPE_DELETED = 'deleted'
EVENT_TYPE_CREATED = 'created'
EVENT_TYPE_MODIFIED = 'modified'


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

        # self.__observer = Observer()
        self.__observer.schedule(self, self.__path, recursive)

        self.__observer.start()

    async def stop(self):

        self.__observer.stop()
        self.__observer.join()
