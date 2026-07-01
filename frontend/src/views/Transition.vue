<template>
  <div v-if="character" class="transition-page">

    <div class="encounter">
      <div class="world-light" :style="{ background: `radial-gradient(circle at center, white 0%, ${elementColor} 100%)` }"></div>
      <div class="reveal-wave" :style="{ background: `radial-gradient(circle, rgba(255,255,255,1) 0%, ${elementColor} 35%, transparent 100%)` }"></div>
      <div class="element-symbol">
        <img :src="`/static/genshin.image/Element_${character.vision}.webp`">
      </div>

      <div class="particle p1"></div><div class="particle p2"></div>
      <div class="particle p3"></div><div class="particle p4"></div>
      <div class="particle p5"></div><div class="particle p6"></div>
      <div class="particle p7"></div><div class="particle p8"></div>

      <img :src="`/static/genshin.image/${character.character_name}.png`" class="character-img">

      <div class="name">{{ character.character_name }}</div>
      <div class="subtitle">{{ character.region }} · {{ character.vision }}</div>
      <div class="loading">Loading Character Archive</div>
    </div>

  </div>
  <div v-else style="height:100vh;display:flex;justify-content:center;align-items:center;background:black;color:white;font-family:'Forum',serif;">
    Loading...
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const character = ref(null)

const elementColors = {
  Pyro: '#ff6b6b', Hydro: '#62adf8', Anemo: '#66cc99',
  Electro: '#b46dfb', Cryo: '#8fe3ff', Geo: '#eacd90', Dendro: '#74b033'
}

const elementColor = computed(() => {
  return character.value ? (elementColors[character.value.vision] || '#c89b3c') : '#c89b3c'
})

onMounted(async () => {
  const name = route.params.name
  try {
    const res = await fetch(`/api/characters/by-name/${encodeURIComponent(name)}`)
    if (!res.ok) throw new Error('not found')
    character.value = await res.json()

    setTimeout(() => {
      router.push(`/character/${encodeURIComponent(name)}/detail`)
    }, 5500)
  } catch (e) {
    console.error('角色加载失败:', e)
    setTimeout(() => {
      router.push(`/character/${encodeURIComponent(name)}/detail`)
    }, 2000)
  }
})
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }

.transition-page {
  height: 100vh; overflow: hidden; display: flex;
  justify-content: center; align-items: center;
  background: black; font-family: 'Forum', serif;
}

.encounter {
  position: relative; width: 100%; height: 100vh;
  display: flex; justify-content: center; align-items: center;
  flex-direction: column; overflow: hidden;
}

.world-light {
  position: absolute; inset: 0;
  opacity: 0; z-index: 0;
  animation: worldReveal 1s forwards; animation-delay: 1.8s;
}

.reveal-wave {
  position: absolute; left: 50%; top: 42%;
  width: 50px; height: 50px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(200,155,60,1) 35%, transparent 100%);
  transform: translate(-50%,-50%) scale(0);
  opacity: 0; z-index: 2;
  animation: waveReveal 0.8s forwards; animation-delay: 1s;
}

.element-symbol {
  position: absolute; left: 50%; top: 42%;
  transform: translate(-50%,-50%);
  opacity: 0; z-index: 3;
  animation: symbolAppear .4s forwards, symbolPulse 0.4s ease-in-out infinite, symbolFade 2s forwards;
  animation-delay: 0s, .8s, 1.2s;
}
.element-symbol img {
  width: 100px;
  filter: drop-shadow(0 0 30px rgba(255,255,255,.9)) drop-shadow(0 0 80px rgba(255,255,255,.5));
}

.particle {
  position: absolute; width: 5px; height: 5px; border-radius: 50%;
  background: white; opacity: .2; z-index: 2;
  box-shadow: 0 0 4px rgba(255,255,255,.5), 0 0 8px rgba(255,255,255,.3);
  animation: twinkle 2s infinite, particleFade .8s forwards;
  animation-delay: 0s, 1.5s;
}
.p1{left:44%;top:38%;} .p2{left:56%;top:38%;} .p3{left:41%;top:47%;} .p4{left:59%;top:46%;}
.p5{left:48%;top:33%;} .p6{left:52%;top:53%;} .p7{left:46%;top:50%;} .p8{left:54%;top:34%;}

.character-img {
  height: 620px; position: relative; z-index: 4;
  opacity: 0; transform: translateY(60px) scale(.85);
  filter: blur(12px) drop-shadow(0 25px 50px rgba(0,0,0,.15));
  animation: characterAppear 1.3s ease forwards; animation-delay: 1.3s;
}

.name {
  font-family: 'IM Fell English SC', serif; font-size: 64px;
  letter-spacing: 2px; color: #2d2039; margin-top: -10px;
  opacity: 0; z-index: 5;
  animation: fadeIn 1s forwards; animation-delay: 2.8s;
}

.subtitle {
  font-size: 28px; color: #555; margin-top: 10px; letter-spacing: 2px;
  opacity: 0; z-index: 5;
  animation: fadeIn 1s forwards; animation-delay: 3.1s;
}

.loading {
  margin-top: 45px; font-size: 22px; letter-spacing: 4px; color: #666;
  opacity: 0; z-index: 5;
  animation: fadeIn 1s forwards; animation-delay: 3.5s;
}
.loading::after { content: ""; animation: dots 1.5s infinite; }

@keyframes worldReveal { from { opacity: 0; } to { opacity: 1; } }
@keyframes waveReveal {
  0% { opacity: .8; filter: blur(0px); transform: translate(-50%,-50%) scale(.2); }
  30% { opacity: 1; }
  100% { opacity: 0; filter: blur(20px); transform: translate(-50%,-50%) scale(45); }
}
@keyframes symbolAppear { from { opacity: 0; transform: translate(-50%,-50%) scale(.4); } to { opacity: 1; transform: translate(-50%,-50%) scale(1); } }
@keyframes symbolPulse { 0%,100% { transform: translate(-50%,-50%) scale(1); opacity: .75; } 50% { transform: translate(-50%,-50%) scale(1.08); opacity: 1; } }
@keyframes symbolFade { 0% { opacity: 1; transform: translate(-50%,-50%) scale(1); } 100% { opacity: 0; transform: translate(-50%,-50%) scale(2.5); filter: blur(12px); } }
@keyframes particleFade { to { opacity: 0; } }
@keyframes twinkle { 0% { opacity: 0; transform: scale(.3); } 50% { opacity: 1; transform: scale(1.5); } 100% { opacity: 0; transform: scale(.3); } }
@keyframes characterAppear { to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0) drop-shadow(0 25px 50px rgba(0,0,0,.15)); } }
@keyframes fadeIn { to { opacity: 1; } }
@keyframes dots { 0% { content: ""; } 33% { content: "."; } 66% { content: ".."; } 100% { content: "..."; } }
</style>
