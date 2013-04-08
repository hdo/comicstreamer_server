import os
import urllib
import plistlib

repo_path = '/Users/huy/projects/comicstreamer/repo'


def getItem(fname):
    oid = urllib.quote(fname)
    ret = {}
    abs_path = os.path.join(repo_path, oid)
    #print abs_path
    ret['oid'] = oid
    ret['url'] = '/list?oid=%s' % (oid)
    itype = 'file'
    if os.path.isdir(abs_path):
        itype = 'folder'
    else:
        if abs_path.endswith('.zip') or abs_path.endswith('.cbz'):
            itype = 'book'
    ret['type'] = itype
    return ret


def dict2plist(d):
    print plistlib.writePlistToString(d)


allitems = {}
allitems['oid'] = '/'
allitems['type'] = 'folder'
items = []
allitems['items'] = items
for element in sorted(os.listdir(repo_path)):
    items.append(getItem(element))
#for element in items:
#   print items
#print allitems
dict2plist(allitems)
