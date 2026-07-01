/** API 请求层 - 所有后端接口封装 */

// 本地开发用空字符串，靠 Vite proxy 转发 /api
// 生产环境用完整后端 URL，在 Render 环境变量中设置 VITE_BACKEND_URL
const BACKEND = import.meta.env.VITE_BACKEND_URL || ''
const BASE = BACKEND ? `${BACKEND}/api` : '/api'

/** 构建完整的 API URL，给不能走 api 对象的直接 fetch 调用使用 */
export function apiUrl(path) {
  return `${BASE}${path}`
}

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  // 角色列表
  getCharacters(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/characters?${q}`)
  },

  // 角色详情（按 ID）
  getCharacter(id) {
    return request(`/characters/${id}`)
  },

  // 角色详情（按名字）
  getCharacterByName(name) {
    return request(`/characters/by-name/${encodeURIComponent(name)}`)
  },

  // 新增角色
  createCharacter(data) {
    return request('/characters', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  // 更新角色
  updateCharacter(id, data) {
    return request(`/characters/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  },

  // 删除角色
  deleteCharacter(id) {
    return request(`/characters/${id}`, {
      method: 'DELETE'
    })
  },

  // 筛选选项
  getFilters() {
    return request('/filters')
  },

  // Dashboard 统计
  getStats() {
    return request('/stats')
  },

  // 地图位置
  getRegionLocations() {
    return request('/region-locations')
  }
}
