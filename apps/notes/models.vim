
User
 user_id
 mobile
 password
 name
 avatar_url
 real_name
 real_id_card

House
 house_id
 user_id
 title
 area_id
 price
 index_image_url
 order_count     #每次有相应订单 此字段+1 提高查询效率

Area
 area_id
 name

House_Image
 image_id
 url
 house_id

Factility
 factility_id
 name

House_Factility
 id
 house_id
 factility_id

Order
 order_id
 user_id
 house_id
 create_time
 start_date
 end_date
 price
 amount
 days
 status  #订单状态 (租房者拒绝及相关信息 或 同意后访客评论信息)
 comment #订单状态对应的评论信息

User表与House表一对多关系 一个User可以有多个相对应House
Area表与House表 一对多关系 一个地区有多个相对应House信息
House表与House_image 一对多关系 一个House有多个相对应House_image图片
House表有默认图片 提高查询速度
House表与Factility表 多对多关系
每个House有多个Factility 每个Factility可以对应于多个House
Order表与user表一对多关系  一个User可以有多个对应的Order (User不同时期的Order)
Order表与House表一对多关系  一个House可以对应多个Order (House不同时期Order)