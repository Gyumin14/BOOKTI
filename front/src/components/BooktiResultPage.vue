<template>
  <div class="wrap">
    <div class="card">
      <h1>📚 당신의 BOOKTI 결과</h1>

      <div v-if="bookti">
        <div class="code">{{ bookti }}</div>
        <div class="alias">{{ result.alias }}</div>
        <p class="summary">{{ result.summary }}</p>
        <p class="detail">{{ result.detail }}</p>

        <div class="tags">
          <span v-for="tag in result.keywords" :key="tag">#{{ tag }}</span>
        </div>

        <button class="btn" @click="goRecommend">
          추천 도서 보러 가기 →
        </button>
      </div>

      <div v-else>
        <p>결과 정보가 없습니다.</p>
        <button class="btn" @click="$router.push('/bookti')">
          설문 다시 하기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const bookti = localStorage.getItem('bookti')

// 👉 최소 결과 매핑 (나중에 JSON으로 분리 추천)
const BOOKTI_MAP = {
  PFLR: {
    alias: '현실형 라이트 리더',
    summary: '필요한 정보만 빠르게 챙기는 실속파 독서러',
    detail: '실용적인 정보를 빠르게 얻기 위해 익숙한 분야의 가벼운 책을 읽는 타입입니다.',
    keywords: ['실용서', '핵심', '업무', '입문'],
  },
  EFLR: {
    alias: '힐링 리더',
    summary: '편안한 감성으로 마음을 쉬게 하는 독서가',
    detail: '위로와 공감을 위해 부담 없는 감성 도서를 즐겨 읽는 타입입니다.',
    keywords: ['힐링', '에세이', '위로', '감성'],
  },
  // 👉 나머지 유형은 이후 확장
}

const result = computed(() => {
  return BOOKTI_MAP[bookti] || {
    alias: 'BOOKTI 독서가',
    summary: '당신만의 독서 성향을 발견했어요',
    detail: '이 성향에 맞는 도서를 추천해드릴게요.',
    keywords: [],
  }
})

function goRecommend() {
  const code = localStorage.getItem('bookti')
  if (!code) {
    router.push('/bookti')
    return
  }

  // (선택) bookti를 쿼리로 넘기면 공유 링크도 가능
  router.push(`/bookti/recommend?bookti=${encodeURIComponent(code)}`)
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
  padding: 32px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.code {
  font-size: 36px;
  font-weight: 900;
  margin: 12px 0;
}
.alias {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 8px;
}
.summary {
  font-weight: 600;
}
.detail {
  margin-top: 8px;
  color: #555;
}
.tags {
  margin: 16px 0;
}
.tags span {
  margin-right: 6px;
  color: #4a6cf7;
}
.btn {
  width: 100%;
  padding: 12px;
  border: 0;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
}
</style>
