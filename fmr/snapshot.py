from query import Query
from colorprinter import coprint
from matcha import MatchaPool
import os.path as osp
from pathlib import Path

# in the case where the directory files pass a threshold,
# it would be wiser to have some written away state that can be deleted after use

class Snapshot:
    """[summary]
    """
    def __init__(self, path, qu: Query, files, dur: int):
        self.newFiles = {}
        self.files = files
        self.dur = dur
        self.path = path
        self.qu = qu
    
    def containedFiles(self):
        cp = self.files.copy()
        cp.update(self.newFiles)
        return cp
        
    def updateSnapshot(self, otherSnap):
        # this function will be used when 2 snapshots need to
        # be merged 
        # this is achieved by:
        # a = set(caller.files)
        # b = set(other.files)
        # a.files = list(a-b)
        # a.newFiles = list(b-a)
        otherFiles = otherSnap.containedFiles()
        others = set(otherFiles)
        slf = set(self.containedFiles())
        
        new = others - slf
        deleted = slf - others

        self.files.update(self.newFiles)
        self.newFiles = {}
        if deleted:
            for d in deleted:
                del self.files[d]

        if new:
            for n in new:
                self.newFiles[n] = otherFiles[n]
            return True
        else:
            return False


    def printContainedDetails(sn, hideFileContents=False):
        if sn.qu.keyword == "**":
            print(f"Finding every file at {sn.path}")
        else:
            print(f"{sn.path} with Query[{sn.qu.searchType} {sn.qu.keyword}]")
        print(f"Query completed on index in {sn.dur}.")

        fileCount = len(sn.containedFiles())

        folders = {}
        for f in sn.containedFiles().values():
            paren = osp.split(f)[0]
            internalFiles = folders.get(paren, [])

            if internalFiles == []:
                internalFiles.append(f)
                folders[paren] = internalFiles
            else:
                internalFiles.append(f)
        
        folderCount = len(folders.keys())

        if not hideFileContents:
            for k, v in folders.items():
                print(k)
                for indx in range(len(v)):
                    item = v[indx]
                    if indx == len(v)-1:
                        stamp = '└──'
                    else:
                        stamp = '├──'

                    col = None
                    attrb = ['bold']
                    if item in sn.newFiles:
                        col = 'green'
                    else:
                        col = 'white'
                    coprint('\t'+stamp+item.name, col, attrb=attrb) 
                print()
        print(f"this snapshot contains {fileCount} file(s).")
        print(f"found in {folderCount} unique folder(s)")

    # ############################################################################### #
    # ############################################################################### #
    @staticmethod
    def snapshotFromPath(path: str, query = None, display=False, checkDirs=True):
        if display: print('Snapshotting ', path)
        if not osp.exists(path):
            print(path, 'not found.')
            return None
        # update server state for client side to read and know that server is currently running
        
        fileObjs = {}

        if (type(path) == str):
            path = Path(path)
        
        mp = MatchaPool(display, checkDirs)
        fileObjs, duration = mp.run(path, query)
        return Snapshot(path, query, fileObjs, duration)

    @staticmethod
    def _itemsInDir(path: Path, query: Query, display=False, checkDirs=True):
        diritems = []
        for diritem in path.iterdir():
            if diritem.is_file() and Snapshot._filterFilesByQuery(diritem, query):
                diritems.append(('f', diritem))

            elif checkDirs and diritem.is_dir():
                diritems.append(('d', diritem))

        return diritems

    # ############################################################################### #
    # this function checks a file path (shortened file name)
    # to see if it contains the keyword
    @staticmethod
    def _filterFilesByQuery(path, criteriaQuery: Query):
        if criteriaQuery:
            queryTerm = criteriaQuery.keyword
            searchType = criteriaQuery.searchType

            if  queryTerm == '**':
                return True

            queryActions = {
                'contains': Snapshot._contains,
                'endswith': Snapshot._endswith,
                'startswith': Snapshot._startswith
            }

            action = queryActions[searchType]
            result = action(path.name, queryTerm)
            return result
        else: return True

    def _contains(A, sub):
        r = A.find(sub)

        if r == -1:
            return False
        else:
            return True

    def _endswith(A, sub):
        return A.endswith(sub)

    def _startswith(A, sub):
        return A.startswith(sub)
