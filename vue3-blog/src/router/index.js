import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import BlogDetail from '@/pages/BlogDetail.vue'
import EditBlog from '@/pages/EditBlog.vue'
import UserProfile from '@/pages/UserProfile.vue'
import SearchPage from '@/pages/SearchPage.vue'
import { useUserStore } from '@/store/userStore.js'
const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/blog/:id', name: 'BlogDetail', component: BlogDetail },
  { path: '/blog/edit/:id', name: 'EditBlog', component: EditBlog },
  { path: '/blog/create', name: 'CreateBlog', component: EditBlog },
  { path: '/user/:userid', name: 'UserProfile', component: UserProfile },
  { path: '/search', name: 'Search', component: SearchPage }

]

const router = createRouter({
  history: createWebHistory(),
  routes,
})
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (!userStore.isInitialized) {
    await userStore.fetchCurrentUser()
  }


  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !userStore.isLoggedIn) {
    // Redirect to login if trying to access protected route without user
    next('/login')
  } else {
    next()
  }
})
export default router
