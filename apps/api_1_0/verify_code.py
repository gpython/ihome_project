import random
from apps.libs.yuntongxun.sms import CCP
from . import api
from flask import current_app, jsonify, make_response, request
from apps.utils.captcha.captcha import captcha
from apps import rdb, constants, db
from apps.utils.response_code import RET
from apps.models import User
# from apps.tasks.task_sms import send_sms
from apps.tasks.sms.tasks import send_sms

#GET /api/v1.0/image_codes/<image_code_id>
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
  """
  获取图片验证码
  :param image_code_id: 图片验证码编号
  :return: 正常:返回验证码图片 异常:返回json
  """

  #生成验证码图片
  #名字 真实文本 图片数据
  name, text, image_data = captcha.generate_captcha()

  #验证码真实值与编号保存到redis中 设置有效期
  #redis: 字符串 列表 哈希 set
  #使用哈希维护有效期的时候只能整体设置　过期时间
  #"image_codes:"{"id1":"img1_data", "id2":"img2_data"}
  #hash
  #hset("image_define_name", "id1", "img1_data")
  #hset("image_define_name", "id2", "img2_data")

  #单条维护记录 使用字符串
  #"image_code_no1": "img1_data"
  #"image_code_no2": "img2_data"

  #rdb.set("image_code_%s" %image_code_id, text)
  #rdb.expire("image_code_%s" %image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)

  # 设置带有效期的key:value  记录名字                  有效期                       记录值
  try:
    rdb.setex("image_code_%s" %image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
  except Exception as e:
    #记录日志
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="save image code id failed")

  #返回图片
  resp = make_response(image_data)
  resp.headers['Content-Type'] = "image/jpg"
  return resp


#GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
  """
  短信验证码
  :param mobile: 正则表达式验证后 手机号
  :return:
  """
  #获取参数
  # image_code用户输入的验证码值
  # image_code_id 存入到redis数据库中的验证码图片对应的UUID值
  image_code = request.args.get("image_code")
  image_code_id = request.args.get("image_code_id")

  #校验
  if not all([image_code_id, image_code]):
    #表示参数不完整
    return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

  #业务逻辑处理
  #从redis中取出真实图片验证码
  try:
    real_image_code = rdb.get("image_code_%s" %image_code_id)
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

  #判断图片是否过期
  if real_image_code is None:
    return jsonify(errno=RET.NODATA, errmsg="图片验证失败 更新图片")

  #验证码与用户填写值对比
  # print(bytes.decode(real_image_code))
  # print(image_code)
  if bytes.decode(real_image_code).upper() != image_code.upper():
    return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

  #图片验证 成功 删除redis中图片验证码 防止用户使用同一个图片验证其他手机
  try:
    rdb.delete("image_code_%s" %image_code_id)
  except Exception as e:
    current_app.logger.error(e)

  #判断手机号 在60秒内有没有之前的记录 如果有则认为操作频繁 不受处理
  try:
    phone_flag = rdb.get("sms_phone_%s" %mobile)
  except Exception as e:
    current_app.logger.error(e)
  else:
    if phone_flag is not None:
      return jsonify(errno=RET.REQERR, errmsg="请求过于频繁 60秒后重试")

  #判断手机号 单条first()查询 若查询不到 返回None
  #有数据库 网络连接的使用try
  #数据库查询异常 不影响后续  当用户不存在流程 最后注册时在校验用户
  try:
    user = User.query.filter_by(mobile=mobile).first()
  except Exception as e:
    current_app.logger.error(e)
  else:
    if user:
      #表示手机号已经存在
      return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")

  #如果手机号不存在 则生成短信验证码
  sms_code = "%06d" % random.randint(0, 999999)

  #保存真实短信验证码 同时保存已发送过短信的手机号 60秒间隔内此手机号不能在发送验证码
  #sms_code_  短信验证码
  #sms_phone_ 手机号发送短信时间间隔标识 redis自动删除
  try:
    rdb.setex("sms_code_%s" %mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    rdb.setex("sms_phone_%s" %mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")

  #发送短信 第三方服务有网络请求 try except
  # try:
  #   ccp = CCP()
  #   result = ccp.send_tempalte_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
  # except Exception as e:
  #   current_app.logger.error(e)
  #   return jsonify(errno=RET.THIRDERR, errmsg="发送失败")

  # 返回值
  # if result == 0:
  #   return jsonify(errno=RET.OK, errmsg="发送成功")
  # else:
  #   return jsonify(errno=RET.THIRDERR, errmsg="短信发送失败")


  #使用celery异步发送短信 delay函数调用后立即返回
  send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)

  #返回的是异步执行的结果
  # 通过get方法返回能获取celery异步执行的结果
  # get方法默认是阻塞的行为 会等到有执行结果之后才返回
  # get方法也接受参数timeout 超时时间 超时时间后还拿不到结果 则返回
  # print(result.id)
  #直接返回返回值
  return jsonify(errnbo=RET.OK, errmsg="发送成功")


