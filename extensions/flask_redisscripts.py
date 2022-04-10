import os
import glob 

class RedisScriptContainer(object):
    def __init__(self, app=None):
        if app:
            self.app = app
            self.init_app(app)

    def init_app(self, app, connection):
        for script_path in glob.glob('beehive/redis_scripts/*.lua'):
            with open(script_path) as f: script = f.read()
            script_name = os.path.basename(script_path).split('.')[0]
            try:
                setattr(self, script_name, connection.register_script(script))
            except Exception as e:
                print script_name
                raise e
