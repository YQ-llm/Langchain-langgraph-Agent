# Langchain-langgraph-AI行程规划助手🗺️✈️
**仅供参考**\
基于Langchain和Langgraph架构构建的智能行程规划助手，集成高德地图MCP服务，提供个性化的旅行计划生成


## 功能特点
🔹🤖**AI驱动的旅游行程规划**：基于langchain和langgraph框架\
🔹🗺️**高德地图集成**：通过MCP协议接入高德地图服务，支持景点搜索、天气查询、时间选择、路径规划\
🔹🧠**智能工具调用**：Agent自动调用高德地图MCP工具，获取实时天气，路线和POI信息\
🔹🎨**现代化前端**：Vue3 + TypeScript + Vite,流式输出，响应式设计，流畅的用户体验\
🔹📱**完整功能**：涵盖住宿、交通、饮食和景点游览时间推荐

## ⚒️技术栈
## 后端
&nbsp;&nbsp;&nbsp;&nbsp;▪️**框架**：Langchain、langgraph\
&nbsp;&nbsp;&nbsp;&nbsp;▪️**API**：FastAPI\
&nbsp;&nbsp;&nbsp;&nbsp;▪️**MCP工具**：amap-mcp-server(高德地图)\
&nbsp;&nbsp;&nbsp;&nbsp;▪️**LLM**：支持多种LLM提供商(OpenAI,Qwen)
## 前端
&nbsp;&nbsp;&nbsp;&nbsp;▪️**框架**：Vue3 + TypeScript\
&nbsp;&nbsp;&nbsp;&nbsp;▪️**构建工具**：Vite\
&nbsp;&nbsp;&nbsp;&nbsp;▪️**UI组件库**：Ant Desing Vue\
&nbsp;&nbsp;&nbsp;&nbsp;▪️**地图服务**：高德地图\
&nbsp;&nbsp;&nbsp;&nbsp;▪️**HTTP客户端**：Axios
## 📁项目结构

```
LLAgent/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agents/            # Agent实现
│   │   │   └── trip_planner_agent.py
│   │   ├── api/               # FastAPI路由
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── trip.py
│   │   │       └── map.py
│   │   ├── services/          # 服务层
│   │   │   ├── amap_service.py
│   │   │   └── llm_service.py
│   │   ├── models/            # 数据模型
│   │   │   └── schemas.py
│   │   └── config.py          # 配置管理
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   ├── services/          # API服务
│   │   ├── types/             # TypeScript类型
│   │   └── views/             # 页面视图
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 📝使用指南
1.在首页直接和小助手对话（想要规划更精准需要说出）：\
&nbsp;&nbsp;&nbsp;&nbsp;📍目的地城市\
&nbsp;&nbsp;&nbsp;&nbsp;📆旅游时间和天数\
&nbsp;&nbsp;&nbsp;&nbsp;🚕交通方式偏好（可选说）\
&nbsp;&nbsp;&nbsp;&nbsp;⛺住宿偏好（可选说）\
🌟注：除了对话外，也可手动填写-点击首页手动设置-里面有相关选项供参考\
2.小助手结合以上信息进行“生成行程规划”\
3.小助手将：\
&nbsp;&nbsp;&nbsp;&nbsp;⚓调用langchain和langgraph生成初步计划\
&nbsp;&nbsp;&nbsp;&nbsp;🗺️Agent自动调用高德地图MCP工具搜索景点\
&nbsp;&nbsp;&nbsp;&nbsp;🗺️Agent更具高德地图自动获取天气信息和路线规划\
&nbsp;&nbsp;&nbsp;&nbsp;📰最终整合所有的信息流式输出\
4.最终规划结果：\
&nbsp;&nbsp;&nbsp;&nbsp;🌤️行程期间天气信息\
&nbsp;&nbsp;&nbsp;&nbsp;📰每日详细行程\
&nbsp;&nbsp;&nbsp;&nbsp;🗺️景点信息与地图标记\
&nbsp;&nbsp;&nbsp;&nbsp;🫕餐饮推荐
## MCP工具调用
## 📄API文档
启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的API文档
主要端点：\
▪️`POST /api/trip/plan` -生成旅游计划\
▪️`GET /api/map/poi` -搜索POI\
▪️`GET /api/map/weather` - 查询天气\
▪️`POST /api/map/rounte` - 规划路线

## 📜开源协议
MIT License 

## 🙏致谢
[高德地图开放平台](https://lbs.amap.com/) - 地图服务\
[amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) - 高德地图MCP服务器\
[HelloAgents](https://github.com/datawhalechina/Hello-Agents) - 智能体教程\
[HelloAgents](https://github.com/datawhalechina/hello-agents/blob/main/code/chapter13/helloagents-trip-planner) - 智能体应用




