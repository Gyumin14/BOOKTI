<template>
  <div class="wrap">
    <div class="card">
      <h1>로그인</h1>

      <form @submit.prevent="handleLogin">
        <div class="group">
          <label>아이디</label>
          <input v-model="username" required />
        </div>

        <div class="group">
          <label>비밀번호</label>
          <input v-model="password" type="password" required />
        </div>

        <button class="btn" :disabled="auth.loading">
          {{ auth.loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <div v-if="msg" class="msg">{{ msg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const msg = ref('')

async function handleLogin() {
  msg.value = ''
  try {
    await auth.login({ username: username.value, password: password.value })
    router.push('/profile')
  } catch (e) {
    msg.value = '로그인 실패 (아이디/비밀번호 확인)'
  }
}
</script>

<style scoped>
.wrap{min-height:100vh;display:flex;justify-content:center;align-items:center;background:#f6f7fb;padding:20px}
.card{width:100%;max-width:420px;background:#fff;border-radius:14px;padding:28px;box-shadow:0 10px 25px rgba(0,0,0,.08)}
.group{margin-bottom:14px}
label{display:block;margin-bottom:6px;color:#555;font-weight:700}
input{width:100%;padding:12px;border:1px solid #ddd;border-radius:10px}
.btn{width:100%;padding:12px;border:0;border-radius:10px;font-weight:900;cursor:pointer}
.btn:disabled{opacity:.6;cursor:not-allowed}
.msg{margin-top:12px;color:#b00020;font-weight:800}
</style>
