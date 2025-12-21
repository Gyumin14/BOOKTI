import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
    loading: false,
    error: null,
  }),

  actions: {
    setTokens({ access, refresh }) {
      this.access = access
      this.refresh = refresh
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
    },

    clearTokens() {
      this.access = null
      this.refresh = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    },

    setUser(user) {
      this.user = user
      if (user) localStorage.setItem('user', JSON.stringify(user))
      else localStorage.removeItem('user')
    },

    async signup(payload) {
      this.loading = true
      this.error = null

      try {
        const res = await axios.post('/api/signup/', payload)
        // 회원가입 후 바로 설문으로 가니까 user만 저장
        if (res.data?.user) this.setUser(res.data.user)
        return res.data
      } catch (err) {
        this.error = err.response?.data || err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async login({ username, password }) {
      this.loading = true
      this.error = null

      try {
        // ✅ JWT 토큰 발급
        const tokenRes = await axios.post('/api/login/', { username, password })
        this.setTokens(tokenRes.data)

        // ✅ 내 정보 조회
        const meRes = await axios.get('/api/me/')
        this.setUser(meRes.data)

        return meRes.data
      } catch (err) {
        this.error = err.response?.data || err.message
        this.clearTokens()
        throw err
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.setUser(null)
      this.clearTokens()
      this.error = null
      localStorage.removeItem('bookti') // 선택: 로그아웃 시 BOOKTI도 제거
    },
  },
})

/**
 * ✅ axios 인터셉터: access 토큰 자동 첨부
 * (main.js에서 한번만 등록해도 되는데, 여기서 등록해도 동작함)
 */
axios.interceptors.request.use((config) => {
  const access = localStorage.getItem('access')
  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
})
