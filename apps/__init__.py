import redis
import logging
from flask import Flask
from config import  config_map
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from logging.handlers import RotatingFileHandler
from apps.utils.commons import ReConverter

#MySQL数据库
db = SQLAlchemy()

#Redis数据库
rdb = None

#为flask补充csrf防御机制
csrf = CSRFProtect()

#设置日志记录等级
logging.basicConfig(level=logging.DEBUG)
#创建日志记录器 指明日志保存路径 每个日志文件最大大小 保存日志文件上限个数
file_log_handler = RotatingFileHandler("logs/ihome.log", maxBytes=1024*1024*1024, backupCount=10)
#c创建日志记录格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
#为创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
#为全局的日志工具对象(flask app使用的) 添加日志记录
logging.getLogger().addHandler(file_log_handler)


#工厂函数
def create_app(config_name):
  """
  创建flask应用
  :param config_name: str 配置模式名字（'develop', 'product'）
  :return:
  """
  app = Flask(__name__)

  #根据参数获取配置模式的类
  config_class = config_map.get(config_name)
  app.config.from_object(config_class)

  #使用app初始化 MySQLdb
  db.init_app(app)

  #Redis数据库
  global rdb
  rdb = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

  #利用flask_session 将session对象存储到redis中
  Session(app)
  #为flask补充csrf防护
  # CSRFProtect(app)
  csrf.init_app(app)

  #为flask添加自定义的转换器
  app.url_map.converters['re'] = ReConverter

  #注册蓝图 蓝图可能会用到上边注册到app中的应用
  from apps import  api_1_0
  app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

  #注册提供静态文件的蓝图
  from apps import web_html
  app.register_blueprint(web_html.html)

  return app


