<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api'

const router = useRouter()
const loading = ref(true)
const characters = ref([])
const filters = ref({})
const totalPages = ref(0)

// 筛选条件
const search = ref('')
const currentPage = ref(1)
const selectedRegion = ref('')
const selectedVision = ref('')
const selectedWeapon = ref('')
const selectedRarity = ref('')
const pageSize = 12

// 弹窗状态
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const formData = ref({
  character_name: '', star_rarity: 5, region: '', vision: '',
  weapon_type: '', model: '', constellation: '', birthday: '',
  affiliation: '', limited: 'TRUE'
})

// 元素配色
const visionColors = {
  Pyro: 'bg-red-100 text-red-700', Hydro: 'bg-blue-100 text-blue-700',
  Anemo: 'bg-emerald-100 text-emerald-700', Electro: 'bg-purple-100 text-purple-700',
  Cryo: 'bg-cyan-100 text-cyan-700', Geo: 'bg-yellow-100 text-yellow-700',
  Dendro: 'bg-green-100 text-green-700'
}

const regionOptions = ['Mondstadt', 'Liyue', 'Inazuma', 'Sumeru', 'Fontaine', 'Natlan', 'Snezhnaya']
const visionOptions = ['Pyro', 'Hydro', 'Anemo', 'Electro', 'Cryo', 'Geo', 'Dendro']
const weaponOptions = ['Sword', 'Claymore', 'Polearm', 'Catalyst', 'Bow']

async function loadCharacters() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (search.value) params.search = search.value
    if (selectedRegion.value) params.region = selectedRegion.value
    if (selectedVision.value) params.vision = selectedVision.value
    if (selectedWeapon.value) params.weapon_type = selectedWeapon.value
    if (selectedRarity.value) params.star_rarity = selectedRarity.value

    const res = await api.getCharacters(params)
    characters.value = res.data
    totalPages.value = res.total_pages
  } catch (e) {
    console.error('加载角色列表失败:', e)
  } finally {
    loading.value = false
  }
}

async function loadFilters() {
  try {
    filters.value = await api.getFilters()
  } catch (e) { /* ignore */ }
}

onMounted(() => {
  loadFilters()
  loadCharacters()
})

// 搜索防抖
let debounceTimer
watch(search, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { currentPage.value = 1; loadCharacters() }, 300)
})
watch([selectedRegion, selectedVision, selectedWeapon, selectedRarity], () => {
  currentPage.value = 1
  loadCharacters()
})
watch(currentPage, loadCharacters)

// ========== CRUD 操作 ==========

function openCreate() {
  isEditing.value = false
  editingId.value = null
  formData.value = {
    character_name: '', star_rarity: 5, region: '', vision: '',
    weapon_type: '', model: '', constellation: '', birthday: '',
    affiliation: '', limited: 'TRUE'
  }
  showModal.value = true
}

function openEdit(char) {
  isEditing.value = true
  editingId.value = char.id
  formData.value = {
    character_name: char.character_name || '',
    star_rarity: char.star_rarity || 5,
    region: char.region || '',
    vision: char.vision || '',
    weapon_type: char.weapon_type || '',
    model: char.model || '',
    constellation: char.constellation || '',
    birthday: char.birthday || '',
    affiliation: char.affiliation || '',
    limited: char.limited || 'TRUE'
  }
  showModal.value = true
}

async function saveCharacter() {
  try {
    if (isEditing.value) {
      await api.updateCharacter(editingId.value, formData.value)
    } else {
      await api.createCharacter(formData.value)
    }
    showModal.value = false
    loadCharacters()
  } catch (e) {
    alert('操作失败: ' + e.message)
  }
}

async function deleteCharacter(id, name) {
  if (!confirm(`确认删除 "${name}" ？此操作不可恢复。`)) return
  try {
    await api.deleteCharacter(id)
    loadCharacters()
  } catch (e) {
    alert('删除失败: ' + e.message)
  }
}

function viewDetail(id) {
  router.push(`/characters/${id}`)
}

// 分页
const pages = () => {
  const p = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) p.push(i)
  return p
}
</script>

<template>
  <div>
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <h2 class="text-2xl font-bold text-gray-800 font-['IM_Fell_English_SC'] tracking-wider">
        👥 Character Management
      </h2>
      <button
        @click="openCreate"
        class="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-xl font-semibold hover:from-amber-600 hover:to-amber-700 transition shadow-md hover:shadow-lg flex items-center gap-2"
      >
        <span>＋</span> New Character
      </button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <input
          v-model="search"
          type="text"
          placeholder="🔍 Search character name..."
          class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 focus:border-amber-400 outline-none"
        />
        <select v-model="selectedRegion" class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none">
          <option value="">All Regions</option>
          <option v-for="r in regionOptions" :key="r" :value="r">{{ r }}</option>
        </select>
        <select v-model="selectedVision" class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none">
          <option value="">All Elements</option>
          <option v-for="v in visionOptions" :key="v" :value="v">{{ v }}</option>
        </select>
        <select v-model="selectedWeapon" class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none">
          <option value="">All Weapons</option>
          <option v-for="w in weaponOptions" :key="w" :value="w">{{ w }}</option>
        </select>
        <select v-model="selectedRarity" class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none">
          <option value="">All Rarities</option>
          <option :value="4">★★★★</option>
          <option :value="5">★★★★★</option>
        </select>
      </div>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin w-10 h-10 border-4 border-amber-400 border-t-transparent rounded-full"></div>
    </div>

    <!-- 角色卡片网格 -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <div
        v-for="char in characters" :key="char.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md hover:border-amber-200 transition-all cursor-pointer group"
        @click="viewDetail(char.id)"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <h3 class="text-lg font-bold text-gray-800 truncate font-['IM_Fell_English_SC']">
              {{ char.character_name }}
            </h3>
            <p class="text-sm text-gray-500">{{ char.region || 'Unknown' }}</p>
          </div>
          <span class="text-amber-500 text-sm ml-1 shrink-0">
            {{ '★'.repeat(char.star_rarity || 5) }}
          </span>
        </div>

        <div class="flex flex-wrap gap-2 mb-3">
          <span v-if="char.vision" :class="visionColors[char.vision] || 'bg-gray-100 text-gray-600'"
            class="px-2.5 py-0.5 rounded-full text-xs font-semibold">
            {{ char.vision }}
          </span>
          <span class="px-2.5 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
            {{ char.weapon_type || 'Unknown' }}
          </span>
        </div>

        <p v-if="char.affiliation" class="text-xs text-gray-400 truncate mb-3">
          {{ char.affiliation.split(',')[0] }}
        </p>

        <!-- 操作按钮 -->
        <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            @click.stop="openEdit(char)"
            class="flex-1 px-3 py-1.5 text-xs rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 transition"
          >
            ✏️ Edit
          </button>
          <button
            @click.stop="deleteCharacter(char.id, char.character_name)"
            class="px-3 py-1.5 text-xs rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && characters.length === 0" class="text-center py-20 text-gray-400">
      <div class="text-5xl mb-4">🔍</div>
      <p class="text-lg">No characters found</p>
      <p class="text-sm">Try adjusting your search or filters</p>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="flex justify-center items-center gap-2 mt-8">
      <button
        @click="currentPage--"
        :disabled="currentPage === 1"
        class="px-3 py-2 rounded-lg border border-gray-200 disabled:opacity-30 hover:bg-gray-50 transition text-sm"
      >← Prev</button>
      <button
        v-for="p in pages()" :key="p"
        @click="currentPage = p"
        :class="[
          'px-3 py-2 rounded-lg text-sm transition',
          currentPage === p
            ? 'bg-amber-500 text-white shadow'
            : 'border border-gray-200 hover:bg-gray-50'
        ]"
      >{{ p }}</button>
      <button
        @click="currentPage++"
        :disabled="currentPage >= totalPages"
        class="px-3 py-2 rounded-lg border border-gray-200 disabled:opacity-30 hover:bg-gray-50 transition text-sm"
      >Next →</button>
    </div>

    <!-- ========== CRUD 弹窗 ========== -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="showModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto m-4 z-10">
          <!-- 弹窗头 -->
          <div class="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 rounded-t-2xl flex items-center justify-between">
            <h3 class="text-xl font-bold text-gray-800">
              {{ isEditing ? '✏️ Edit Character' : '＋ Add New Character' }}
            </h3>
            <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
          </div>

          <!-- 表单 -->
          <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Character Name *</label>
              <input v-model="formData.character_name" required
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Star Rarity</label>
              <select v-model.number="formData.star_rarity"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none">
                <option :value="4">★★★★</option>
                <option :value="5">★★★★★</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Region</label>
              <select v-model="formData.region"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none">
                <option value="">-- Select --</option>
                <option v-for="r in regionOptions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Vision (Element)</label>
              <select v-model="formData.vision"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none">
                <option value="">-- Select --</option>
                <option v-for="v in visionOptions" :key="v" :value="v">{{ v }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Weapon Type</label>
              <select v-model="formData.weapon_type"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none">
                <option value="">-- Select --</option>
                <option v-for="w in weaponOptions" :key="w" :value="w">{{ w }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Model</label>
              <input v-model="formData.model"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Constellation</label>
              <input v-model="formData.constellation"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Birthday</label>
              <input v-model="formData.birthday" placeholder="e.g. 13-Sep"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-xs font-semibold text-gray-500 mb-1">Affiliation</label>
              <input v-model="formData.affiliation"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-amber-300 outline-none" />
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="sticky bottom-0 bg-white border-t border-gray-100 px-6 py-4 rounded-b-2xl flex justify-end gap-3">
            <button @click="showModal = false"
              class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm hover:bg-gray-50 transition">
              Cancel
            </button>
            <button @click="saveCharacter"
              class="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-xl text-sm font-semibold hover:from-amber-600 hover:to-amber-700 transition shadow">
              {{ isEditing ? '💾 Save Changes' : '＋ Create Character' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
