python manage.py db init
python manage.py db migrate -m "init tables"  #初始化 需要有文件使用models
python manage.py db upgrade
python manage.py db downgrade
