windows 7+ 运行celery4 版本
报错如下
ERROR/MainProcess] Task handler raised error: ValueError('not enough values to unpack (expected 3, got 0)',)
File "d:\pchar_project\ihome_project\venv\lib\site-packages\billiard\pool.py", line 358, in workloop
    result = (True, prepare_result(fun(*args, **kwargs)))
  File "d:\pchar_project\ihome_project\venv\lib\site-packages\celery\app\trace.py", line 537, in _fast_trace_task
    tasks, accept, hostname = _loc
ValueError: not enough values to unpack (expected 3, got 0)

解决方案
pip install eventlet

启动celery时候添加-P eventlet
celery -A <mymodule> worker -l info -P eventlet

celery -A apps.tasks.task_sms worker -l info -P eventlet
即可正常调用

