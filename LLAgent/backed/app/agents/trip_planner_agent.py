"""基于 LangChain/LangGraph 原生 MCP 管理的多智能体旅行规划系统"""

import json
from typing import Dict, Any, List, TypedDict
from datetime import datetime, timedelta

# 引入 LangChain & LangGraph 核心库
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END

from ..services.llm_service import get_llm
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings
from ..services.amap_service import get_amap_service

# ================= 定义本地高德工具，彻底干掉子进程 =================

@tool
def get_system_time() -> str:
    """获取系统当前的实时精准时间、日期和星期几。
    当你需要回答'现在几点'、'今天是几号'或需要根据当前日期推算'明天/后天'具体日期时，必须调用此工具。
    """
    from datetime import datetime
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    day_str = weekdays[now.weekday()]
    return f"系统实时时钟读数：{time_str}，{day_str}。"

# app/agents/trip_planner_agent.py

@tool
async def search_poi_tool(keywords: str, city: str) -> str:
    """搜索目标城市中的兴趣点信息。
    返回的数据中包含景点的真实 photo_url。
    """
    try:
        service = get_amap_service()
        pois = await service.search_poi(keywords=keywords, city=city)
        # 只取前 5 个，减少 token 消耗
        return json.dumps(pois[:5], ensure_ascii=False)
    except Exception as e:
        return "搜索失败"

@tool
async def get_weather_tool(city: str) -> str:
    """查询指定城市当前或近期的天气状况。
    
    Args:
        city: 目标城市名称，例如'北京'
    """
    try:
        service = get_amap_service()
        weather = await service.get_weather(city=city)
        return json.dumps(weather, ensure_ascii=False)
    except Exception as e:
        return f"天气查询服务暂时不可用: {str(e)}"
# ================= 1. 定义 LangGraph 状态 =================

class PlanState(TypedDict):
    """LangGraph 运行状态，用于在 Agent 节点之间传递上下文数据"""
    request: TripRequest
    attractions_raw: str
    weather_raw: str
    hotels_raw: str
    final_plan_json: str
    errors: List[str]

# ============ Agent提示词 ============

ATTRACTION_PROMPT = """你是一个专业的景点搜索专家。你的任务是根据城市和用户偏好，使用绑定的地图工具（如 amap_maps_text_search）搜索合适的景点。
你必须调用工具来获取真实的景点数据，不要自己凭空编造景点信息。
搜索到结果后，将主要的景点名称、地址和坐标提取出来并进行简要整理。"""

WEATHER_PROMPT = """你是一个天气查询专家。你的任务是查询指定城市的天气信息（如使用 amap_maps_weather 工具）。
你必须调用绑定的天气工具来获取真实的天气情况，不要自己编造天气。
查询到天气后，提取出关键的天气现象、气温变化，并整理好传递给后续行程规划师。"""

HOTEL_PROMPT = """你是一个酒店推荐专家。你的任务是根据城市和偏好推荐合适的酒店。
你必须调用绑定的工具（如 amap_maps_text_search）来搜索酒店，关键词可以使用"酒店"或"宾馆"。
整理出至少 3 个酒店的名称、地址和位置信息。"""

PLANNER_PROMPT = """你是行程规划专家。你的任务是根据景点信息和天气信息,生成详细的旅行计划。

请严格按照以下JSON格式返回旅行计划，不要输出任何其他的 markdown 格式之外的解释文字:
```json
{{
  "city": "{city}",
  "start_date": "{start_date}",
  "end_date": "{end_date}",
  "days": [
    {{
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {{
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {{"longitude": 116.397128, "latitude": 39.916527}},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      }},
      "attractions": [
        {{
          "name": "景点名称",
          "address": "详细地址",
          "location": {{"longitude": 116.397128, "latitude": 39.916527}},
          "visit_duration": 120,
          "description": "景点详细描述",
          "category": "景点类别",
          "ticket_price": 60
        }}
      ],
      "meals": [
        {{"type": "breakfast", "name": "早餐推荐", "description": "早餐描述", "estimated_cost": 30}},
        {{"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 50}},
        {{"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}}
      ]
    }}
  ],
  "weather_info": [
    {{
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }}
  ],
  "overall_suggestions": "总体建议",
  "budget": {{
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }}
}}
```

**重要提示:**
1. weather_info数组必须包含每一天的天气信息
2. 温度必须是纯数字(不要带°C等单位)
3. 每天安排2-3个景点
4. 考虑景点之间的距离和游览时间
5. 每天必须包含早中晚三餐
6. 提供实用的旅行建议
7. **必须包含预算信息**:
   - 景点门票价格(ticket_price)
   - 餐饮预估费用(estimated_cost)
   - 酒店预估费用(estimated_cost)
   - 预算汇总(budget)包含各项总费用
"""
#================= 3. 多智能体旅行规划系统类 =================

class MultiAgentTripPlanner:
    """多智能体旅行规划系统 (基于 LangChain 原生 MCP 客户端和 LangGraph)"""

    def __init__(self):
        """同步初始化多智能体系统配置"""
        print("🔄 开始初始化多智能体旅行规划系统...")
        self.settings = get_settings()
        self.llm = get_llm()
        
         # 统一声明注册上面写好的标准本地工具，不走 uvx 命令行，保证 100% 稳定
        self.tools = [search_poi_tool, get_weather_tool, get_system_time]
        # 编译 LangGraph 状态图流程
        self.workflow = self._build_workflow()
        print("✅ 多智能体 LangGraph 工作流骨架编译成功")

    async def ensure_initialized(self):
        """异步安全初始化：只在第一次调用时拉起并初始化 MCP 客户端"""
        # if self.mcp_toolkit is None:
        #     print("  - [Lazy Loading] 正在异步拉起原生 MCP 客户端...")
        #     from mcp import ClientSession
        #     from mcp.client.stdio import stdio_client, StdioServerParameters

        #     server_params = StdioServerParameters(
        #         command="uvx",
        #         args=["amap-mcp-server"],
        #         env={"AMAP_MAPS_API_KEY": self.settings.amap_api_key}
        #     )

        #     # 在当前的 asyncio 事件循环中安全、优雅地运行 stdio 客户端连接
        #     # 使用 ExitStack 或是直接连接
        #     read_stream, write_stream = await stdio_client(server_params).__aenter__()
        #     session = await ClientSession(read_stream, write_stream).__aenter__()
        #     await session.initialize()

        #     # 初始化 toolkit
        #     self.mcp_toolkit = MCPToolkit(
        #         server_command="uvx",
        #         server_args=["amap-mcp-server"],
        #         env={"AMAP_MAPS_API_KEY": self.settings.amap_api_key},
        #         session=session
        #     )
        #     self.tools = self.mcp_toolkit.get_tools()
        #     print(f"  - [Lazy Loading] MCP 客户端拉起成功，共载入 {len(self.tools)} 个工具")
        return 
            
            # 获取 LangChain 格式的 Tools 列表
           

            # 2. 编译并生成 LangGraph 状态图流程
            

    def _build_workflow(self) -> StateGraph:
        """构建并行查询的多智能体执行流程图"""
        builder = StateGraph(PlanState)

        # 添加 Agent 节点
        builder.add_node("search_attractions", self._attraction_node)
        builder.add_node("search_weather", self._weather_node)
        builder.add_node("search_hotels", self._hotel_node)
        builder.add_node("planner", self._planner_node)

        # 定义并行查询边
        builder.add_edge(START, "search_attractions")
        builder.add_edge(START, "search_weather")
        builder.add_edge(START, "search_hotels")

        # 汇聚到核心规划器
        builder.add_edge("search_attractions", "planner")
        builder.add_edge("search_weather", "planner")
        builder.add_edge("search_hotels", "planner")

        # 结束
        builder.add_edge("planner", END)

        return builder.compile()

    # ---- LangGraph 节点处理函数 ----

    async def _attraction_node(self, state: PlanState) -> Dict[str, Any]:
        """景点搜索 Agent 节点"""
        # 
        pass

    async def _weather_node(self, state: PlanState) -> Dict[str, Any]:
        """天气查询 Agent 节点"""
        await self.ensure_initialized()  # 确保通道已异步建立
        req: TripRequest = state["request"]
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        response = llm_with_tools.invoke([
            SystemMessage(content=WEATHER_PROMPT),
            HumanMessage(content=f"请查询{req.city}的最新天气状况。")
        ])
        
        result_str = self._execute_tool_calls(response)
        if not result_str:
            result_str = response.content
            
        return {"weather_raw": result_str}

    async def _hotel_node(self, state: PlanState) -> Dict[str, Any]:
        """酒店推荐 Agent 节点"""
        await self.ensure_initialized()  # 确保通道已异步建立
        req: TripRequest = state["request"]
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        hotel_type = req.accommodation or "酒店"
        prompt = f"{HOTEL_PROMPT}\n目标城市: {req.city}，偏好类型: {hotel_type}"
        response = llm_with_tools.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=f"请在{req.city}查找适合的'{hotel_type}'推荐列表。")
        ])
        
        result_str = self._execute_tool_calls(response)
        if not result_str:
            result_str = response.content
            
        return {"hotels_raw": result_str}

    async def _planner_node(self, state: PlanState) -> Dict[str, Any]:
        """行程规划师节点：整合输出规范 JSON"""
        req: TripRequest = state["request"]
        
        formatted_prompt = PLANNER_PROMPT.format(
            city=req.city,
            start_date=req.start_date,
            end_date=req.end_date
        )
        
        user_input_context = f"""
基本要求：
- 城市: {req.city}
- 日期: {req.start_date} 至 {req.end_date}
- 偏好交通: {req.transportation}
- 用户特别要求: {req.free_text_input or "无"}

【子 Agent 搜集的数据】：
- 景点推荐数据：
{state.get("attractions_raw")}
- 天气预报状况：
{state.get("weather_raw")}
- 备选住宿酒店：
{state.get("hotels_raw")}
"""
        response = self.llm.invoke([
            SystemMessage(content=formatted_prompt),
            HumanMessage(content=user_input_context)
        ])
        
        # 直接使用 LLM 输出作为最终结果，后续可以增加 JSON 验证和修正机制
        return {"final_plan_json": response.content}

    # ---- 辅助调用方法 ----

    def _execute_tool_calls(self, response: Any) -> str:
        """执行模型产生的原生 LangChain 工具调用"""
        outputs = []
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                # 在原生 McpToolkit 工具集里匹配
                target_tool = next((t for t in self.tools if t.name == tool_name), None)
                if target_tool:
                    try:
                        # 原生工具可以直接执行传入其 args 参数
                        tool_result = target_tool.invoke(input=tool_call["args"])
                        outputs.append(str(tool_result))
                    except Exception as e:
                        outputs.append(f"[原生工具 {tool_name} 执行出错: {str(e)}]")
        return "\n".join(outputs)

    # ---- 外部主要接口 ----

    async def plan_trip(self, request: TripRequest) -> TripPlan:
        """多智能体协作生成行程计划逻辑"""
        try:
            print(f"\n{'='*60}")
            print(f"🚀 [LangGraph] 开始多智能体协作流程 (原生 MCP 客户端模式)...")
            print(f"目的地: {request.city} | 天数: {request.travel_days}天")
            print(f"{'='*60}\n")
            initial_state = {
                "request": request,
                "attractions_raw": "",
                "weather_raw": "",
                "hotels_raw": "",
                "final_plan_json": "",
                "errors": []
            }

            # 执行多智能体并行状态图
            final_state = await self.workflow.ainvoke(initial_state)

            # 解析规划师返回的 JSON 数据
            plan_json_str = final_state.get("final_plan_json", "")
            return self._parse_response(plan_json_str, request)

        except Exception as e:
            print(f"❌ 运行多智能体行程规划失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_plan(request)

    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """提取并解析规划数据 JSON"""
        try:
            clean_str = response.strip()
            # 兼容 Markdown 中的 ```json 包装格式
            if "```json" in clean_str:
                clean_str = clean_str.split("```json")[-1].split("```")[0].strip()
            elif "```" in clean_str:
                clean_str = clean_str.split("```")[-1].split("```")[0].strip()
            
            plan_data = json.loads(clean_str)
            return TripPlan(**plan_data)
        except Exception as e:
            print(f"⚠️ 解析计划 JSON 失败: {str(e)}，降级采用默认兜底行程。")
            return self._create_fallback_plan(request)

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """兜底降级行程"""
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)
            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i+1}天行程游览",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}热门景区",
                        address=f"{request.city}市区中心区域",
                        location=Location(longitude=116.4, latitude=39.9),
                        visit_duration=120,
                        description="这是一个默认的备份推荐景点",
                        category="景点"
                    )
                ],
                meals=[
                    Meal(type="breakfast", name="当地特色早餐", description="品尝风味早餐"),
                    Meal(type="lunch", name="特色午餐", description="推荐风味午饭"),
                    Meal(type="dinner", name="特色晚餐", description="推荐美味晚饭")
                ]
            )
            days.append(day_plan)
            
        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions="系统响应缓慢，已为您快速返回极简备用行程。"
        )

    def close(self):
        """显式释放和关闭原生 MCP 连接"""
        try:
            if hasattr(self, "mcp_toolkit"):
                # 如果底层提供同步或异步的清理方法
                # McpToolkit 会在进程退出时被 Python 的垃圾回收自动清理，但手动释放是优雅的
                pass
        except Exception:
            pass


# ================= 4. 单例导出 =================
_multi_agent_planner = None

def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体系统单例"""
    global _multi_agent_planner
    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner