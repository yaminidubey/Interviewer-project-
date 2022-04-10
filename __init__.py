# -*- coding: utf-8 -*-

from flask import Flask
from celery import Celery
from flask.ext.mongoengine import MongoEngine
from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView, filters
from flask.ext.redis import Redis
from flask.ext.elastic import Elastic

from .extensions.flask_redisscripts import RedisScriptContainer

import jinja2
import os

import logging
from logging.handlers import SMTPHandler

admin = Admin()
db = MongoEngine()
rc = Redis()
rscripts = RedisScriptContainer()
es = Elastic()

def create_app(package_name='mordor', config_name='Development'):
    """Returns a :class:`Flask` application instance configured with common
    functionality for the mordor platform.

    :param package_name: application package name
    :param package_path: application package path
    :param config_name: can have one of [production, development, testing]
    """
    
    app = Flask(package_name, instance_relative_config=True)
    if os.environ.get('mordor_CONFIG_NAME') == 'Production':
        config_name = 'Production'

    app.config.from_object('configurations.%s'%config_name.title())

    app.jinja_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader('mordor/templates/'),
    ])

    db.init_app(app)
    rc.init_app(app)
    es.init_app(app)
    admin.init_app(app)
    
    rscripts.init_app(app, rc)
    from views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    mail_handler = SMTPHandler((app.config['MAIL_SERVER'], app.config['MAIL_PORT']), 
        'admin@reviews42.com', app.config['ADMINS'], '[mordor] phat gaya', 
        (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),(None, None))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    
    return app


def create_celery_app(app=None):
    app = app or create_app()
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

from mordor import models
from mordor import tasks
from mordor import views
admin.add_view(ModelView(models.User))
admin.add_view(ModelView(models.Problem))