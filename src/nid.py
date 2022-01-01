from snap import takeSnapshotOf, Filter

path = "/Users/iwarilama/Desktop/Code/"
fl = Filter("*", "endswith")
new = takeSnapshotOf(path, fl)
print(new)