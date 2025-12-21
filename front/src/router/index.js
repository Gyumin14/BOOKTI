import { createRouter, createWebHistory } from 'vue-router'

import SignupForm from '../components/SignupForm.vue'
import ProfilePage from '../components/ProfilePage.vue'
import BooktiSurveyPage from '../components/BooktiSurveyPage.vue'
import BooktiResultPage from '../components/BooktiResultPage.vue' // ✅ 추가
import BooktiRecommendPage from '../components/BooktiRecommendPage.vue' // ✅ 추가
import LoginForm from '../components/LoginForm.vue'
const Home = {
  template: `
    <div style="max-width:480px;margin:40px auto;">
      <h1>메인 페이지</h1>
      <p>BOOKTI 서비스</p>
      <button @click="$router.push('/signup')">회원가입</button>
      <button style="margin-left:8px" @click="$router.push('/profile')">프로필</button>
    </div>
  `,
}

const routes = [
  { path: '/', component: Home },
  { path: '/signup', component: SignupForm },
  { path: '/profile', component: ProfilePage },
  { path: '/bookti', component: BooktiSurveyPage },          // 설문
  { path: '/bookti/result', component: BooktiResultPage },   // ✅ 결과
  { path: '/bookti/recommend', component: BooktiRecommendPage }, // ✅ 추가
  { path: '/login', component: LoginForm },


]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
router.beforeEach((to) => {
  const publicPaths = ['/', '/signup', '/login', '/bookti', '/bookti/result', '/bookti/recommend']
  const access = localStorage.getItem('access')

  if (!publicPaths.includes(to.path) && !access) {
    return '/login'
  }
})