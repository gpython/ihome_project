# -*- coding: utf-8 -*-
from qiniu import Auth, put_file, etag
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 's2SADxX6nwnYbOF1Y-0gdviHLL8xDiUY4NppMHs3'     #t access key
secret_key = 'oKKeerRYiHqdQkIPZZ00aGZXSz--h8EjF2vdSah2'     #t secret key


def storage(file_data):
  """
  上传文件到qiniu
  :return:
  """
  #构建鉴权对象
  q = Auth(access_key, secret_key)

  #要上传的空间
  bucket_name = 'ihome'

  #上传到七牛后保存的文件名 若不指定文件名 则随机生成文件名
  #若不指定key 以下函数参数使用None来代替
  # key = 'my-python-logo.png'

  #生成上传 Token，可以指定过期时间等
  token = q.upload_token(bucket_name, None, 3600)

  #要上传文件的本地路径 可以使用二进制文件流格式上传
  #file_data 文件二进制数据
  # localfile = './sync/bbb.jpg'

  ret, info = put_file(token, None, file_data)
  print(info)
  print(ret)
  if info.status_code == 200:
    #上传成功 返回文件名
    return ret.get("key")
  else:
    #上传失败
    raise Exception("上传失败")
  # assert ret['key'] == key
  # assert ret['hash'] == etag(localfile)

if __name__ == '__main__':
  with open("./1.png") as f:
    file_data = f.read()
    storage(file_data)