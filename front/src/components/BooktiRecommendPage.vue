<template>
  <div class="wrap">
    <div class="card">
      <div class="top">
        <h1>📚 BOOKTI 추천 도서</h1>
        <div class="meta" v-if="bookti">내 BOOKTI: <b>{{ bookti }}</b></div>
      </div>

      <div class="toolbar">
        <button class="btn" @click="reload" :disabled="loading">
          다시 추천 받기
        </button>
        <button class="btn ghost" @click="$router.push('/bookti')">
          설문 다시하기
        </button>
      </div>

      <div v-if="!bookti" class="empty">
        <p>BOOKTI 결과가 없습니다. 설문부터 진행해주세요.</p>
        <button class="btn" @click="$router.push('/bookti')">설문 하러 가기</button>
      </div>

      <div v-else>
        <div v-if="loading" class="status">추천 도서를 불러오는 중...</div>
        <div v-else-if="error" class="status error">{{ error }}</div>

        <div v-else class="grid">
          <a
            v-for="b in books"
            :key="b.isbn13 || b.link"
            class="book"
            :href="b.link"
            target="_blank"
            rel="noopener"
          >
            <img class="cover" :src="b.cover" alt="" />
            <div class="info">
              <div class="title">{{ b.title }}</div>
              <div class="author">{{ b.author }}</div>
              <div class="cat">{{ b.categoryName }}</div>
              <div class="desc" v-if="b.description">{{ b.description }}</div>
            </div>
          </a>
        </div>

        <div v-if="!loading && !error && books.length === 0" class="status">
          추천 결과가 비어있습니다. 다시 추천받기를 눌러주세요.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'

/**
 * ✅ bookti 가져오는 우선순위
 * 1) URL 쿼리 (?bookti=PFLR)   ← 나중에 공유 링크에 유리
 * 2) localStorage bookti       ← 현재 흐름에서 기본
 */
const params = new URLSearchParams(window.location.search)
const bookti = params.get('bookti') || localStorage.getItem('bookti') || ''

const books = ref([])
const loading = ref(false)
const error = ref('')

async function fetchRecommendations() {
  if (!bookti) return
  loading.value = true
  error.value = ''

  try {
    const res = await axios.get('/api/bookti/recommendations/', {
      params: { bookti },
    })
    books.value = res.data.items || []
  } catch (e) {
    error.value = '추천 도서를 불러오지 못했습니다. (백엔드/알라딘 API 확인)'
    books.value = []
  } finally {
    loading.value = false
  }
}

function reload() {
  fetchRecommendations()
}

onMounted(() => {
  fetchRecommendations()
})
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
  max-width: 900px;
  background: white;
  border-radius: 14px;
  padding: 28px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}
.top { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.meta { color: #555; }
.toolbar { display:flex; gap:10px; margin: 14px 0 18px; }
.btn {
  padding: 10px 12px;
  border: 0;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
}
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn.ghost { background: #eef0f6; }
.status { padding: 14px; border: 1px solid #eee; border-radius: 10px; background: #fafafa; }
.status.error { border-color: #ffd2d2; background: #fff4f4; color: #b00020; }
.empty { padding: 16px; border: 1px dashed #ddd; border-radius: 10px; }

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 740px) {
  .grid { grid-template-columns: 1fr; }
}
.book {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  transition: transform .05s ease-in-out;
}
.book:hover { transform: translateY(-1px); }
.cover {
  width: 80px;
  height: auto;
  border-radius: 8px;
  flex-shrink: 0;
}
.title { font-weight: 900; margin-bottom: 4px; }
.author, .cat { color: #666; font-size: 13px; }
.desc { margin-top: 8px; color: #444; font-size: 13px; line-height: 1.35; }
</style>
