from os import cpu_count
from pathlib import Path
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import get_ident
from objs import Filter
from snap import enumerateItemsAt

class Pool:
    def __init__(p):
        # tasks to be completed
        p.tasks = Queue()
        # completed tasks
        p.completed = Queue()
        # printer queue for synchronizing printing
        p.printable = Queue()
        # terminator for all threads, passed into queues
        p.terminator = (None, None)
        # track thread IDs used for job
        p.tIDs = set()
        # create threads for upcoming job function
        p.configure()

    def configure(p):
        p.max_thread_count = int(cpu_count() * 1.5)
        p.executor = ThreadPoolExecutor(p.max_thread_count)

class Blink(Pool):
    def __init__(bl):
        super().__init__()

    def arachnid(bl):
        # track this arachnid
        bl.tIDs.add(get_ident())
        # tasks loop
        while not bl.tasks.empty() or True:
            try:
                path, query = bl.tasks.get()

                match (path, query):
                    case (None, None): # end thread
                        bl.tasks.task_done()
                        bl.tasks.put(bl.terminator)
                        break
                    case _: # process path's contents
                        for itype, item in enumerateItemsAt(path, query):
                            if itype == "file":
                                bl.completed.put(item)
                            elif itype == "dir":
                                bl.tasks.put((item, query))
            except Exception as e:
                print(e)
                break
            bl.tasks.task_done()

    def run(bl, path: Path, query: Filter):
        # set first task
        start = datetime.now()
        bl.tasks.put((path, query))
        for _ in range(bl.max_thread_count):
            bl.executor.submit(bl.arachnid)

        # terminate all threads after tasks are done
        bl.tasks.join()
        bl.tasks.put(bl.terminator)

        bl.executor.shutdown(wait=False)
        end = datetime.now()
        
        # collect accumulated results
        results = {}
        for file in list(bl.completed.queue):
            results[str(file)] = file
        # return results and duration
        return (results, end - start, len(bl.tIDs))