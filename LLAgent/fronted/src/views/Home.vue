<template>
  <div class="home-container">
    <!-- 背景高雅微渐变装饰物 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 侧边隐藏手动表单抽屉 -->
    <a-drawer
      title="高级旅行选项"
      placement="right"
      :visible="drawerVisible"
      :width="450"
      @close="drawerVisible = false"
    >
      <div class="drawer-form-wrapper">
        <p style="color: #666; margin-bottom: 24px;">手动配置精确参数：</p>
        <a-form :model="formData" layout="vertical" @finish="handleSubmit">
          <a-form-item label="目的地" name="city">
            <a-input v-model:value="formData.city" size="large" />
          </a-form-item>
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="开始日期">
                <a-date-picker v-model:value="formData.start_date" style="width: 100%" size="large" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="结束日期">
                <a-date-picker v-model:value="formData.end_date" style="width: 100%" size="large" />
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="交通方式">
                <a-select v-model:value="formData.transportation" size="large">
                  <a-select-option value="公共交通">🚇 公共交通</a-select-option>
                  <a-select-option value="自驾">🚗 自驾</a-select-option>
                  <a-select-option value="混合">🔀 混合</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="住宿偏好">
                <a-select v-model:value="formData.accommodation" size="large">
                  <a-select-option value="经济型酒店">💰 经济型酒店</a-select-option>
                  <a-select-option value="舒适型酒店">🏨 舒适型酒店</a-select-option>
                  <a-select-option value="豪华酒店">⭐ 豪华酒店</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          <a-button type="primary" html-type="submit" size="large" block style="margin-top: 24px; border-radius: 12px; height: 50px;">
            更新并生成
          </a-button>
        </a-form>
      </div>
    </a-drawer>

    <!-- 主交互视窗 (Fluid Design) -->
    <div class="chat-wrapper">
      <!-- 顶部状态栏 -->
      <div class="page-header-compact">
        <div class="header-logo-section">
          <span class="header-avatar-icon">🌍</span>
          <div>
            <h1 class="chat-title">AI 行程规划助手</h1>
            <p class="chat-subtitle">高德数据驱动 · 通义千问流式驱动</p>
          </div>
        </div>
        <a-button type="link" class="drawer-trigger" @click="drawerVisible = true">
          ⚙️ 手动配置
        </a-button>
      </div>

      <!-- 对话历史滚动区域 -->
      <div class="chat-history" ref="historyContainer">
        <!-- 欢迎引导区 -->
        <div class="welcome-guide-wrapper" v-if="chatList.length === 0">
          <div class="mascot-container">
            <!-- 使用一个更通用的高画质头像链接，防止本地路径失效 -->
            <img src="https://image.pollinations.ai/prompt/cute%203D%20chibi%20girl%20explorer%20backpacking%20adventure%20holding%20map?width=260&height=260&nologo=true" class="mascot-img" />
          </div>
          <h2 class="welcome-text">嗨！我是你的 AI 行程规划助手</h2>
        </div>

        <!-- 4格动作卡片 -->
        <div class="action-grid" v-if="chatList.length === 0">
          <div class="action-card color-blue" @click="handleActionCard('为我发现目的地')">
            <div class="card-icon">🌴</div>
            <div class="card-title">为我发现美景</div>
            <div class="card-subtitle">为你发现热点美景</div>
          </div>
          <div class="action-card color-cyan" @click="handleActionCard('为我寻找便宜高铁票')">
            <div class="card-icon">⛺</div>
            <div class="card-title">为我找舒适的住宿</div>
            <div class="card-subtitle">舒适住宿推荐指南</div>
          </div>
          <div class="action-card color-purple" @click="handleActionCard('为我规划行程')">
            <div class="card-icon">🗺️</div>
            <div class="card-title">为我规划行程</div>
            <div class="card-subtitle">智能个性化行程推荐</div>
          </div>
          <div class="action-card color-teal" @click="handleActionCard('为我查询目的地天气')">
            <div class="card-icon">🌤️</div>
            <div class="card-title">为我查询目的地天气</div>
            <div class="card-subtitle">实时天气出行参考</div>
          </div>
        </div>

        <!-- 聊天气泡列表 -->
        <div
          v-for="(chat, index) in chatList"
          :key="index"
          :class="['chat-bubble', chat.role]"
        >
          <div class="bubble-avatar-wrapper">
            <div class="bubble-avatar">{{ chat.role === 'user' ? '👤' : '🤖' }}</div>
          </div>
          <div class="bubble-content-box">
            <div 
              v-if="chat.role === 'ai'" 
              class="markdown-body" 
              v-html="renderMarkdown(chat.content, true, index)"
            ></div>
            <div v-else class="bubble-text">{{ chat.content }}</div>
          </div>
        </div>

        <!-- 状态加载气泡 -->
        <div class="chat-bubble ai" v-if="loading && currentStreamText === ''">
          <div class="bubble-avatar-wrapper">
            <div class="bubble-avatar">🤖</div>
          </div>
          <div class="bubble-content-box loading-box">
            <p class="loading-status-text">🧠 {{ loadingStatus }}</p>
          </div>
        </div>

        <div class="bottom-safety-spacing"></div>
      </div>

      <!-- 底部圆角胶囊输入栏 -->
      <div class="bottom-input-bar">
        <div class="input-container">
          <a-input
            v-model:value="userRawInput"
            placeholder="请输入内容"
            size="large"
            class="capsule-input"
            @pressEnter="handleSendStreamChat"
            :disabled="loading"
          >
            <template #prefix>
              <div class="input-prefix-icon">🎙️</div>
            </template>
            <template #suffix>
              <a-button
                type="primary"
                shape="circle"
                class="send-button"
                @click="handleSendStreamChat"
                :loading="loading"
              >
                <span class="send-icon">🚀</span>
              </a-button>
            </template>
          </a-input>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onUnmounted } from 'vue'
import MarkdownIt from 'markdown-it'
import { message } from 'ant-design-vue'
import dayjs, { Dayjs } from 'dayjs'
import AMapLoader from '@amap/amap-jsapi-loader'
import type { TripFormData } from '@/types'

// ================= 1. 配置区 =================
window._AMapSecurityConfig = {
  securityJsCode: import.meta.env.VITE_AMAP_SECURITY_KEY, 
}

const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true
})

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// ================= 2. 状态变量定义 =================
const chatList = ref<Array<{ role: 'user' | 'ai'; content: string }>>([])
const userRawInput = ref('')
const loading = ref(false)
const loadingStatus = ref('')
const currentStreamText = ref('')
const showMapButton = ref(false)
const historyContainer = ref<HTMLElement | null>(null)
const drawerVisible = ref(false)
const renderedMapIds = new Set<string>() 
let eventSource: EventSource | null = null

const formData = reactive<TripFormData & { start_date: Dayjs | null; end_date: Dayjs | null }>({
  city: '',
  start_date: null,
  end_date: null,
  travel_days: 3,
  transportation: '公共交通',
  accommodation: '舒适型酒店',
  preferences: [],
  free_text_input: ''
})

// ================= 3. 功能函数 =================

const renderMarkdown = (text: string, isAi: boolean, index: number) => {
  if (!isAi) return text

  // 1. 识别并隐藏坐标点锚点，防止页面显示丑陋的自定义标签
   const mapRegex = /\[\[MAP_ANCHOR:\s*(.*?)\s*\|\s*(.*?)\s*\]\]/g
  let processedText = text.replace(mapRegex, '') 

  // 2. 正常渲染 Markdown 文字
  let htmlContent = md.render(processedText)

  // 3. 在每段回复末尾追加一个用于最后显示总览地图的容器
  const finalMapId = `final_map_${index}`
  // 注意：初始高度为 0，只有在 done 之后由 JS 撑开
  htmlContent += `<div id="${finalMapId}" class="final-itinerary-map"></div>`

  return htmlContent
}

const scrollToBottom = async () => {
  await nextTick()
  if (historyContainer.value) {
    historyContainer.value.scrollTop = historyContainer.value.scrollHeight
  }
}

// 核心：在模型回答完毕后，一次性渲染包含 1, 2, 3 标记的路线地图
const renderFinalRouteMap = async (fullText: string, bubbleIndex: number) => {
  await nextTick()
  
  // 1. 更加健壮的正则：匹配 [[MAP_ANCHOR: 内容 ]]
  const mapRegex = /\[\[MAP_ANCHOR:(.*?)\]\]/g
  const matches = [...fullText.matchAll(mapRegex)]
  if (matches.length === 0) return

  const spots = matches.map((m, index) => {
  const content = m[1]; // 获取到 "景点名|坐标字符串"
  const parts = content.split('|')
  if (parts.length < 2) return null

  const name = parts[0].trim()
  const coordStr = parts[1].trim()
  
  // 自动处理逗号或竖线分隔
  const coords = coordStr.split(/[,\s]+/)
  if (coords.length < 2) return null

  let lng = parseFloat(coords[0].replace(/[^-0-9.]/g, ''))
  let lat = parseFloat(coords[1].replace(/[^-0-9.]/g, ''))

  // 💡 智能自动纠偏：在中国境内，经度(Lng)一般在 73-135 之间，纬度(Lat)在 18-54 之间
  // 如果发现第一个数小于第二个数，说明 AI 把纬度写在前面了，我们自动交换位置
  if (lat > lng && lat > 70) {
    console.warn(`🔄 自动纠正坐标顺序: ${name}`);
    [lng, lat] = [lat, lng];
  }

  if (isNaN(lng) || isNaN(lat)) return null
  return { name, lng, lat, order: index + 1 }
}).filter(s => s !== null)

  if (spots.length === 0) {
    console.warn("未发现有效坐标点，取消地图渲染")
    return
  }

  const mapId = `final_map_${bubbleIndex}`
  const mapEl = document.getElementById(mapId)
  if (!mapEl) return

  mapEl.style.height = '360px'
  mapEl.style.marginTop = '20px'
  mapEl.style.display = 'block'

  try {
    const AMap = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_WEB_JS_KEY,
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline']
    })

    const map = new AMap.Map(mapId, {
      viewMode: '3D',
      zoom: 13,
      // 默认中心点设为第一个景点
      center: [spots[0].lng, spots[0].lat],
      mapStyle: 'amap://styles/normal'
    })

    const markers: any[] = []
    const pathCoords: any[] = []

    spots.forEach(spot => {
      const pos = [spot.lng, spot.lat]
      pathCoords.push(pos)

      const marker = new AMap.Marker({
        position: pos,
        content: `<div class="custom-route-marker">${spot.order}</div>`,
        title: spot.name,
        // 将偏移量改为图标中心
        offset: new AMap.Pixel(-16, -16),
        map: map
      })
      markers.push(marker)
    })

    // 💡 关键：确保地图自动缩放，能完整看到 1, 2, 3 所有标记
    if (markers.length > 0) {
      map.setFitView(markers, false, [60, 60, 60, 60])
    }

    // 绘制行程虚线
    if (pathCoords.length > 1) {
      new AMap.Polyline({
        path: pathCoords,
        strokeColor: "#7452ff",
        strokeWeight: 5,
        strokeOpacity: 0.6,
        strokeStyle: "dashed",
        map: map
      })
    }

  } catch (err) {
    console.error("地图汇总渲染失败:", err)
  }
}

const handleActionCard = (query: string) => {
  userRawInput.value = query
  handleSendStreamChat()
}

// 核心：流式对话处理逻辑
const handleSendStreamChat = async () => {
  const query = userRawInput.value.trim()
  if (!query) return
  
  // 每一轮新对话，清空之前的锁
  renderedMapIds.clear()

  chatList.value.push({ role: 'user', content: query })
  userRawInput.value = ''
  await scrollToBottom()
  
  loading.value = true
  loadingStatus.value = 'AI 正在深度思考规划中...'
  currentStreamText.value = ''
  showMapButton.value = false
  
  const aiBubbleIndex = chatList.value.push({ role: 'ai', content: '' }) - 1
  
  try {
    const url = `${API_BASE_URL}/api/trip/plan_stream?user_message=${encodeURIComponent(query)}`
    eventSource = new EventSource(url)

    eventSource.onmessage = async (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'status') {
        loadingStatus.value = data.content
      } else if (data.type === 'chunk') {
        currentStreamText.value += data.content
        chatList.value[aiBubbleIndex].content = currentStreamText.value
        await scrollToBottom()
      } else if (data.type === 'done') {
        if (eventSource) eventSource.close()
        loading.value = false
        showMapButton.value = true
        
        // 💡 重点：话说完后，延迟触发最终总览地图渲染
        setTimeout(() => {
          renderFinalRouteMap(currentStreamText.value, aiBubbleIndex)
        }, 600)
      } else if (data.type === 'error') {
        if (eventSource) eventSource.close()
        loading.value = false
        message.error('流式生成异常中断')
      }
    }

    eventSource.onerror = () => {
      if (eventSource) eventSource.close()
      loading.value = false
    }
  } catch (error) {
    loading.value = false
    message.error('无法连接至 AI 服务')
  }
}

const handleSubmit = async () => {
  drawerVisible.value = false
  userRawInput.value = `我想去${formData.city}旅行。`
  handleSendStreamChat()
}

onUnmounted(() => {
  if (eventSource) eventSource.close()
})
</script>

<style scoped>
/* 全局锁死外部滚动条，实现 Fluid 响应式 */
.home-container {
  height: 100vh;
  width: 100vw;
  background: #e8eaff;
  position: relative;
  overflow: hidden; 
  display: flex;
  justify-content: center;
  align-items: center;
}

.bg-decoration {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.45);
}

.circle-1 { width: 30vw; height: 30vw; top: -10vw; left: -10vw; }
.circle-2 { width: 20vw; height: 20vw; bottom: 5%; right: -5vw; }
.circle-3 { width: 15vw; height: 15vw; bottom: -5vw; left: 10%; }

/* 主视窗自适应高宽 */
.chat-wrapper {
  width: 95vw;
  max-width: 680px; 
  height: 94vh; 
  background: #f1f3ff;
  border-radius: 40px; 
  box-shadow: 0 25px 80px rgba(102, 110, 234, 0.2);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.page-header-compact {
  padding: 18px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(225, 227, 255, 0.6);
  background: rgba(241, 243, 255, 0.95);
  backdrop-filter: blur(10px);
  z-index: 10;
  flex-shrink: 0;
}

.header-logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-avatar-icon { font-size: 22px; }
.chat-title { font-size: 15px; font-weight: 700; color: #1e2432; margin: 0; }
.chat-subtitle { font-size: 11px; color: #8c90a6; margin: 0; }
.drawer-trigger { font-size: 12px; font-weight: 600; color: #7452ff; }

/* 内部高雅滚动条 */
.chat-history {
  flex: 1;
  padding: 3vh 28px 120px; 
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.chat-history::-webkit-scrollbar { width: 5px; }
.chat-history::-webkit-scrollbar-thumb { background: rgba(116, 82, 255, 0.1); border-radius: 10px; }

.welcome-guide-wrapper { text-align: center; margin-top: 2vh; }
.mascot-container { width: min(18vh, 120px); height: min(18vh, 120px); margin: 0 auto 15px; }
.mascot-img { width: 100%; height: 100%; object-fit: contain; border-radius: 20px; }
.welcome-text { font-size: 18px; font-weight: 700; color: #1a1e29; }

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-width: 500px;
  margin: 10px auto;
  width: 100%;
}

.action-card {
  padding: 22px 18px;
  border-radius: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255,255,255,0.4);
}

.action-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }

/* 复刻截图中的鲜艳扁平色彩 */
.color-blue { background: #00f2fe; color: #004e52; }
.color-cyan { background: #00eddf; color: #004d49; }
.color-purple { background: #12fff7; color: #1e3c72; }
.color-teal { background: #00ecc2; color: #003d32; }

.card-icon { font-size: 24px; margin-bottom: 8px; }
.card-title { font-size: 14px; font-weight: 700; margin-bottom: 3px; }
.card-subtitle { font-size: 11px; opacity: 0.8; }

.chat-bubble { display: flex; gap: 14px; max-width: 90%; }
.bubble-avatar {
  width: 40px; height: 40px; background: #ffffff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 18px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.04);
}

.bubble-content-box {
  background: #ffffff; padding: 16px 20px; border-radius: 22px;
  box-shadow: 0 3px 15px rgba(102, 126, 234, 0.05);
  border: 1px solid rgba(230, 233, 255, 0.8);
  font-size: 14.5px; line-height: 1.7; color: #2c3e50;
}

.chat-bubble.user { align-self: flex-end; flex-direction: row-reverse; }
.chat-bubble.user .bubble-content-box {
  background: linear-gradient(135deg, #7452ff 0%, #5438c7 100%);
  color: white; border-radius: 22px; border: none;
  box-shadow: 0 8px 25px rgba(116, 82, 255, 0.2);
}
.chat-bubble.user .bubble-avatar { background: #7452ff; color: white; }

/* 底部胶囊输入框 */
.bottom-input-bar {
  position: absolute; bottom: 0; left: 0; width: 100%;
  padding: 15px 30px 25px;
  background: linear-gradient(to top, #f1f3ff 80%, rgba(241, 243, 255, 0) 100%);
  z-index: 20;
}

.input-container { max-width: 580px; margin: 0 auto; position: relative; }

.capsule-input :deep(.ant-input) {
  height: 54px; border-radius: 27px; padding-left: 50px; padding-right: 60px;
  border: 2px solid #e1e4fa !important; box-shadow: 0 10px 30px rgba(102,126,234,0.06);
}

.input-prefix-icon { position: absolute; left: 18px; top: 16px; font-size: 18px; color: #7452ff; z-index: 5; }
.send-button { width: 42px; height: 42px; background: #7452ff !important; border: none !important; }

/* Markdown 内容样式：图片大气展示 */
.markdown-body :deep(img) {
  width: 100%; max-width: 100%; border-radius: 15px; margin: 15px 0;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1); object-fit: cover; aspect-ratio: 16/9;
}

/* 最终行程总览地图容器 */
.final-itinerary-map {
  width: 100%; display: none; /* 初始隐藏，说完话后再显现 */
  border-radius: 24px; background: #f0f2f5; overflow: hidden;
  box-shadow: 0 15px 45px rgba(102, 126, 234, 0.15); border: 3px solid white;
}

/* 📍 1, 2, 3 数字标记样式 */
:deep(.custom-route-marker) {
  width: 32px; height: 32px; background: linear-gradient(135deg, #7452ff 0%, #5438c7 100%);
  color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 15px; border: 2.5px solid white; box-shadow: 0 5px 15px rgba(0,0,0,0.25);
}

/* 隐藏 AMap 多余组件 */
:deep(.amap-logo), :deep(.amap-copyright) { display: none !important; }
</style>