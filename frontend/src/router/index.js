import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import App from '../App.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/app',
      name: 'app',
      component: App,
      meta: { requiresAuth: true } // Add this meta field
    }
  ],
})

// Add this function to check token validity
const isTokenValid = (token) => {
  if (!token) return false
  
  try {
    // Simple check - you could add expiration validation here
    const payload = JSON.parse(atob(token.split('.')[1]))
    const now = Date.now() / 1000
    return payload.exp > now // Check if token is not expired
  } catch (error) {
    console.error('Token validation error:', error)
    return false
  }
}

// Update the navigation guard
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = localStorage.getItem('access_token')
    const isLoggedIn = localStorage.getItem('isLoggedIn')
    
    if (!token || isLoggedIn !== 'true' || !isTokenValid(token)) {
      // Clear invalid auth data
      localStorage.removeItem('access_token')
      localStorage.removeItem('isLoggedIn')
      
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router