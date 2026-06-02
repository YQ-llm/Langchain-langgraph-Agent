# Langchain-langgraph-AI行程规划助手
仅供参考
基于Langchain和Langgraph架构构建的智能行程规划助手，集成高德地图MCP服务，提供个性化的旅行计划生成

## 功能特点
AI驱动的旅游行程规划：基于langchain和langgraph框架\
高德地图集成：通过MCP协议接入高德地图服务，支持景点搜索、天气查询、时间选择、路径规划\
智能工具调用：Agent自动调用高德地图MCP工具，获取实时天气，路线和POI信息\
现代化前端：Vue3 + TypeScript + Vite,流式输出，响应式设计，流畅的用户体验\n
完整功能：包含住宿、交通、饮食和景点游览时间推荐\n

## 技术栈
## 后端
框架：Langchain、langgraph\n
API：FastAPI\n
MCP工具：amap-mcp-server(高德地图)\n
LLM：支持多种LLM提供商(OpenAI,Qwen)\n
## 前端
框架：Vue3 + TypeScript\n
构建工具：Vite\n
UI组件库：Ant Desing Vue\n
地图服务：高德地图\n
HTTP客户端：Axios\n
## 项目结构

## 使用指南
1.在首页直接和小助手对话（想要规划更精准需要说出）：\n
目的地城市\n
旅游时间和天数\n
交通方式偏好（可选说）\n
住宿偏好（可选说）\n
注：出来对话外，也可手动填写-点击首页手动设置-里面有相关选项供参考\n
2.小助手结合以上信息进行“生成行程规划”\n
3.小助手将：\n
调用langchain和langgraph生成初步计划\n
Agent自动调用高德地图MCP工具搜索景点\n
Agent更具高德地图自动获取天气信息和路线规划\n
最终整合所有的信息流式输出\n
4.最终规划结果：\n
行程期间天气信息\n
每日详细行程\n
景点信息与地图标记\n
餐饮推荐\n
## 核心实现
## MCP工具调用
## API文档
启动后端服务后，访问http://localhost:8000/docs查看完整的API文档\n
主要端点：\n
POST /api/trip/plan -生成旅游计划\n
GET /api/map/poi -搜索POI\n
GET /api/map/weather - 查询天气\n
POST /api/map/rounte - 规划路线\n

## 开源协议

## 致谢
 





