<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import L from 'leaflet'
import { api } from '../../api'

const router = useRouter()
const loading = ref(true)
const stats = ref(null)
const regions = ref([])

// ECharts 实例
const pieChart = ref(null)
const barChart = ref(null)
let pieInstance = null
let barInstance = null

// Leaflet 地图
const mapContainer = ref(null)
let map = null

// 元素配色
const elementColors = {
  Pyro: '#ff6b6b', Hydro: '#62adf8', Anemo: '#66cc99',
  Electro: '#b46dfb', Cryo: '#8fe3ff', Geo: '#eacd90', Dendro: '#74b033'
}

onMounted(async () => {
  try {
    const [s, r] = await Promise.all([
      api.getStats(),
      api.getRegionLocations()
    ])
    stats.value = s
    regions.value = r
    loading.value = false

    await nextTick()
    initPieChart()
    initBarChart()
    initMap()
  } catch (e) {
    console.error('加载数据失败:', e)
    loading.value = false
  }
})

function initPieChart() {
  if (!pieChart.value || !stats.value) return
  pieInstance = echarts.init(pieChart.value)

  const data = stats.value.vision_distribution.map(d => ({
    name: d.name,
    value: d.value,
    itemStyle: { color: elementColors[d.name] || '#c89b3c' }
  }))

  pieInstance.setOption({
    title: { text: '元素分布', left: 'center', top: 10,
      textStyle: { fontSize: 16, color: '#333', fontFamily: 'Forum, serif' } },
    tooltip: { trigger: 'item', formatter: '{b}: {c} 位 ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['50%', '55%'],
      roseType: 'area',
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { fontSize: 13 },
      data
    }]
  })
}

function initBarChart() {
  if (!barChart.value || !stats.value) return
  barInstance = echarts.init(barChart.value)

  const data = stats.value.region_distribution
  const regions = data.map(d => d.name)
  const values = data.map(d => d.value)

  barInstance.setOption({
    title: { text: '地区分布', left: 'center', top: 10,
      textStyle: { fontSize: 16, color: '#333', fontFamily: 'Forum, serif' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: regions,
      axisLabel: { fontSize: 12, rotate: regions.length > 6 ? 30 : 0 }
    },
    yAxis: { type: 'value', name: '角色数量' },
    series: [{
      type: 'bar',
      data: values.map((v, i) => ({
        value: v,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#c89b3c' },
            { offset: 1, color: '#e9c26c' }
          ])
        }
      })),
      barWidth: '55%'
    }]
  })
}

function initMap() {
  if (!mapContainer.value || !regions.value.length) return

  map = L.map(mapContainer.value).setView([35, 60], 3)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap & CartoDB',
    maxZoom: 8, minZoom: 2
  }).addTo(map)

  // 自定义图标
  const iconHtml = (count) => `
    <div style="
      background: linear-gradient(135deg, #c89b3c, #e9c26c);
      color: white; width: 40px; height: 40px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 14px; font-weight: bold;
      box-shadow: 0 0 15px rgba(200,155,60,0.6);
      border: 2px solid white;
    ">${count}</div>
  `

  regions.value.forEach(r => {
    if (!r.lat || !r.lng) return
    const icon = L.divIcon({
      html: iconHtml(r.character_count),
      className: 'custom-marker',
      iconSize: [44, 44],
      iconAnchor: [22, 22]
    })

    L.marker([r.lat, r.lng], { icon })
      .addTo(map)
      .bindPopup(`
        <div style="text-align:center;font-family:Forum,serif;">
          <h3 style="color:#c89b3c;margin:0 0 4px;">${r.name_cn}</h3>
          <p style="margin:0;font-size:13px;color:#666;">${r.region}</p>
          <p style="margin:4px 0 0;font-weight:bold;color:#333;">${r.character_count} 位角色</p>
        </div>
      `)
  })

  // 延迟刷新地图尺寸
  setTimeout(() => map.invalidateSize(), 300)
}

// 响应式处理
window.addEventListener('resize', () => {
  pieInstance?.resize()
  barInstance?.resize()
  map?.invalidateSize()
})
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6 font-['IM_Fell_English_SC'] tracking-wider">
      ⚜ Dashboard · Teyvat Overview
    </h2>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-amber-500 animate-pulse text-lg">Loading Teyvat data...</div>
    </div>

    <template v-else>
      <!-- 统计卡片 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition cursor-pointer"
             @click="router.push('/characters')">
          <div class="text-3xl mb-2">👥</div>
          <div class="text-3xl font-bold text-gray-800">{{ stats?.total_characters }}</div>
          <div class="text-sm text-gray-500 mt-1">Total Characters</div>
        </div>
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition">
          <div class="text-3xl mb-2">🌍</div>
          <div class="text-3xl font-bold text-gray-800">{{ stats?.region_distribution?.length || 0 }}</div>
          <div class="text-sm text-gray-500 mt-1">Regions</div>
        </div>
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition">
          <div class="text-3xl mb-2">✨</div>
          <div class="text-3xl font-bold text-gray-800">{{ stats?.vision_distribution?.length || 0 }}</div>
          <div class="text-sm text-gray-500 mt-1">Elements</div>
        </div>
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition">
          <div class="text-3xl mb-2">⚔️</div>
          <div class="text-3xl font-bold text-gray-800">{{ stats?.weapon_distribution?.length || 0 }}</div>
          <div class="text-sm text-gray-500 mt-1">Weapon Types</div>
        </div>
      </div>

      <!-- 图表区 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div ref="pieChart" class="h-80"></div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div ref="barChart" class="h-80"></div>
        </div>
      </div>

      <!-- Leaflet 地图 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <h3 class="text-lg font-semibold text-gray-700 mb-3 font-['IM_Fell_English_SC']">
          🗺️ Teyvat Region Map
        </h3>
        <div ref="mapContainer" class="h-[400px] rounded-xl"></div>
      </div>
    </template>
  </div>
</template>
