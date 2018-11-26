from flask import Blueprint, current_app

#提供静态文件的蓝图
html = Blueprint("web_html", __name__)

#http://127.0.0.1/()
#http://127.0.0.1/(index.html)
#http://127.0.0.1/(register.html)
#http://127.0.0.1/favicon.ico

#re(参数):提取参数名称
@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
  """
  提供html文件
  如果html_file_name为"" 表示访问路径为/ 请求的是主页
  :param html_file_name:
  :return: current_app.send_static_file 静态文件资源
  """

  if not html_file_name:
    html_file_name = "index.html"

  #如果资源名不为favicon.ico
  if html_file_name != "favicon.ico":
    html_file_name = "html/" + html_file_name

  #flask提供返回静态文件的方法
  return current_app.send_static_file(html_file_name)