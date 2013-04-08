class BookCache():

   cacheobjects = {}

   @staticmethod
   def getBook(oid):
      if BookCache.cacheobjects.has_key(oid):
         return BookCache.cacheobjects[oid]
      return

   @staticmethod
   def putBook(oid, book):
      BookCache.cacheobjects[oid] = book
      return      