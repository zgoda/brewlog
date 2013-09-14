from stat import S_ISREG, ST_CTIME, ST_MODE
import os

def sorted_directory_listing(dirname):
    entries = (os.path.join(dirname, fn) for fn in os.listdir(dirname))
    entries = ((os.stat(path), path) for path in entries)
    entries = ((stat[ST_CTIME], path) for stat, path in entries if S_ISREG(stat[ST_MODE]))
    return sorted(entries)
