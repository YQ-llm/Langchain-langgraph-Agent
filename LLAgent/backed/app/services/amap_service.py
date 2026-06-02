"""高德地图服务封装 (高性能纯 Python 版)"""

import httpx
from typing import List, Dict, Any, Optional
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo

class AmapService:
    """高德地图服务封装类 - 直接调用高德 Web API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.amap_api_key
        self.base_url = "https://restapi.amap.com/v3"

    async def get_weather(self, city: str) -> str:
        """获取目的地真实的未来天气预报"""
        if not self.api_key:
            return "天气数据暂不可用 (API Key 未配置)"
        
        try:
            async with httpx.AsyncClient() as client:
                # 调用高德预报天气接口 (extensions=all 获取预报)
                params = {
                    "key": self.api_key,
                    "city": city,
                    "extensions": "all",
                    "output": "JSON"
                }
                response = await client.get(f"{self.base_url}/weather/weatherInfo", params=params)
                data = response.json()
                
                if data.get("status") == "1" and data.get("forecasts"):
                    f = data["forecasts"][0]
                    casts = f.get("casts", [])
                    result = f"【{city}天气预报】\n"
                    for c in casts[:3]: # 只取前三天
                        result += f"- {c['date']} ({c['dayweather']}): 白天{c['daytemp']}度, 晚上{c['nighttemp']}度\n"
                    return result
                return f"暂未查询到 {city} 的预报信息"
        except Exception as e:
            return f"天气查询异常: {str(e)}"

    # app/services/amap_service.py

    async def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[Dict]:
        """搜索 POI 并提取真实图片"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "key": self.api_key,
                    "keywords": keywords,
                    "city": city,
                    "citylimit": "true" if citylimit else "false",
                    "output": "JSON",
                    "extensions": "all" # 💡 必须设置为 all 才会返回图片和详情
                }
                response = await client.get(f"{self.base_url}/place/text", params=params)
                data = response.json()
                pois = data.get("pois", [])
                
                result = []
                for poi in pois:
                    # 提取第一张高德图片，如果没有则给一个占位图
                    photo_url = ""
                    if poi.get("photos") and len(poi["photos"]) > 0:
                        photo_url = poi["photos"][0].get("url", "")
                    
                    result.append({
                        "name": poi.get("name"),
                        "location": poi.get("location"),
                        "address": poi.get("address"),
                        "photo_url": photo_url  # 💡 这里的 URL 是高德服务器提供的真实实景图
                    })
                return result
        except Exception as e:
            print(f"高德搜索异常: {e}")
            return []
            

# 全局单例
_amap_service = AmapService()

def get_amap_service() -> AmapService:
    return _amap_service