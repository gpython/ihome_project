import json

from apps.utils.image_storage import storage
from . import api
from apps.utils.commons import login_required
from flask import g, current_app, jsonify, request
from apps.utils.response_code import RET
from apps.models import Area, House, Facility, HouseImage
from apps import db, constants, rdb


@api.route("/areas", methods=["GET"])
def get_area_info():
  """
  获取城区信息
  先从缓存redis中查询area_info获取城区数据 若有数据直接返回
  否则 从数据库中查询数据 数据查询数据转换为字典 保存到redis缓存中
  并返回字典 json数据
  :return:
  """
  #尝试从redis中获取数据
  try:
    resp_json = rdb.get("area_info")
  except Exception as e:
    current_app.logger.error(e)
  else:
    if resp_json is not None:
      #缓存有数据
      current_app.logger.info("Hit redis area_info")
      return resp_json, 200, {"Content-Type": "applicaition/json"}

  #缓存无数据 查询数据库 获取城区信息
  try:
    area_li = Area.query.all()
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="数据库异常")

  area_dict_li = []

  #将对象转换为字典
  for area in area_li:
    area_dict_li.append(area.to_dict())

  #将数据转换为json
  resp_dict = dict(errno=RET.OK, errmsg="OK", data=area_dict_li)
  resp_json = json.dumps(resp_dict)

  #将数据保存到redis中
  try:
    rdb.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
  except Exception as e:
    current_app.logger.error(e)

  return resp_json, 200, {"Content-Type":"application/json"}

@api.route("/houses/info", methods=["POST"])
@login_required
def save_house_info():
  """
  保存房屋的基本信息
  :return:
  前端发送过来的json数据
  {
    "title":"",
    "price":"",
    "area_id":"",
    "address":"",
    "room_count":"",
    "acreage":"",
    "unit":"",
    "capacity":"",
    "beds":"",
    "deposit":"",
    "min_days":"",
    "max_days":"",
    "facility":["7","8"]
  }
  """
  #获取数据
  user_id = g.user_id
  house_data = request.get_json()

  title = house_data.get("title") #房屋标题
  price = house_data.get("price") #房屋单价
  area_id = house_data.get("area_id") #房屋所属区编号
  address = house_data.get("address") #房屋地址
  room_count = house_data.get("room_count") #房屋包含房间数
  acreage = house_data.get("acreage") #房屋面积
  unit = house_data.get("unit") #房屋布局(几室几厅)
  capacity = house_data.get("capacity") #房屋容纳人数
  beds = house_data.get("beds") #房屋卧床数目
  deposit = house_data.get("deposit") #押金
  min_days = house_data.get("min_days") #最小入住天数
  max_days = house_data.get("max_days") #最大入住天数

  #校验参数
  if not ([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
    return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

  #判断金额是否正确 谨防爬虫
  try:
    price = int(float(price)*100)
    deposit = int(float(price)*100)
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

  #判断城区id是否存在 谨防爬虫
  try:
    area = Area.query.get(area_id)
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="数据异常")

  if area is None:
    return jsonify(errno=RET.NODATA, errmsg="城区信息有误")

  #保存房屋信息
  house = House(
    user_id = user_id,
    area_id = area_id,
    title = title,
    price = price,
    address = address,
    room_count = room_count,
    acreage = acreage,
    unit = unit,
    capacity = capacity,
    beds = beds,
    deposit = deposit,
    min_days = min_days,
    max_days = max_days
  )
  try:
    db.session.add(house)
    # db.session.commit()
  except Exception as e:
    current_app.logger.error(e)
    # db.session.rollback()
    return jsonify(errno=RET.DBERR, errmsg="保存数据异常")

  #处理房屋设施信息
  facility_ids = house_data.get("facility")

  #如果用户勾选了设施信息 在保存到数据库
  if facility_ids:
    try:
      facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
    except Exception as e:
      current_app.loggr.error(e)
      return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if facilities:
      #表示合法的设施数据
      #保存设施数据
      house.facilities = facilities

  #一次全部提交数据 基础数据 和 facilities数据一起提交
  try:
    db.session.add(house)
    db.session.commit()
  except Exception as e:
    current_app.logger.error(e)
    db.session.rollback()
    return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

  return jsonify(errno=RET.OK, errmsg="保存数据成功", data={"house_id": house.id})

@api.route("/houses/image", methods=["POST"])
@login_required
def save_hosue_image():
  """
  保存房屋图片
  :return:
  """
  image_file = request.files.get("house_image")
  house_id = request.form.get("house_id")

  if not all([image_file, house_id]):
    return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

  #判断house_id正确定
  try:
    house = House.query.get(house_id)
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.DBERR, errmsg="数据库异常")

  if house is None:
    return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

  #读取图片 保存在七牛云存储
  image_data = image_file.read()
  try:
    file_name = storage(image_data)
  except Exception as e:
    current_app.logger.error(e)
    return jsonify(errno=RET.THIRDERR, errmsg="保存图片失败")

  #保存图片信息到数据库  房屋信息还有一张主图片
  house_image = HouseImage(house_id=house_id, url=file_name)
  db.session.add(house_image)

  #处理房屋主主图片 上传的第一站图片为主图片
  if not house.index_image_url:
    house.index_image_url = file_name
    db.session.add(house)

  try:
    db.session.commit()
  except Exception as e:
    current_app.logger.error(e)
    db.session.rollback()
    return jsonify(errno=RET.DBERR, errmsg="保存图片数据异常")

  image_url = constants.QINIU_URL_DOMAIN + file_name
  return jsonify(errno=RET.OK, errmsg="OK", data={"image_url": image_url})




