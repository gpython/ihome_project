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