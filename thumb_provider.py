import os
import sqlite3
import csconfig
import subprocess
import thread
import time


class JobRunner:
    def __init__(self, runner_id):
        self.current_job = None
        self.runner_id = runner_id

    def is_ready(self):
        if self.current_job:
            return False
        return True

    def notify_status(self, status):
        if status == 0:
            self.current_job = None

    def process_job(self, job):
        if not self.current_job:
            self.current_job = job
            print "running job %s with runner id %d ..." % (job.jobid, self.runner_id)
            thread.start_new_thread(job.run, (self,))


class JobManager:

    waiting_jobs = []
    running_jobs = []
    running = False

    @classmethod
    def add_job(cls, job):
        for item in JobManager.waiting_jobs:
            if item.is_equal(job):
                return
        JobManager.waiting_jobs.append(job)


    @classmethod
    def get_free_slot(cls):
        for jRunner in JobManager.running_jobs:
            if jRunner.is_ready():
                return jRunner
        None


    @classmethod
    def threadrunner(cls):
        while True:
            if len(JobManager.waiting_jobs) > 0:
                current_job = JobManager.waiting_jobs.pop(0)
                slot = JobManager.get_free_slot()
                while not slot:
                    time.sleep(0.1)
                    slot = JobManager.get_free_slot()
                slot.process_job(current_job)

    @classmethod
    def start(cls):
        if not JobManager.running:
            JobManager.running_jobs.append(JobRunner(1))
            JobManager.running_jobs.append(JobRunner(2))
            JobManager.running_jobs.append(JobRunner(3))
            #JobManager.running_jobs.append(JobRunner(4))
            #JobManager.running_jobs.append(JobRunner(5))
            JobManager.running = True
            thread.start_new_thread(JobManager.threadrunner, ())

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

    def run(self, status_listener):
        self.create_thumbnail_to_file()
        ThumbProvider.add_thumbnail(self.file_id, self.org_name, self.output_file)
        if status_listener:
            status_listener.notify_status(0)

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
