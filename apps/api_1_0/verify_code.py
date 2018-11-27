from flask import current_app, jsonify, make_response
from . import api
from apps.utils.captcha.captcha import captcha
from apps import rdb, constants
from apps.utils.response_code import RET

#GET http://127.0.0.1:5000/api/v1.0/image_codes/<image_code_id>
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