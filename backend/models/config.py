"""系统配置相关模型"""

from pydantic import BaseModel


class ConfigResponse(BaseModel):
    config_key: str
    config_value: str
    description: str = ""


class ConfigUpdate(BaseModel):
    config_value: str
