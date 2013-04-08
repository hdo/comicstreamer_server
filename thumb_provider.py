import os
import sqlite3
import csconfig
import subprocess
import thread
import time


class JobManager:

    job_list = []
    running = False

    @classmethod
    def add_job(cls, job):
        for item in JobManager.job_list:
            if item.is_equal(job):
                return
        JobManager.job_list.append(job)

    @classmethod
    def threadrunner(cls):
        while len(JobManager.job_list) > 0:
            current_job = JobManager.job_list.pop(0)
            print "running job %s" % current_job.jobid
            current_job.run()
            time.sleep(0.2)

    @classmethod
    def start(cls):
        if not JobManager.running:
            JobManager.running = True
            thread.start_new_thread(JobManager.threadrunner, ())
            while True:
                time.sleep(5)
                print "Thread hearbeat ..." 
                print "%d jobs remaining " % len(JobManager.job_list)


class ResizeJob:

    def __init__(self, file_id, org_name, data_provider, output_file):
        self.file_id = file_id
        self.org_name = org_name
        self.data_provider = data_provider
        self.output_file = output_file
        self.priority = 0.0
        self.jobid = output_file

    def create_thumbnail_to_file(self):
        p = subprocess.Popen(['convert', '-resize', '240x240', '-', '%s' % self.output_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        image_data = self.data_provider.read(self.org_name)
        p.communicate(image_data)

    def run(self):
        self.create_thumbnail_to_file()
        ThumbProvider.add_thumbnail(self.file_id, self.org_name, self.output_file)

    def is_equal(self, other_job):
        if self.jobid == other_job.jobid:
            return True
        else:
            return False


class ThumbProvider:

    databasefile = os.path.join(csconfig.CSServerConfig.db_path, 'thumbs.db')

    @classmethod
    def get_table_name(cls, file_id):
        return "THUMBS_%s" % file_id

    @classmethod
    def is_table_available(cls, file_id):
        sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s'" % (ThumbProvider.get_table_name(file_id))
        conn = sqlite3.connect(ThumbProvider.databasefile)

        cur = conn.execute(sql)
        ret = int((cur.fetchone()[0]))
        conn.close()
        if ret == 1:
            return True
        return False

    @classmethod
    def is_thumbnail_available(cls, file_id, org_name):
        if not ThumbProvider.is_table_available(file_id):
            print "table not available"
            return False
        conn = sqlite3.connect(ThumbProvider.databasefile)

        sql = "select thumb_file from %s where org_name = ?" % (ThumbProvider.get_table_name(file_id))
        p = (org_name,)
        cur = conn.execute(sql, p)
        res = cur.fetchone()
        conn.close()
        if res:
            return True
        return False

    @classmethod
    def add_thumbnail(cls, file_id, org_name, thumb_file):
        conn = sqlite3.connect(ThumbProvider.databasefile)

        if not ThumbProvider.is_table_available(file_id):
            sql = "create table if not exists %s (org_name text, thumb_file text)" % ThumbProvider.get_table_name(file_id)
            conn.execute(sql)
            conn.commit()
        sql = "insert into %s values (?,?)" % (ThumbProvider.get_table_name(file_id))
        p = (org_name, thumb_file)
        conn.execute(sql, p)
        conn.commit()
        conn.close()
        return True

    @classmethod
    def create_thumbnail(cls, file_id, org_name, data_provider, index):
        output_dir = os.path.join(csconfig.CSServerConfig.thumbnail_path, file_id)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        thb_name = 'thumb_%03d.jpg' % index
        output_file = os.path.join(output_dir, thb_name)

        rJob = ResizeJob(file_id, org_name, data_provider, output_file)
        JobManager.add_job(rJob)
        return True

#    @classmethod
#    def prepare_thumbnails(cls, file_id, org_)

#print is_thumbnail_available('0815', '00.jpg')
