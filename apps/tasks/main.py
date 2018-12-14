from celery import Celery
from apps.tasks import config

#定义celery对象
celery_app = Celery("ihome")

#引入配置信息
celery_app.config_from_object(config)

#自动搜寻异步任务 可能有多个定义名为tasks.py的任务包 的包名字
#自动去包apps.tasks.sms 中寻s找tasks.py文件并导入
celery_app.autodiscover_tasks(["apps.taks.sms"])