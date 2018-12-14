from apps.libs.yuntongxun.sms import CCP
from apps.tasks.main import celery_app

@celery_app.task
def send_sms(to, data, temp_id):
  """celery异步发送短信"""
  ccp = CCP()
  ccp.send_tempalte_sms(to, data, temp_id)