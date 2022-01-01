from pathlib import Path
from objs import Filter, Snapshot
import os.path as osp

# main trigger function
def takeSnapshotOf(path: str, query: Filter, showFiles: bool=False) -> Snapshot:
    from pool import Blink
    if not osp.exists(path):
        print(f"{path} was not found.")
        return None

    n_path = Path(path)
    # make thread pool
    bl = Blink();
    files, runtime, threadCount = bl.run(n_path, query)
    return Snapshot(path, query, files, runtime, showFiles, threadCount)

def enumerateItemsAt(path: Path, query: Filter):
    items = []
    for item in path.iterdir():
        if item.is_file() and matchesFilter(path.name, query):
            # enumerate a file that passes query
            items.append(('file', item)) 
        elif item.is_dir():
            # enumerate a directory to be visited
            items.append(('dir', item)) 
    return items

# used for matching strings to query term
def doesContain(string: str, substr: str) -> bool:
    r = string.find(substr)
    match r:
        case -1: # does not contain
            return False
        case _: # does contain
            return True

def doesEndWith(string: str, terminator: str) -> bool:
    return string.endswith(terminator)

def doesStartWith(string: str, head: str) -> bool:
    return string.startswith(head)

matchTypes = {
    'contains': doesContain,
    'endswith': doesEndWith,
    'startswith': doesStartWith
}

def matchesFilter(string: str, qu: Filter):
    match qu:
        case None: # no query
            return True
        case Filter(term=qTerm, matchType=matchType): # some query
            if qTerm == "*": # used for matching all files
                return True
            matchFn = matchTypes[matchType]
            return matchFn(string, qTerm)