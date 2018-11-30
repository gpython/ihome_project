#encoding:utf-8

#图片验证码 redis有效期 单位 秒
IMAGE_CODE_REDIS_EXPIRES = 180

#短信验证码的redis有效期 单位 秒
SMS_CODE_REDIS_EXPIRES = 300

#发送短信验证码间隔
SEND_SMS_CODE_INTERVAL = 60

#登录错误尝试次数
LOGIN_ERROR_MAX_TIMES = 5

#登录错误限制的时间 单位 秒
LOGIN_ERROR_FORBID_TIME = 600

QINIU_URL_DOMAIN = "http://o91qujnqh.bkt.clouddn.com/"


HOUSE_DETAIL_DISPLAY_COUNTS = 10