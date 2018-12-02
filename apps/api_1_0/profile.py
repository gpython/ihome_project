from apps import db, constants
from apps.models import User
from . import api
from apps.utils.commons import login_required
from flask import g, current_app, jsonify, request
from apps.utils.response_code import RET
from apps.utils.image_storage import storage

@api.route("/user/avatar". methods=["POST"])
@login_required
def set_user_avatar():
  """
  设置用户头像
  参数 图片(多媒体表单格式) 用户id (g.user_id)
  :return:
  """
  #装饰器代码中 已经将user_id 保存到g对象中 所以视图中可以直接获取
  user_id = g.user_id

  #获取图片
  image_file = request.files.get("avatar")

  if image_file is None:
    return jsonify(errno=RET.PARAMERR, errmsg="未上传图片")

  image_data = image_file.read()

  #使用七牛上传图片
  try:
    file_name = storage(image_data)
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.THIRDERR, errmsg="上传失败")

  #保存图片
  try:
    User.query.filter_by(id=user_id).update({"avatar_url":file_name})
    db.session.commit()
  except Exception as e:
    db.sesion.rollback()
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="保存图片信息失败")

  avatar_url = constants.QINIU_URL_DOMAIN  + file_name
  #保存成功返回
  return jsonify(errno=RET.OK, errmsg="保存成功", data={"avatar_url": avatar_url})