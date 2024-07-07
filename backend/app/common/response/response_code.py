from enum import Enum


class CustomCodeBase(Enum):

    @property
    def code(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]


class CustomResponseCode(CustomCodeBase):

    HTTP_200 = (200, "")
    HTTP_201 = (201, "新建请求成功")
    HTTP_202 = (202, "请求已接受，但处理尚未完成")
    HTTP_204 = (204, "请求成功，但没有返回内容")
    HTTP_400 = (400, "请求错误")
    HTTP_401 = (401, "未经授权")
    HTTP_403 = (403, "禁止访问")
    HTTP_404 = (404, "请求的资源不存在")
    HTTP_410 = (410, "请求的资源已永久删除")
    HTTP_422 = (422, "请求参数非法")
    HTTP_425 = (425, "无法执行请求，由于服务器无法满足要求")
    HTTP_429 = (429, "请求过多，服务器限制")
    HTTP_500 = (500, "服务器内部错误")
    HTTP_502 = (502, "网关错误")
    HTTP_503 = (503, "服务器暂时无法处理请求")
    HTTP_504 = (504, "网关超时")


class CustomErrorCode(CustomCodeBase):

    CAPTCHA_ERROR = (40001, "验证码错误")
