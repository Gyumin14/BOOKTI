<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1>BOOKTI 회원가입</h1>

      <form @submit.prevent="handleSignup">
        <!-- 이름 -->
        <div class="form-group">
          <label for="name">이름</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            placeholder="이름을 입력하세요"
            required
          />
        </div>

        <!-- 생년월일 -->
        <div class="form-group">
          <label for="birth_date">생년월일</label>
          <input
            id="birth_date"
            v-model="form.birth_date"
            type="date"
            required
          />
        </div>

        <!-- 아이디 -->
        <div class="form-group">
          <label for="username">아이디</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder="아이디를 입력하세요"
            required
          />
        </div>

        <!-- 비밀번호 -->
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            required
          />
        </div>

        <!-- 비밀번호 확인 -->
        <div class="form-group">
          <label for="password2">비밀번호 확인</label>
          <input
            id="password2"
            v-model="form.password2"
            type="password"
            placeholder="비밀번호를 다시 입력하세요"
            required
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '가입 중...' : '회원가입' }}
        </button>
      </form>

      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()

const form = ref({
  username: '',
  name: '',
  birth_date: '',
  password: '',
  password2: '',
})

const loading = ref(false)
const message = ref('')
const messageType = ref('')

const handleSignup = async () => {
  message.value = ''
  messageType.value = ''

  if (form.value.password !== form.value.password2) {
    messageType.value = 'error'
    message.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  loading.value = true

  try {
    // ✅ 회원가입 API 호출
    const data = await auth.signup({
      username: form.value.username,
      name: form.value.name,
      birth_date: form.value.birth_date,
      password: form.value.password,
      password2: form.value.password2,
    })

    /**
     * ✅ 핵심
     * Django SignupView 응답:
     * {
     *   message: "회원가입 성공!",
     *   user: { id, username, name, birth_date }
     * }
     */
    if (data?.user) {
      // auth store에 저장 (선택이지만 추천)
      auth.setUser(data.user)

      // 새로고침 대비 localStorage에도 저장
      localStorage.setItem('user', JSON.stringify(data.user))
    }

    messageType.value = 'success'
    message.value = data?.message || '회원가입 성공!'

    // ✅ BOOKTI 설문 페이지로 이동
    router.push('/bookti')
  } catch (e) {
    messageType.value = 'error'
    message.value =
      typeof auth.error === 'string'
        ? auth.error
        : JSON.stringify(auth.error || '회원가입 실패')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell,
    sans-serif;
}

.signup-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message {
  margin-top: 20px;
  padding: 12px;
  border-radius: 5px;
  text-align: center;
  font-weight: 500;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
