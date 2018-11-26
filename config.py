import redis


class Config(object):
  #配置信息
  SECRET_KEY = 'sdsfdSDDFRGdkfdjksdkjixkls-9e95-0'

  #database
  SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:abc12345@192.168.9.55:3306/ihome"
  SQLALCHEMY_TRACK_MODIFICATIONS = True

  #redis
  REDIS_HOST = '192.168.9.55'
  REDIS_PORT = 6379

  #flask-session配置
  SESSION_TYPE = 'redis'
  SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
  SESSION_USE_SIGNER = True #对cookie中session_id进行隐藏处理
  PERMANENT_SESSION_LIFETIME = 86400 #sessions数据有效期 单位秒


class DevelopmentConfig(Config):
  #开发环境配置
  DEBUG = True #Debug模式会强制覆盖掉自己设置的logging的日志模式

class ProductionConfig(Config):
  #生产环境配置
  pass

config_map = {
  'develop': DevelopmentConfig,
  'product': ProductionConfig
}