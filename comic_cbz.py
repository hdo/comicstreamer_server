import os
import zipfile
import csconfig
import thumb_provider
import id_provider
import time

class ComicBookCBZ:

    def __init__(self, file_name):
        self.file_name = file_name
        if not os.path.exists(self.file_name) or not os.path.isfile(self.file_name):
            return False
        self.file_id = id_provider.get_or_create_id_for_book(self.file_name)

    def accept_page(self, file_name):
        if file_name.lower().endswith(".png"):
            return True
        if file_name.lower().endswith(".jpg"):
            return True
        return False

    def prepare_thumbnails(self):
        output_dir = os.path.join(csconfig.CSServerConfig.thumbnail_path, self.file_id)
        #print output_dir
        counter = 0
        for item in self.page_list:
            #thb_name = 'thumb_%03d.jpg' % counter
            #print thb_name
            thumb_provider.ThumbProvider.create_thumbnail(self.file_id, item, self.zip_file, counter)
            counter = counter + 1
        #print self.file_id

    def open(self):
        # check for file existance
        self.zip_file = zipfile.ZipFile(self.file_name, 'r')
        self.page_list = []
        for item in sorted(self.zip_file.namelist()):
            if self.accept_page(item):
                self.page_list.append(item)
        self.prepare_thumbnails()
        return True

    def close(self):
        return True

    def debug_print(self):
        for item in self.page_list:
            data = self.zip_file.read(item)
            print item
            print len(data)


cb = ComicBookCBZ('/data/hdo/comicstreamer/repo/Der kleine Spirou/Der kleine Spirou - 01.cbz')
cb.open()
cb2 = ComicBookCBZ('/data/hdo/comicstreamer/repo/Der kleine Spirou/Der kleine Spirou - 02.cbz')
cb2.open()
#cb.debug_print()
thumb_provider.JobManager.start()
while True:
    time.sleep(5)
