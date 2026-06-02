"""旅行规划API路由"""
from typing import List, Optional, Union
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent
from ...services.llm_service import get_llm 
from datetime import datetime
import json
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
# 找到导入 get_llm 的地方，在它下面加上 get_amap_service 的导入
from ...services.llm_service import get_llm
from ...services.amap_service import get_amap_service  # 👈 补上这一行
# We need sse_starlette to make FastAPI stream SSE nicely
# Install it first if not present: pip install sse-starlette
from sse_starlette import EventSourceResponse
router = APIRouter(prefix="/trip", tags=["旅行规划"])

# 定义一个获取实时时间上下文的辅助函数
def get_current_time_context():
    now = datetime.now()
    # 格式化为：2025年05月20日 星期二 14:30:05
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return f"{now.strftime('%Y-%m-%d %H:%M:%S')} {weekdays[now.weekday()]}"

@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """
    生成旅行计划

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")

        # 获取Agent实例 (此时底层已切换为 LangGraph)
        print("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划 (接口签名完全一致，底层通过 Graph 运行)
        print("🚀 开始生成旅行计划...")
        trip_plan = await agent.plan_trip(request)

        print("✅ 旅行计划生成成功,准备返回响应\n")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 获取重构后的 LangGraph 智能体实例
        agent = get_trip_planner_agent()
        
        # 统计注册到 LangGraph 的节点
        nodes_count = 0
        if hasattr(agent, "workflow") and hasattr(agent.workflow, "nodes"):
            nodes_count = len(agent.workflow.nodes)
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "engine": "LangGraph + LangChain",
            "graph_nodes_count": nodes_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )
#怎加一个机器轻量级的“大白话解析路由”
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

class ExtractedTripIntent(BaseModel):
    """大模型提取出的用户出行意图"""
    city: str = Field(description="目的地城市名称，例如 '宁波'")
    start_date: str = Field(description="开始日期，如果用户没说，默认生成今天起的明后天格式 YYYY-MM-DD")
    end_date: str = Field(description="结束日期，YYYY-MM-DD")
    travel_days: int = Field(description="旅行天数，数字，默认3")
    transportation: str = Field(description="交通工具，例如 '公共交通' 或 '自驾'")
    accommodation: str = Field(description="住宿偏好，例如 '快捷酒店' 或 '高档宾馆'")
    preferences: List[str] = Field(description="偏好标签列表")
    free_text_input: str = Field(description="原样保留用户的输入内容")

from fastapi import Query  # 确保导入了 Query

@router.post("/parse_chat", summary="解析用户的对话输入")
async def parse_chat_input(
    user_message: str = Query(..., description="用户手写的旅行大白话文本")
):
    """
    将用户手写的对话大白话，通过 LLM 解析为标准的结构化出行意图
    """
   # 获取实时时间
    time_info = get_current_time_context()
    try:
        llm = get_llm()
        
        parser = JsonOutputParser(pydantic_object=ExtractedTripIntent)
        
        prompt = PromptTemplate(
            template=f"当前系统实时时间: {time_info}。\n" + 
                 "请根据这个时间，从用户输入中提取旅行意图（如'今天'指具体哪天）。\n" +
                 "{format_instructions}\n用户输入: {query}",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | llm | parser
        
        # 运行 Chain，让通义千问自动提取
        extracted_data = chain.invoke({"query": user_message})
        
        return {
            "success": True,
            "data": extracted_data
        }
    except Exception as e:
        # 在这里显式把错误打印在终端中，万一有错我们能立马看到
        print(f"❌ 大白话意图解析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"意图解析失败: {str(e)}")

import json
import asyncio
from fastapi.responses import StreamingResponse  # 改用 FastAPI 官方原生无缓存流式
from langchain_core.messages import HumanMessage, SystemMessage


@router.get("/plan_stream", summary="流式生成旅行计划")
async def plan_trip_stream(user_message: str):
    """
    使用极简、百分百不悬挂的 FastAPI 原生 StreamingResponse 传输字元数据 (SSE)
    """
    async def event_generator():
        try:
            # # 1. 初始化
            # llm = get_llm()
            # from ...services.amap_service import get_amap_service
            # amap_service = get_amap_service() # 获取同步工厂实例
            
            # # 获取当前时间
            now = datetime.now()
            time_context = now.strftime("%Y-%m-%d %H:%M:%S")
            weekday_str = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][now.weekday()]

            # # 2. 预处理：快速提取城市名
            # print(f"🧠 [Step 1] 正在解析用户意图: {user_message}")
            # city_extract = await llm.ainvoke(f"从用户输入中提取目的地城市名，只返回城市名。用户说：{user_message}")
            # target_city = city_extract.content.strip().replace("。", "").replace(" ", "")
            
            # # 3. 获取高德真实预报 (关键点：必须 await)
            # print(f"🌤️  [Step 2] 正在检索 {target_city} 的高德实时气象数据...")
            # weather_raw = await amap_service.get_weather(target_city)
            # weather_context = str(weather_raw)
            llm = get_llm()
            from ...services.amap_service import get_amap_service
            amap_service = get_amap_service()

            # [Step 1] 提取城市名
            city_extract = await llm.ainvoke(f"提取目的地城市名。用户说：{user_message}")
            target_city = city_extract.content.strip().replace("。", "")

            # [Step 2] 直接获取天气 (现在是纯 HTTP，极其稳定)
            # 2. 提前并发抓取天气和热门景点数据 (Augmented Data)
            # 这样 AI 还没开口，手里就已经攥着高德的真实图片 URL 了
            weather_task = amap_service.get_weather(target_city)
            poi_task = amap_service.search_poi("著名景点", target_city)
            weather_info, poi_info = await asyncio.gather(weather_task, poi_task)
            # 4. 构造强力系统提示词
            # 在 event_generator 内部，先获取 POI 数据
            # amap_pois 是通过 service.search_poi(target_city) 拿到的真实列表
            # 包含：{"name": "...", "location": "116.39,39.91", "photo": "..."}
            # 3. 构造超级上下文
            # 把高德返回的 POI 列表（带图片 URL）直接塞进系统提示词
            # 将天气信息赋值给上下文变量
            weather_context = str(weather_info)
            poi_context = json.dumps(poi_info, ensure_ascii=False)
            #- 你必须通过调用 `search_poi_tool` 获取景点的真实数据。
            system_prompt = f"""你现在是【高德地图官方认证实时智能导游】。

            【实时真理数据区】：
            - 系统当前时间：{time_context} ({weekday_str})
            - 目的地：{target_city}
            - 高德真实预报天气：{weather_context}
            - 可选高德真实景点素材库（含精准坐标）：{json.dumps(poi_info, ensure_ascii=False)}

            【核心任务与顺序】：
            1. **时间对齐**：首先播报当前时间，并精准推算出游玩当天的日期。
            2. **天气播报**：必须基于上方“真实天气数据”，给出当天的气象建议。
            3. **行程规划**：请从下方的“真实景点素材库”中挑选最合适的景点。
                
            
            【景点输出格式规范（严格执行）】：
            - 时间：请明确指出是第几天的行程（例如：Day 1, Day 2...），并给出具体日期（例如：2025年05月21日）。
            - 标题： 📍 {{景点名称}}
            - 介绍：写一段大气、详尽且吸引人的游览指南，50字以内。
            - 图片：1. 在调用 `search_poi_tool` 得到的 JSON 结果中，每个景点都有一个 `photo_url` 字段。
                    2. **禁止使用 Unsplash 或 Pollinations 链接。**
                    3. 如果 `photo_url` 为空，则不显示图片，或者使用一张该城市的通用美图。
                    4. Markdown 格式：`![景点图](直接填入获取到的 photo_url)`。
                    5.图片下面内容：1.给出具体时间点建议；
                        2.建议玩的时长和交通工具和特色美食推荐；
                        3.如果游玩时间超过一天，表明第几天的游玩计划进行罗列；
                        4.总开销；
            
            - 动态地图：必须【原样抄写】素材库中对应的 `location` 字段（经纬度），严禁自行编造。
                格式：`[[MAP_ANCHOR:{{景点名称}}|{{location}}]]`
                （例如：若素材库 location 是 "116.39,39.91"，则必须写为 [[MAP_ANCHOR:故宫|116.39,39.91]]）。
            - 其他要求：
                1. 每个景点的介绍必须基于高德提供的真实数据来撰写，禁止凭空编造。
                2. 根据游玩时间的不同，合理安排每天的行程，确保内容详尽且具有吸引力。
                3. 行程单必须包含天气建议、交通工具建议、特色美食推荐、住宿推荐（如果大于一天，根据景点分布距离）和总开销估算。
                4. 一天的行程如果包含多个景点，必须清晰标明每个景点的游玩时间和顺序。
            
                 

            【视觉风格】：
            大气、专业、详细。景点之间请使用 `---` 分割线。不要在坐标后面加任何多余的文字说明。
            """

            # 5. 正式流式吐字
            print(f"🚀 [Step 3] 正在流式生成精美行程单...")
            async for chunk in llm.astream([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]):
                content = getattr(chunk, "content", str(chunk))
                if content:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': content}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)

            yield "data: " + json.dumps({"type": "done", "content": ""}, ensure_ascii=False) + "\n\n"

        except Exception as e:
            # 打印详细错误方便你调试
            print(f"❌ 流式引擎内部崩溃: {str(e)}")
            import traceback
            traceback.print_exc()
            yield "data: " + json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False) + "\n\n"
    return StreamingResponse(event_generator(), headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Content-Type": "text/event-stream"
    })