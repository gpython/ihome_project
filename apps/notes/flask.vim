python manage.py db init
python manage.py db migrate -m "init tables"  #初始化 需要有文件使用models
python manage.py db upgrade
python manage.py db downgrade


Post请求 服务器csrf
csrf验证机制
cookie:
  csrf_token = xxx
body:
  csrf_token = xxx
从cookie中获取一个csrf_token值
从请求体中获取一个csrf_token值
如果两个值相等 则检验通过
可以进入视图函数中检验
如果两个值不同 校验失败 想前端返回400状态码


图片验证

浏览器生成随机编号
携带编号发送获取图片验证码的请求

服务器生成验证码图片 并将验证码真实值和编号存到redis中


浏览器获取短信验证请求
携带参数
  用户填写图片验证码
  图片验证码编号

验证图片验证码正确性 正确发送短信验证