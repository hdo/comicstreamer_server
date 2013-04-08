import os
import urllib
import plistlib
import zipfile
import bookcache

repo_path = '/Users/huy/projects/comicstreamer/repo'

def get_abs_path(oid):
   fname = urllib.unquote(oid)
   if fname[0] == '/':
      fname = fname[1:]
   abs_path = os.path.join(repo_path, fname)
   return abs_path

def is_folder(oid):
   abs_path = get_abs_path(oid)
   if os.path.exists(abs_path) and os.path.isdir(abs_path):
      return True
   return False

def is_book(oid):
   abs_path = get_abs_path(oid)
   if not os.path.exists(abs_path) and not os.path.isfile(abs_path):
      return False
   if abs_path.endswith('.zip') or abs_path.endswith('.cbz'):
      return True
   return False

def getItem(oid):
   ret = {}
   abs_path = get_abs_path(oid)
   if not os.path.exists(abs_path):
      return
   #print abs_path
   ret['oid'] = oid
   ret['url'] = '/list?oid=%s' % (oid)
   itype = 'file'
   if is_folder(oid):
      itype = 'folder'
   elif is_book(oid):
      itype = 'book'
   ret['type'] = itype   
   return ret

def dict2plist(d):
   return plistlib.writePlistToString(d)

def getFolderList(oid, p):
   allitems = {}
   allitems['oid'] = oid
   allitems['type'] = 'folder'
   items = []
   allitems['items'] = items
   rel_p = urllib.unquote(oid)  
   for element in sorted(os.listdir(p)):
      if element[0] == '.':
         continue
      new_oid = urllib.quote(os.path.join(rel_p, element))
      items.append(getItem(new_oid))
   return allitems

def getZIPPageList(oid):
   co = bookcache.BookCache.getBook(oid)
   if co:
      return co
   abs_path = get_abs_path(oid)
   zf = zipfile.ZipFile(abs_path, 'r')
   res = sorted(zf.namelist())
   bookcache.BookCache.putBook(oid, res)
   return res


def getRARPageList(oid):
   return

def getPageList(oid):
   abs_path = get_abs_path(oid)
   if abs_path.endswith('.zip') or abs_path.endswith('.cbz'):
      return getZIPPageList(oid)
   if abs_path.endswith('.rar') or abs_path.endswith('.cbr'):
      return getRARPageList(oid)
   return


def getList(oid = ''):
   if not oid or len(oid) == 0:
      return dict2plist(getFolderList('', repo_path))

   if oid and len(oid) > 0:
      abs_path = get_abs_path(oid)
      if is_folder(oid):
         return dict2plist(getFolderList(oid, abs_path))
      if is_book(oid):
         return getPageList(oid)
      print abs_path
      

#print getList()
#print getList('mahou%20sensei%20negima')
print getList('mahou%20sensei%20negima/Mahou%20Sensei%20Negima%20-%20Vol%2003.zip')
print getList('mahou%20sensei%20negima/Mahou%20Sensei%20Negima%20-%20Vol%2003.zip')
print getList('mahou%20sensei%20negima/Mahou%20Sensei%20Negima%20-%20Vol%2003.zip')
