#encoding:utf-8
from CCPRestSDK import REST

accountSid = '8a216da8674defd101675896e98107b1'

#主帐号Token
accountToken = '107b7e17326f439b8ebabfa23dc25b95'

#应用Id
appId = '8a216da8674defd101675896e9df07b8'

#请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

#请求端口 
serverPort = '8883'

#REST版本号
softVersion = '2013-12-26'

# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为列表 例如：['12','34']，如不需替换请填 ''
# @param $tempId 模板Id

class CCP(object):
  """
  单例模式
  使用__new__(cls)创建对象 判断当前__new__中是否有对象 没有则创建 有直接返回对象
  __init__() 则表示对象已经产生
  """
  #保存对象的类属性  属于类 此值更改后每次请求 值都是相同的
  insatnce = None

  def __new__(cls, *args, **kwargs):
    #判断CCP类有没有已经创建好的对象 如果没有 创建对象 并保存
    if cls.insatnce is None:
      obj = super(CCP, cls).__new__(cls)   #cls 调用父类的__new__()方法

      #初始化 REST SDK
      obj.rest = REST(serverIP, serverPort, softVersion)
      obj.rest.setAccount(accountSid, accountToken)
      obj.rest.setAppId(appId)

      cls.insatnce = obj

    return cls.insatnce

  def send_tempalte_sms(self, to, data, temp_id):
    result = self.rest.sendTemplateSMS(to, data, temp_id)
    print(result)
    # for k, v in result.iteritems():
    #   if k == 'templateSMS':
    #     for k, s in v.iteritems():
    #       print('%s:%s' % (k, s))
    #   else:
    #     print('%s:%s' % (k, v))


if __name__ == "__main__":
  ccp = CCP()
  #                      接受验证码手机号   验证码   分钟 测试模板ID:1
  ccp.send_tempalte_sms("18210912426", ['1111', '5'], 1)

#sendTemplateSMS(手机号码,内容数据,模板Id)