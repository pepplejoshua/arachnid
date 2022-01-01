from snapshot import Snapshot as Sn
from query import Query

path = "/Users/iwarilama/Desktop/Code/"
qu = Query("**", "endswith")
old = Sn.snapshotFromPath(path, qu)
old.printContainedDetails(True)