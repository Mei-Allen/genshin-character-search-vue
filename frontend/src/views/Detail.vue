<template>
  <div v-if="character" class="detail-page">
    <div :style="{ background: `radial-gradient(circle at top center, white, ${elementColor})`, width:'95%', maxWidth:'1200px', margin:'30px auto', padding:'30px', borderRadius:'25px', boxShadow:'0px 0px 20px lightgray' }">

      <!-- ========== 角色头图 + 基础信息 ========== -->
      <div style="display:flex;gap:40px;align-items:flex-start;">
        <div style="width:400px;text-align:center;">
          <img :src="`/static/genshin.image/${character.character_name}.png`"
            style="width:460px;display:block;margin-top:15px;filter:drop-shadow(0 20px 40px rgba(0,0,0,0.12));">
        </div>

        <div style="flex:1;padding-top:20px;font-family:'Forum',serif;">
          <div class="info-panel">
            <h2 :style="{ fontSize:'56px', margin:'0', textAlign:'center', fontFamily:'IM Fell English SC', color:darkColor, letterSpacing:'1px' }">
              {{ character.character_name }}
            </h2>
            <p :style="{ fontSize:'30px', opacity:0.9, marginTop:'8px', marginBottom:'6px', textAlign:'center', color:darkColor }">
              {{ character.vision }} • {{ character.region }}
            </p>
            <p style="text-align:center;font-size:24px;color:#e4bb53;letter-spacing:6px;margin-bottom:35px;">
              {{ '★'.repeat(character.star_rarity || 5) }}
            </p>

            <div class="info-grid">
              <div class="info-card"><h3>Weapon</h3><p>{{ character.weapon_type || '-' }}</p></div>
              <div class="info-card"><h3>Model</h3><p>{{ character.model || '-' }}</p></div>
              <div class="info-card"><h3>Constellation</h3><p>{{ character.constellation || '-' }}</p></div>
              <div class="info-card"><h3>Birthday</h3><p>{{ character.birthday || '-' }}</p></div>
              <div class="info-card affiliation-card">
                <h3>Affiliations</h3>
                <div class="tag-container">
                  <span v-for="tag in affiliationTags" :key="tag" class="affiliation-tag">{{ tag }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 关系图网络环 ========== -->
      <div style="margin-top:40px;display:flex;gap:30px;justify-content:center;">
        <!-- Region 网络 -->
        <div class="network-panel">
          <h3 :style="{ color: darkColor }">Region</h3>
          <div class="network-container">
            <div class="network-ring">
              <div class="orbit-circle"></div>
              <div class="center-node">{{ character.character_name }}</div>
              <router-link v-for="(name, i) in (character.region_characters || []).slice(0,8)" :key="name"
                :to="`/character/${name}`" :class="`orbit-link node-${i+1}`">
                <div class="orbit-node">{{ name }}</div>
              </router-link>
            </div>
          </div>
        </div>

        <!-- Element 网络 -->
        <div class="network-panel">
          <h3 :style="{ color: darkColor }">Element</h3>
          <div class="network-container">
            <div class="network-ring">
              <div class="orbit-circle"></div>
              <div class="center-node">{{ character.character_name }}</div>
              <router-link v-for="(name, i) in (character.element_characters || []).slice(0,8)" :key="name"
                :to="`/character/${name}`" :class="`orbit-link node-${i+1}`">
                <div class="orbit-node">{{ name }}</div>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== ECharts 成长曲线 + 角色资料 ========== -->
      <div class="bottom-layout">
        <div class="analytics-section" ref="analyticsRef">
          <h2 :style="{ color: darkColor }">Character Analytics</h2>

          <div class="chart-card horizontal-chart" ref="hpCard">
            <div class="chart-title" :style="{ color: darkColor }">HP</div>
            <div ref="hpChart" class="chart-canvas"></div>
          </div>
          <div class="chart-card horizontal-chart" ref="atkCard">
            <div class="chart-title" :style="{ color: darkColor }">ATK</div>
            <div ref="atkChart" class="chart-canvas"></div>
          </div>
          <div class="chart-card horizontal-chart" ref="defCard">
            <div class="chart-title" :style="{ color: darkColor }">DEF</div>
            <div ref="defChart" class="chart-canvas"></div>
          </div>
        </div>

        <!-- 角色资料 -->
        <div class="character-extra">
          <h2 :style="{ color: darkColor }">Character Profile</h2>
          <div class="profile-grid">
            <div v-for="item in profileItems" :key="item.label" class="profile-item">
              <label>{{ item.label }}</label>
              <span>{{ item.value }}</span>
            </div>
          </div>

          <!-- Lv.90 最高属性 -->
          <div style="margin-top:24px;">
            <h4 style="font-size:13px;letter-spacing:2px;text-transform:uppercase;opacity:0.5;margin-bottom:12px;">Lv.90 Max Stats</h4>
            <div style="display:flex;gap:12px;text-align:center;">
              <div :style="{ background: 'rgba(255,255,255,0.12)', backdropFilter:'blur(12px)', borderRadius:'14px', padding:'14px 16px', flex:1, border: '1px solid ' + elementColor + '40' }">
                <div :style="{ fontSize:'22px', fontWeight:'bold', color: darkColor }">{{ formatNumber(character.hp_90_90) }}</div>
                <div :style="{ fontSize:'11px', color: darkColor, opacity:0.7 }">Max HP</div>
              </div>
              <div :style="{ background: 'rgba(255,255,255,0.12)', backdropFilter:'blur(12px)', borderRadius:'14px', padding:'14px 16px', flex:1, border: '1px solid ' + elementColor + '40' }">
                <div :style="{ fontSize:'22px', fontWeight:'bold', color: darkColor }">{{ formatNumber(character.atk_90_90) }}</div>
                <div :style="{ fontSize:'11px', color: darkColor, opacity:0.7 }">Max ATK</div>
              </div>
              <div :style="{ background: 'rgba(255,255,255,0.12)', backdropFilter:'blur(12px)', borderRadius:'14px', padding:'14px 16px', flex:1, border: '1px solid ' + elementColor + '40' }">
                <div :style="{ fontSize:'22px', fontWeight:'bold', color: darkColor }">{{ formatNumber(character.def_90_90) }}</div>
                <div :style="{ fontSize:'11px', color: darkColor, opacity:0.7 }">Max DEF</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else style="text-align:center;padding:100px;font-family:'Forum',serif;color:#999;">Loading...</div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'

const route = useRoute()
const character = ref(null)
const loaded = ref(false)

const hpChart = ref(null), atkChart = ref(null), defChart = ref(null)
const hpCard = ref(null), atkCard = ref(null), defCard = ref(null)
const analyticsRef = ref(null)
let observer = null

const elementColors = {
  Pyro: '#ff6b6b', Hydro: '#62adf8', Anemo: '#66cc99',
  Electro: '#b46dfb', Cryo: '#8fe3ff', Geo: '#eacd90', Dendro: '#74b033'
}

const elementColor = computed(() => elementColors[character.value?.vision] || '#f5f5f5')

function darkenColor(hex, factor = 0.7) {
  if (!hex || hex.length < 7) return '#333'
  hex = hex.replace('#', '')
  const r = Math.floor(parseInt(hex.substring(0,2), 16) * factor)
  const g = Math.floor(parseInt(hex.substring(2,4), 16) * factor)
  const b = Math.floor(parseInt(hex.substring(4,6), 16) * factor)
  return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`
}

const darkColor = computed(() => darkenColor(elementColor.value))

const affiliationTags = computed(() => {
  if (!character.value?.affiliation) return []
  return character.value.affiliation.split(',').map(t => t.trim()).filter(Boolean)
})

const profileItems = computed(() => {
  const c = character.value
  if (!c) return []
  return [
    { label: 'Release Date', value: c.release_date || '-' },
    { label: 'Birthday', value: c.birthday || '-' },
    { label: 'Limited', value: c.limited || '-' },
    { label: 'Special Dish', value: c.special_dish || '-' },
    { label: 'Ascension Specialty', value: c.ascension_specialty || '-' },
    { label: 'Boss Material', value: c.ascension_boss_material || '-' },
    { label: 'Talent Book', value: c.talent_book_9_10 || '-' },
    { label: 'Weekly Boss', value: c.talent_weekly || '-' },
    { label: 'Ascension Stat', value: c.ascension_special_stat || '-' },
    { label: 'Ascension Gem', value: c.ascension_gem_0_1 || '-' },
    { label: 'Bonus Stat (Lv.90)', value: c.special_6 || '-' },
    { label: 'CN Voice', value: c.voice_cn || '-' },
    { label: 'JP Voice', value: c.voice_jp || '-' },
    { label: 'EN Voice', value: c.voice_en || '-' },
    { label: 'KR Voice', value: c.voice_kr || '-' },
  ].filter(item => item.value !== '-' && item.value)
})

function formatNumber(val) {
  return val ? Number(val).toLocaleString() : '-'
}

function initCharts() {
  if (!character.value) return
  const levels = ['20','40','50','60','70','80','90']
  const color = elementColor.value
  const rarity = character.value.star_rarity || 5

  const chartConfigs = [
    { el: hpChart.value, key: 'hp', label: 'HP' },
    { el: atkChart.value, key: 'atk', label: 'ATK' },
    { el: defChart.value, key: 'def', label: 'DEF' }
  ]

  chartConfigs.forEach(({ el, key, label }) => {
    if (!el) return
    const inst = echarts.init(el)
    inst.setOption({
      tooltip: { trigger: 'axis' },
      animation: true,
      animationDuration: 2000,
      animationEasing: 'cubicOut',
      legend: { data: [label, `Avg ${rarity}★`], top: 0, textStyle: { fontSize: 11 } },
      grid: { top: 30, left: 52, right: 20, bottom: 5 },
      xAxis: { type: 'category', data: levels },
      yAxis: { type: 'value', name: label, nameTextStyle: { fontSize: 10 } },
      series: [
        {
          name: label, type: 'line',
          data: character.value[`${key}_growth`] || [],
          lineStyle: { color, width: 3 },
          itemStyle: { color },
          symbol: 'circle', symbolSize: 6
        },
        {
          name: `Avg ${rarity}★`, type: 'line',
          data: character.value[`avg_${key}_growth`] || [],
          lineStyle: { color: '#999', width: 2, type: 'dashed' },
          itemStyle: { color: '#999' },
          symbol: 'none'
        }
      ]
    })
  })
}

onMounted(async () => {
  const name = route.params.name
  try {
    const res = await fetch(`/api/characters/by-name/${encodeURIComponent(name)}`)
    if (!res.ok) throw new Error('not found')
    character.value = await res.json()

    // IntersectionObserver 懒加载图表
    await nextTick()
    observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !loaded.value) {
        loaded.value = true

        const cards = [hpCard.value, atkCard.value, defCard.value].filter(Boolean)
        cards.forEach((card, i) => {
          setTimeout(() => card?.classList.add('show'), i * 150)
        })

        setTimeout(() => initCharts(), 100)
      }
    }, { threshold: 0.35 })

    if (analyticsRef.value) observer.observe(analyticsRef.value)
  } catch (e) {
    console.error('加载角色详情失败:', e)
  }
})

watch(() => route.params.name, async (newName) => {
  if (newName) {
    loaded.value = false
    const res = await fetch(`/api/characters/by-name/${encodeURIComponent(newName)}`)
    if (res.ok) character.value = await res.json()
    await nextTick()
    initCharts()
  }
})
</script>

<style scoped>
.detail-page {
  background-color: #f5f5f5;
}

/* ========== 信息面板 ========== */
.info-panel {
  background: rgba(255,255,255,0.18); backdrop-filter: blur(18px);
  padding: 35px; border-radius: 30px;
  border: 1px solid rgba(255,255,255,0.35);
  box-shadow: 0 20px 60px rgba(0,0,0,0.04); margin-bottom: 30px;
}

.info-grid {
  display: grid; grid-template-columns: repeat(2,1fr); gap: 22px;
}

.info-card {
  padding: 20px; background: rgba(255,255,255,0.28);
  backdrop-filter: blur(14px); border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.35);
  box-shadow: 0 15px 40px rgba(0,0,0,0.04); transition: 0.3s;
}
.info-card:hover { transform: translateY(-4px); box-shadow: 0 20px 50px rgba(0,0,0,0.08); }
.info-card h3 { margin: 0 0 12px 0; font-size: 14px; letter-spacing: 2px; opacity: 0.5; text-transform: uppercase; }
.info-card p { margin: 0; font-size: 23px; line-height: 1.35; word-break: break-word; }

.affiliation-card { grid-column: span 2; padding: 28px; }
.tag-container { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 12px; }
.affiliation-tag {
  padding: 12px 22px; background: rgba(255,255,255,0.35);
  backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.45);
  border-radius: 999px; font-size: 22px; color: #333;
  box-shadow: 0 8px 20px rgba(0,0,0,0.05); transition: 0.25s;
}
.affiliation-tag:hover { transform: translateY(-2px); background: rgba(255,255,255,0.55); box-shadow: 0 12px 25px rgba(0,0,0,0.08); }

/* ========== 网络环 ========== */
.network-panel {
  flex: 1; padding: 35px; background: rgba(255,255,255,0.08);
  backdrop-filter: blur(25px); border-radius: 35px;
  box-shadow: 0 10px 40px rgba(255,255,255,0.12) inset, 0 8px 20px rgba(0,0,0,0.03);
  text-align: center;
}
.network-panel h3 { font-size: 34px; margin-bottom: 25px; letter-spacing: 2px; font-family: 'IM Fell English SC', serif; }

.network-container { display: flex; justify-content: center; align-items: center; }
.network-ring { position: relative; width: 450px; height: 400px; }

.center-node {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  width: 115px; height: 115px; border-radius: 50%;
  background: rgba(255,255,255,0.78); backdrop-filter: blur(25px);
  display: flex; justify-content: center; align-items: center;
  font-family: 'IM Fell English SC', serif; font-size: 30px; font-weight: bold;
  z-index: 10;
  box-shadow: 0 15px 40px rgba(255,255,255,0.25), 0 12px 35px rgba(0,0,0,0.06);
  animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
  0%,100% { box-shadow: 0 0 20px rgba(255,255,255,0.25), 0 12px 35px rgba(0,0,0,0.06); }
  50% { box-shadow: 0 0 45px rgba(255,255,255,0.55), 0 12px 35px rgba(0,0,0,0.06); }
}

.orbit-link { position: absolute; transform: translate(-50%,-50%); text-decoration: none; color: inherit; z-index: 5; }
.orbit-node {
  padding: 12px 22px; background: rgba(255,255,255,0.32); backdrop-filter: blur(18px);
  border-radius: 999px; font-size: 22px; white-space: nowrap;
  box-shadow: 0 6px 18px rgba(0,0,0,0.04); transition: 0.3s;
}
.orbit-node:hover { transform: scale(1.08); background: rgba(255,255,255,0.55); box-shadow: 0 12px 24px rgba(0,0,0,0.06); }

.node-1{top:12%;left:50%;animation:float1 3.5s ease-in-out infinite;}
.node-2{top:30%;left:20%;animation:float2 4.1s ease-in-out infinite;}
.node-3{top:30%;left:80%;animation:float3 3.8s ease-in-out infinite;}
.node-4{top:50%;left:12%;animation:float4 4.6s ease-in-out infinite;}
.node-5{top:50%;left:88%;animation:float5 3.7s ease-in-out infinite;}
.node-6{top:72%;left:25%;animation:float6 4.4s ease-in-out infinite;}
.node-7{top:84%;left:50%;animation:float7 3.9s ease-in-out infinite;}
.node-8{top:72%;left:75%;animation:float8 4.2s ease-in-out infinite;}

@keyframes float1{0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(-10px)}}
@keyframes float2{0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(8px)}}
@keyframes float3{0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(-12px)}}
@keyframes float4{0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(10px)}}
@keyframes float5{0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(-9px)}}
@keyframes float6{0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(12px)}}
@keyframes float7{0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(-8px)}}
@keyframes float8{0%,100%{transform:translate(-50%,-50%) translateY(0)}50%{transform:translate(-50%,-50%) translateY(10px)}}

/* ========== 图表区 ========== */
.bottom-layout { display: flex; gap: 50px; align-items: flex-start; margin-top: 80px; }
.analytics-section { flex: 1.2; max-width: 700px; }
.analytics-section h2 { font-family: 'IM Fell English SC', serif; font-size: 35px; text-align: center; margin-bottom: 45px; letter-spacing: 2px; }

.chart-card {
  padding: 30px; margin-bottom: 35px;
  background: rgba(255,255,255,0.12); backdrop-filter: blur(20px);
  border-radius: 28px; box-shadow: 0 10px 30px rgba(0,0,0,0.04);
  opacity: 0; transform: translateY(20px); transition: all 0.8s ease;
}
.chart-card.show { opacity: 1; transform: translateY(0); }
.horizontal-chart { display: flex; align-items: center; gap: 25px; }
.chart-title { width: 70px; flex-shrink: 0; font-family: 'IM Fell English SC', serif; font-size: 28px; font-weight: bold; text-align: center; }
.chart-canvas { flex: 1; height: 200px; min-height: 200px; }

.character-extra { flex: 1; padding: 0; }
.character-extra h2 { font-family: 'IM Fell English SC', serif; font-size: 34px; margin-bottom: 30px; text-align: left; }
.profile-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 22px 24px; }
.profile-item { padding-bottom: 12px; border-bottom: 1px solid rgba(0,0,0,0.08); }
.profile-item label { display: block; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; opacity: 0.5; margin-bottom: 6px; }
.profile-item span { font-size: 22px; line-height: 1.4; }
</style>
