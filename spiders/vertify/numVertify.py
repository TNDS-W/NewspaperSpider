import base64
from spiders.vertify.ShowapiRequest import ShowapiRequest

class NumVertify():

    def image_to_base64(self):
        with open('captcha.png','rb') as f:
            data = f.read()
            encodestr = base64.b64encode(data)
            return str(encodestr,'utf-8')

    def vertify_identity(self):
        base64_value = 'data:image/png;base64,'+ self.image_to_base64()

        r = ShowapiRequest("http://route.showapi.com/184-5", "84897", "8a89dae202384d768e79a1ffc884cb98")
        r.addBodyPara("img_base64", base64_value)
        r.addBodyPara("typeId", "13")
        r.addBodyPara("convert_to_jpg", "0")
        r.addBodyPara("needMorePrecise", "0")
        res = r.post()
        json_value = res.json()
        vertify_Num = json_value['showapi_res_body']['Result']
        return vertify_Num
