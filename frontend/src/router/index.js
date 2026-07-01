import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ========== 公共路由（全屏，v2 视觉效果）==========
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: 'Genshin Archive · Teyvat' }
  },
  {
    path: '/character/:name',
    name: 'Transition',
    component: () => import('../views/Transition.vue'),
    meta: { title: 'Loading Character...' }
  },
  {
    path: '/character/:name/detail',
    name: 'Detail',
    component: () => import('../views/Detail.vue'),
    meta: { title: 'Character Detail' }
  },

  // ========== 管理路由（TailAdmin 侧边栏布局）==========
  {
    path: '/admin',
    component: () => import('../layouts/AdminShell.vue'),
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { title: 'Admin · Dashboard' }
      },
      {
        path: 'characters',
        name: 'AdminCharacters',
        component: () => import('../views/admin/AdminChars.vue'),
        meta: { title: 'Admin · Characters' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  document.title = to.meta.title || 'Genshin Archive'
})

export default router
