from sqlalchemy.exc import IntegrityError
from apps.models import User
from . import  api
from flask import request, jsonify, current_app, session
from apps.utils.response_code import RET
from apps import rdb, db, constants
import  re

@api.route("/users", methods=["POST"])
def register():
  """
  注册 传递过来参数
  手机号 短信验证码 密码 确认密码
  参数格式 json
  :return:
  """

  #获取json请求数据 返回字典
  req_dict = request.get_json()

  mobile = req_dict.get("mobile")
  sms_code = req_dict.get("sms_code")
  password = req_dict.get("password")
  password2 = req_dict.get("password2")

  #校验参数
  if not all([mobile, sms_code, password]):
    return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

  #判断手机号吗格式
  if not re.match(r"1[34578]\d{9}", mobile):
    #格式不对
    return jsonify(errno=RET.PARAMERR, errmsg="手机号码错误")

  #
  if password != password2:
    return jsonify(errno=RET.PARAMERR, errmsg="两次密码不同")

  #redis中取出短信验证码
  try:
    real_sms_code = rdb.get("sms_code_%s" %mobile)
    print("real_sms_code:", real_sms_code)
  except Exception as e:
    current_app.logger.error(e)
    return  jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")

  #短信验证码是否过期
  if real_sms_code is None:
    return  jsonify(errno=RET.NODATA, errmsg="短信验证码验证失败")

  #删除redis中短信验证码 防止重复校验 手机号注册撞库
  try:
    rdb.delete("sms_code_%s" %mobile)
  except Exception as e:
    current_app.logger.error(e)

  #短信验证码 正确性
  if bytes.decode(real_sms_code) != sms_code:
    return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

  #判断用户手机是否注册过
  # try:
  #   #获取单条数据 如果数据不存在返回None
  #   user = User.query.filter_by(mobile=mobile).first()
  # except Exception as e:
  #   current_app.logger.error(e)
  #   return jsonify(errno=RET.DATAERR, errmsg="数据异常")
  # else:
  #   if user is not None:
  #     #手机号已经存在
  #     return  jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")

  #保存用户 User表中设置mobile uniq=True唯一值 重复存入数据 数据库报错
  user = User(name=mobile, mobile=mobile)
  user.password = password
  try:
    db.session.add(user)
    db.session.commit()
  except IntegrityError as e:
    #数据库操作错误回滚
    db.session.rollback()
    #表示手机号出现重复 手机号已经注册过
    current_app.logger.error(e)
    return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")
  except Exception as e:
    #数据库操作错误回滚
    db.session.rollback()
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="数据库异常")

  #保存登录状态到session中
  session["name"] = mobile
  session["mobile"] = mobile
  session["user_id"] = user.id

  #以防止 用户通过程序自动注册
  #返回结果
  return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route("/sessions", methods=["POST"])
def login():
  """
  用户登录
  参数 手机号 密码 json
  :return:
  """
  #获取参数
  req_dict = request.get_json()
  mobile = req_dict.get("mobile")
  password = req_dict.get("password")

  #校验参数
  #参数完整性校验
  if not all([mobile, password]):
    return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

  #手机号格式
  if not re.match(r"1[34578]\d{9}", mobile):
    return jsonify(errno=RET.PARAMERR, errmsg="手机号码格式错误")

  #判断错误次数是否超过限制 超过限制则返回
  #redis中记录 "access_num_请求IP": 次数
  user_ip = request.remote_addr
  try:
    access_nums = rdb.get("access_num_%s" %user_ip)
  except Exception as e:
    current_app.logger.error(e)
  else:
    if access_nums is not None and int(bytes.decode(access_nums)) > constants.LOGIN_ERROR_MAX_TIMES:
      return jsonify(errno=RET.REQERR, errmsg="错误次数过多 请稍后重试")

  #从数据库中根据手机号查询用户的数据对象
  try:
    user = User.query.filter_by(mobile=mobile).first()
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

  #用数据库的密码为用户填写的密码进行校验
  if user is None or not user.check_password(password):
    #如果验证失败 记录错误次数 返回信息
    try:
      rdb.incr("access_num_%s" %user_ip)
      rdb.expire("access_num_%s" %user_ip, constants.LOGIN_ERROR_FORBID_TIME)
    except Exception as e:
      current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="用户名或密码错误")

  #如果验证相同成功 保存登录状态在session中
  session["name"] = user.name
  session["mobile"] = user.mobile
  session["user_id"] = user.id

  return jsonify(errno=RET.OK, errmsg="登录成功")

@api.route("/session", methods=["GET"])
def check_login():
  """
  检查登录状态 尝试从session中获取用户的名字
  :return:
  """
  name = session.get("name")
  #如果session中数据name名字存在 则表示用户已经登录 否则未登录

  if name is not None:
    return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
  else:
    return jsonify(errno=RET.SESSIONERR, errmsg="false")

@api.route("/session", methods=["DELETE"])
def logout():
  """
  登出 清除session
  :return:
  """
  session.clear()
  return jsonify(errno=RET.OK, errmsg="ok")