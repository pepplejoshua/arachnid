from datetime import timedelta
import os.path as osp

# TODO: I can write a SnapshotDelta class as well to cover differencing on indexes
class OutputAssembler:
    def __init__(ca) -> None:
        ca.defTabSize = 4
        ca.body = [] 
        ca.tabSize = 0

    def insert(ca, line: str = ''):
        line = (ca.tabSize * " ") + line + "\n"
        ca.body.append(line);

    def unaddLastLine(ca):
        ca.body = ca.body[0:len(ca.body)-1]

    def dedent(ca):
        if (ca.tabSize > 0):
            ca.tabSize -= ca.defTabSize

    def indent(ca):
        ca.tabSize += ca.defTabSize

    def indentInsertDedent(ca, line: str):
        ca.indent()
        ca.insert(line)
        ca.dedent()

    def __str__(ca) -> str:
        return ''.join(ca.body)

class Filter:
    def __init__(f, term: str, matchType: str):
        f.term = term
        f.matchType = matchType
    
    def __repr__(f) -> str:
        return f"|{f.matchType} {f.term}|"

class Snapshot:
    def __init__(sn, searchPath: str, qu: Filter, 
                files: dict, searchTime: timedelta, 
                showFiles: bool, threadCount: int):
        sn.path = searchPath
        sn.query = qu
        sn.files = files
        sn.searchTime = searchTime
        sn.showFileStruc = showFiles
        sn.workersCount = threadCount
    
    def __repr__(sn) -> str:
        asm = OutputAssembler()
        if sn.query.term == "*":
            asm.insert(f"Finding every file at {sn.path}")
        else:
            asm.insert(f"{sn.path} with {sn.query}")
        asm.insert(f"{sn.workersCount} arachnids were used...")
        asm.insert(f"Filter completed on index in {sn.searchTime}.")

        sourceFolders = {}
        for file in sn.files.values():
            parent = osp.split(file)[0]
            filesAtParent = sourceFolders.get(parent, [])

            # parent not seen before
            if filesAtParent == []:
                filesAtParent.append(file)
                sourceFolders[parent] = filesAtParent
            else:
                filesAtParent.append(file)
            
        filesCount = len(sn.files)
        foldersCount = len(sourceFolders.keys())

        if sn.showFileStruc:
            for parent, files in sourceFolders.items():
                asm.insert(parent) # record parent
                # then record contained children
                for index, file in enumerate(files):
                    # if we are at the last file
                    tree: str
                    if index == len(files)-1:
                        tree = '└──'
                    else:
                        tree = '├──'
                    asm.indentInsertDedent(f"\t{tree}{file.name}")
        
        asm.insert(f"this snapshot contains {filesCount} file(s).")
        asm.insert(f"found in {foldersCount} unique folder(s).")
        return str(asm)
