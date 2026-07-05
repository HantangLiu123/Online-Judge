<template>
  <div class="submission-detail-page">
    <div class="submission-card">
      <h1>Submission Detail</h1>

      <!-- 基本信息 -->
      <div class="info-list">
        <div class="info-item">
          <span class="label">Status</span>
          <span class="value status" :class="submission.status">
            {{ submission.status }}
          </span>
        </div>

        <div class="info-item">
          <span class="label">Score</span>
          <span class="value">{{ submission.score }}</span>
        </div>

        <div class="info-item">
          <span class="label">Counts</span>
          <span class="value">{{ submission.counts }}</span>
        </div>

        <div class="info-item">
          <span class="label">Language</span>
          <span class="value">{{ submission.language }}</span>
        </div>
      </div>

      <!-- 代码 -->
      <div class="code-block">
        <div class="code-header">Source Code</div>
        <pre><code v-html="highlightedCode"></code></pre>
      </div>

      <!-- 测试详情按钮 -->
      <button
        v-if="submission.status === 'success'"
        class="detail-button"
        @click="fetchTests"
      >
        {{ showTests ? 'Hide Test Details' : 'View Test Details' }}
      </button>

      <!-- 测试详情 -->
      <div v-if="showTests" class="test-list">
        <h2>Test Details</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Result</th>
              <th>Time (s)</th>
              <th>Memory (MB)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="test in tests" :key="test.test_id">
              <td>{{ test.test_id }}</td>
              <td :class="['test-result', test.result]">
                {{ test.result }}
              </td>
              <td>{{ test.time }}</td>
              <td>{{ test.memory }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/api/request';

export default {
  name: 'SubmissionDetail',
  setup() {
    const route = useRoute();
    const submissionId = route.params.id;

    const submission = ref({
      status: '',
      score: 0,
      counts: 0,
      language: '',
      code: '',
    });

    const tests = ref([]);
    const showTests = ref(false);

    onMounted(async () => {
      // TODO: 获取 submission 基本信息
      const res = await api.get(`/submissions/${submissionId}`);
      submission.value = res.data;
    });

    const fetchTests = async () => {
      if (showTests.value) {
        showTests.value = false;
        return;
      }

      // TODO: 请求测试详情
      const res = await api.get(`/submissions/${submissionId}/log`);
      tests.value = res.data.details;
      showTests.value = true;
    };

    const highlight = inject('highlight');

    /**
     * 简单代码高亮（不引库）
     * 适合 OJ 场景，够用、可控
     */
    const highlightedCode = computed(() => {
      return highlight(submission.value.code, submission.value.language);
    });

    return {
      submission,
      tests,
      showTests,
      highlightedCode,
      fetchTests,
    };
  },
};
</script>

<style scoped>
/* 页面布局 */
.submission-detail-page {
  min-height: calc(100vh - 56px);
  display: flex;
  justify-content: center;
  padding-top: 80px;
  background-color: #f5f6f8;
}

/* 卡片 */
.submission-card {
  width: 900px;
  background: #fff;
  padding: 32px;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* 标题 */
h1 {
  text-align: center;
  margin-bottom: 28px;
}

/* 基本信息 */
.info-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px 32px;
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  justify-content: space-between;
}

.label {
  color: #666;
}

.value {
  font-weight: 500;
}

.value.status.success {
  color: #67c23a;
}
.value.status.pending {
  color: #e6a23c;
}
.value.status.error {
  color: #f56c6c;
}

/* 代码块 */
.code-block {
  margin-top: 16px;
}

.code-header {
  font-size: 14px;
  margin-bottom: 6px;
  color: #555;
}

pre {
  background: #2d2d2d;
  color: #eaeaea;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 14px;
}

:deep(.kw) {
  color: #409eff;
}

:deep(.str) {
  color: #d79d46;
}

:deep(.num) {
  color: #acef8b;
}

/* 按钮 */
.detail-button {
  margin-top: 20px;
  padding: 8px 16px;
  background-color: #409eff;
  border: none;
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
}

.detail-button:hover {
  background-color: #337ecc;
}

/* 测试详情 */
.test-list {
  margin-top: 24px;
}

.test-list h2 {
  margin-bottom: 12px;
  font-size: 18px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.test-result.success {
  color: #67c23a;
}
.test-result.error {
  color: #f56c6c;
}
</style>
