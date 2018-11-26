from . import api
from apps import db, models
from flask import current_app

@api.route('/index')
def index():
  current_app.logger.error('error')
  current_app.logger.warn('warn')
  current_app.logger.info('info')
  current_app.logger.debug('debug')
  return 'api 1.0 index page yes'