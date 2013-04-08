import os


class CSServerConfig:

    cs_path = '/data/hdo/comicstreamer'
    tmp_path = os.path.join(cs_path, 'tmp')
    cache_path = os.path.join(cs_path, 'cache')
    thumbnail_path = os.path.join(cache_path, 'thumbs')
    db_path = os.path.join(cs_path, 'db')
    repo_path = '/data/hdo/comicstreamer/repo'

    @classmethod
    def get_relative_path(cls, file_name):
        fname = file_name.replace(CSServerConfig.repo_path, '')
        if fname.startswith('/'):
            return fname[1:]
        return fname