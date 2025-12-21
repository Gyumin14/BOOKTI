<template>
  <div class="wrap">
    <div class="card">
      <h1>BOOKTI 설문 (12문항)</h1>
      <p class="sub">A/B 중 하나를 선택하면 됩니다.</p>

      <div v-for="q in questions" :key="q.id" class="qbox">
        <div class="qtitle">{{ q.id }}. {{ q.text }}</div>

        <label class="choice">
          <input
            type="radio"
            :name="'q-' + q.id"
            value="A"
            v-model="answers[q.id]"
          />
          <span>A. {{ q.choices.A.label }}</span>
        </label>

        <label class="choice">
          <input
            type="radio"
            :name="'q-' + q.id"
            value="B"
            v-model="answers[q.id]"
          />
          <span>B. {{ q.choices.B.label }}</span>
        </label>
      </div>

      <button class="btn" :disabled="!isAllAnswered" @click="submit">
        결과 보기
      </button>

      <div v-if="result" class="result">
        <div class="code">당신의 BOOKTI: <b>{{ result }}</b></div>
        <div class="hint">※ 다음 단계: 이 결과를 서버에 저장하고 추천 도서를 불러오면 됩니다.</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()

// ✅ 너가 정한 4축: 목적(P/E), 범위(F/C), 깊이(L/D), 표현(R/A)
const questions = [
  // purpose (P/E)
  { id: 1, axis: 'purpose', text: '책을 고를 때 가장 큰 이유는?', choices: { A: { label: '당장 도움이 될 정보나 해결책', score: 'P' }, B: { label: '감정적인 공감이나 분위기, 위로', score: 'E' } } },
  { id: 2, axis: 'purpose', text: '책을 다 읽고 남는 만족감은?', choices: { A: { label: '"쓸모 있는 걸 배웠다"', score: 'P' }, B: { label: '"기분이나 생각이 달라졌다"', score: 'E' } } },
  { id: 3, axis: 'purpose', text: '독서 후 가장 먼저 떠오르는 생각은?', choices: { A: { label: '이 내용을 어디에 써먹을 수 있을까', score: 'P' }, B: { label: '이 감정이나 장면이 오래 남는다', score: 'E' } }, tiebreaker: true },

  // range (F/C)
  { id: 4, axis: 'range', text: '독서 취향에 더 가까운 쪽은?', choices: { A: { label: '익숙한 분야, 이미 관심 있는 주제', score: 'F' }, B: { label: '잘 몰랐던 분야도 호기심 생기면 도전', score: 'C' } } },
  { id: 5, axis: 'range', text: '서점/앱에서 책을 고를 때 행동은?', choices: { A: { label: '늘 보던 코너부터 본다', score: 'F' }, B: { label: '신간/추천/트렌드부터 훑는다', score: 'C' } } },
  { id: 6, axis: 'range', text: '한 달 독서 목록을 보면?', choices: { A: { label: '비슷한 주제나 장르가 반복됨', score: 'F' }, B: { label: '장르가 꽤 다양하게 섞여 있음', score: 'C' } }, tiebreaker: true },

  // depth (L/D)
  { id: 7, axis: 'depth', text: '책 분량에 대한 생각은?', choices: { A: { label: '가볍고 빨리 읽히는 게 좋다', score: 'L' }, B: { label: '두꺼워도 내용이 깊으면 괜찮다', score: 'D' } } },
  { id: 8, axis: 'depth', text: '책을 읽는 속도는?', choices: { A: { label: '핵심 위주로 빠르게', score: 'L' }, B: { label: '곱씹으며 천천히', score: 'D' } } },
  { id: 9, axis: 'depth', text: '책을 덮은 후 행동은?', choices: { A: { label: '인상 깊은 부분만 기억하고 넘어간다', score: 'L' }, B: { label: '내용 전체를 정리하거나 오래 생각한다', score: 'D' } }, tiebreaker: true },

  // expression (R/A)
  { id: 10, axis: 'expression', text: '독서 후 기록 습관은?', choices: { A: { label: '따로 남기지 않는다', score: 'R' }, B: { label: '짧게라도 리뷰/메모를 남긴다', score: 'A' } } },
  { id: 11, axis: 'expression', text: '마음에 든 책이 있을 때?', choices: { A: { label: '혼자 만족하고 끝낸다', score: 'R' }, B: { label: '다른 사람에게 추천하고 싶다', score: 'A' } } },
  { id: 12, axis: 'expression', text: '독서 기록을 남긴다면 더 가까운 건?', choices: { A: { label: '개인 메모용, 나만 보기', score: 'R' }, B: { label: '공개 리뷰, 정리 글, 추천 목록', score: 'A' } }, tiebreaker: true },
]

// answers[qid] = 'A' | 'B'
const answers = reactive({})
const result = ref('')

const isAllAnswered = computed(() => {
  return questions.every(q => answers[q.id] === 'A' || answers[q.id] === 'B')
})

// 동점 시 타이브레이커 문항: purpose=3, range=6, depth=9, expression=12
const tiebreak = {
  purpose: 3,
  range: 6,
  depth: 9,
  expression: 12,
}

function calcBookti() {
  const scores = { P: 0, E: 0, F: 0, C: 0, L: 0, D: 0, R: 0, A: 0 }

  for (const q of questions) {
    const picked = answers[q.id]
    const letter = q.choices[picked].score
    scores[letter] += 1
  }

  const pickAxis = (left, right, axisKey) => {
    if (scores[left] > scores[right]) return left
    if (scores[right] > scores[left]) return right

    // tie → tiebreaker question
    const qid = tiebreak[axisKey]
    const tq = questions.find(x => x.id === qid)
    const picked = answers[qid]
    return tq.choices[picked].score // left or right letter
  }

  const p = pickAxis('P', 'E', 'purpose')
  const r = pickAxis('F', 'C', 'range')
  const d = pickAxis('L', 'D', 'depth')
  const e = pickAxis('R', 'A', 'expression')

  return `${p}${r}${d}${e}`
}

async function submit() {
  const code = calcBookti()

  // 결과 저장 (결과 페이지에서 쓰기)
  localStorage.setItem('bookti', code)

  // ✅ 백엔드에 저장
  // 로그인/토큰이 없어서 MVP로 user_id를 같이 전송
  if (auth.user?.id) {
    await axios.post('/api/bookti/submit/', {
      user_id: auth.user.id,
      bookti_code: code,
    })
  }

  // ✅ 결과 페이지로 이동
  router.push('/bookti/result')
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
  max-width: 760px;
  background: white;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}
h1 { margin: 0 0 6px; }
.sub { margin: 0 0 18px; color: #666; }
.qbox {
  padding: 14px 12px;
  border: 1px solid #eee;
  border-radius: 10px;
  margin-bottom: 12px;
}
.qtitle { font-weight: 700; margin-bottom: 8px; }
.choice {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 6px 0;
  cursor: pointer;
}
.btn {
  width: 100%;
  padding: 12px;
  border: 0;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.result {
  margin-top: 18px;
  padding: 14px;
  border-radius: 10px;
  background: #f0f7ff;
  border: 1px solid #d8ecff;
}
.code { font-size: 18px; }
.hint { margin-top: 6px; color: #555; font-size: 13px; }
</style>
