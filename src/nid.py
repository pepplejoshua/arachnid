from snap import takeSnapshotOf, Filter

path = "/Users/iwarilama/Desktop/Code/"
fl = Filter("*", "endswith")
sn = takeSnapshotOf(path, fl)
print(sn)