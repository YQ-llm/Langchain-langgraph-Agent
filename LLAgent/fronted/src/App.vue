<template>
  <div id="app">
    <a-layout style="min-height: 100vh">
      <!-- 头部：由原来的沉闷深蓝色，升级为富有通透科技感的高雅雾霾渐变蓝 -->
      <a-layout-header style="background: linear-gradient(135deg, #4f63b5 0%, #34478f 100%); padding: 0 50px; box-shadow: 0 4px 20px rgba(79, 99, 181, 0.15);">
        <div style="color: white; font-size: 20px; font-weight: 700; letter-spacing: 1px; display: flex; align-items: center; gap: 10px;">
          🌍 AI 智能旅行规划大屏
        </div>
      </a-layout-header>
      <a-layout-content style="padding: 24px">
        <router-view />
      </a-layout-content>
      <a-layout-footer style="text-align: center; color: #8c90a6; font-size: 13px; background: transparent;">
        AI 智能旅行助手 ©2026 基于 LangChain & LangGraph 状态机
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif;
  background-color: #f1f3ff;
}
</style>