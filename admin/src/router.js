import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './pages/Dashboard.vue'
import Add from './pages/Add.vue'
import Users from './pages/Users.vue'

export default createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/add', component: Add },
    { path: '/users', component: Users }
  ]
})
