<template>
  <div class="wrap">
    <div class="card">
      <div class="top">
        <h1>🙋 내 프로필</h1>
        <button class="btn ghost" @click="goHome">메인</button>
      </div>

      <div v-if="!user" class="empty">
        <p>로그인 정보가 없습니다.</p>
        <button class="btn" @click="goLogin">로그인</button>
      </div>

      <div v-else>
        <div class="row">
          <div class="label">아이디</div>
          <div class="value">{{ user.username }}</div>
        </div>
        <div class="row">
          <div class="label">이름</div>
          <div class="value">{{ user.name }}</div>
        </div>
        <div class="row">
          <div class="label">생년월일</div>
          <div class="value">{{ user.birth_date }}</div>
        </div>

        <hr class="hr" />

        <div class="row">
          <div class="label">BOOKTI</div>
          <div class="value">
            <span v-if="bookti" class="pill">{{ bookti }}</span>
            <span v-else class="muted">아직 설문을 하지 않았어요</span>
          </div>
        </div>

        <div class="actions">
          <button class="btn" @click="goBookti">
            {{ bookti ? 'BOOKTI 다시하기' : 'BOOKTI 설문 하러가기' }}
          </button>

          <button class="btn" :disabled="!bookti" @click="goRecommend">
            추천 도서 보러가기 →
          </button>

          <button class="btn danger" @click="logout">
            로그아웃
          </button>
        </div>

        <p class="hint">
          * BOOKTI는 서버에 저장된 값(bookti_code)을 우선 표시하고,
          없으면 localStorage 값을 임시로 보여줍니다.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()

const user = computed(() => auth.user)

// ✅ 1순위: 서버에서 내려온 bookti_code (auth.user.bookti_code)
// ✅ 2순위: 로컬에 저장된 bookti (임시/백업)
const bookti = computed(() => {
  return auth.user?.bookti_code || localStorage.getItem('bookti') || ''
})

function goHome() {
  router.push('/')
}
function goLogin() {
  router.push('/login')
}
function goBookti() {
  router.push('/bookti')
}
function goRecommend() {
  if (!bookti.value) return
  router.push(`/bookti/recommend?bookti=${encodeURIComponent(bookti.value)}`)
}
function logout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.wrap {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 40px 16px;
  background: #f6f7fb;
}
.card {
  width: 100%;
  max-width: 520px;
  background: white;
  border-radius: 14px;
  padding: 28px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}
.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
}
.label { color: #666; font-weight: 800; }
.value { font-weight: 900; }
.hr { margin: 16px 0; border: 0; border-top: 1px solid #eee; }
.pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #eef0ff;
  font-weight: 900;
}
.muted { color: #888; font-weight: 800; }
.actions {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}
.btn {
  padding: 12px;
  border: 0;
  border-radius: 10px;
  font-weight: 900;
  cursor: pointer;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn.ghost { background: #eef0f6; }
.btn.danger { background: #ffecec; color: #b00020; }
.empty { padding: 16px; border: 1px dashed #ddd; border-radius: 10px; }
.hint { margin-top: 10px; font-size: 12px; color: #666; }
</style>
