from os import cpu_count
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import get_ident

class MatchaPool:
    def __init__(s, display=False, checkDirs=True):
        # this queue contains all paths that can visited by threaded functions
        s.candidatesQueue = Queue()
        # this queue contains all files that have been matched so far
        s.matchesQueue = Queue()
        # used for writing output out to terminal from other threads (independent thread)
        s.outputQueue = Queue()
        # this queue contains all paths that we've already seen 
        s.visitedQueue = Queue()
        
        s.poison_pill = (None, None)
        s.display = display
        s.checkDirs = checkDirs
        s.tIDs = set()

    def fileMatcha(s):
        from snapshot import Snapshot as sn
        s.tIDs.add(get_ident())
        while not s.candidatesQueue.empty() or True:
            try:
                path, query = s.candidatesQueue.get()

                if (path, query) == s.poison_pill:
                    s.candidatesQueue.task_done()
                    s.candidatesQueue.put(s.poison_pill)
                    break
                
                # if path not in list(s.visitedQueue.queue):
                for itemtype, item in sn._itemsInDir(path, query, display=s.display, checkDirs=s.checkDirs):
                    if itemtype == 'f':
                        s.matchesQueue.put(item)
                        # s.outputQueue.put((get_ident(), item))
                    elif itemtype == 'd':
                        s.candidatesQueue.put((item, query))
                    # s.visitedQueue.put(path)
            except Exception as e:
                print(e)
                break                
            s.candidatesQueue.task_done()

    def printer(s):
        for tID, path in iter(s.outputQueue.get, s.poison_pill):
            print(tID, '->', path)

    def run(s, path, query):
        lent = int(cpu_count() * 1.5)
        exc = ThreadPoolExecutor(lent)
        s.candidatesQueue.put((path, query))
        now = datetime.now()

        for _ in range(lent):
            exc.submit(s.fileMatcha)

        # exc.submit(s.printer)

        s.candidatesQueue.join()
        s.candidatesQueue.put(s.poison_pill)
        # s.outputQueue.put(s.poison_pill)
        exc.shutdown(wait=False)

        later = datetime.now()

        dct = {}
        for f in list(s.matchesQueue.queue):
            dct[str(f)] = f

        dur = later-now
        # print(f"{len(s.tIDs)} unique threads finished job in {dur} time...")
        return (dct, dur)