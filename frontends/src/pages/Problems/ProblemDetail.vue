<template>
  <div class="problem-detail">

    <!-- Problem Card -->
    <div class="card">
      <h1 class="title">
        {{ problem.title }}
        <span class="difficulty">{{ problem.difficulty }}</span>
      </h1>

      <div class="meta">
        <span v-if="problem.author">Author: {{ problem.author }}</span>
        <span v-if="problem.time_limit">Time: {{ problem.time_limit }}s</span>
        <span v-if="problem.memory_limit">Memory: {{ problem.memory_limit }}MB</span>
      </div>

      <section>
        <h3>Description</h3>
        <p>{{ problem.description }}</p>
      </section>

      <section>
        <h3>Input</h3>
        <p>{{ problem.input_description }}</p>
      </section>

      <section>
        <h3>Output</h3>
        <p>{{ problem.output_description }}</p>
      </section>

      <section v-if="problem.samples?.length">
        <h3>Samples</h3>

        <div
          v-for="(sample, idx) in problem.samples"
          :key="idx"
          class="sample"
        >
          <div class="io-block">
            <div class="io-label">Input</div>
            <pre>{{ sample.input }}</pre>
          </div>

          <div class="io-block">
            <div class="io-label">Output</div>
            <pre>{{ sample.output }}</pre>
          </div>
        </div>
      </section>

      <section>
        <h3>Constraints</h3>
        <p>{{ problem.constraints }}</p>
      </section>

      <section v-if="problem.hint">
        <h3>Hint</h3>
        <p>{{ problem.hint }}</p>
      </section>

      <!-- Admin only -->
      <section v-if="isAdmin">
        <h3>Testcases</h3>

        <div
          v-for="(testcase, idx) in problem.testcases"
          :key="idx"
          class="sample"
        >
          <div class="io-block">
            <div class="io-label">Input</div>
            <pre>{{ testcase.input }}</pre>
          </div>

          <div class="io-block">
            <div class="io-label">Output</div>
            <pre>{{ testcase.output }}</pre>
          </div>
        </div>
      </section>

    </div>

    <!-- Submission List -->
    <div class="card">
      <h2>My Submissions</h2>
      <SubmissionList
      ref="submissionListRef"
      :fixed-problem-i-d="problemId"
      :fixed-user-i-d="userStore.user?.user_id"/>
    </div>

    <!-- Submit Code -->
    <div class="card">
      <h2>Submit Solution</h2>

      <div class="submit-toolbar">
        <select v-model="language">
          <option disabled value="">Select Language</option>
          <option
            v-for="lang in languages"
            :key="lang"
            :value="lang"
          >
            {{ lang }}
          </option>
        </select>

        <button @click="submitCode" :disabled="!canSubmit">
          Submit
        </button>
      </div>

      <div class="code-editor">
        <textarea
          v-model="code"
          placeholder="Write your code here..."
        ></textarea>

        <!-- 高亮预览 -->
        <pre class="highlight">
          <code v-html="highlightedCode"></code>
        </pre>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue';
import { useRoute } from 'vue-router';
import SubmissionList from '../Submissions/SubmissionList.vue';
import { useUserStore } from '@/store/auth';
import api from '@/api/request.js';

const highlight = inject('highlight');

// route
const route = useRoute();
const problemId = route.params.id;

// state
const problem = ref({});
const languages = ref([]);
const language = ref('');
const code = ref('');
const submissionListRef = ref(null);

// TODO: 从你的 auth / store 中拿
const userStore = useUserStore();
const isAdmin = computed(() => userStore.user?.role === 'admin');

// computed
const highlightedCode = computed(() =>
  highlight(code.value, language.value)
);

const canSubmit = computed(() =>
  language.value && code.value.trim().length > 0
);

// lifecycle
onMounted(async () => {
  // TODO: 获取 problem
  const res = await api.get(`/problems/${problemId}`);
  problem.value = res.data;

  // TODO: 获取语言列表
  const langRes = await api.get('/languages/');
  languages.value = langRes.data.name;
});

// submit
async function submitCode() {
  try {
    // TODO: 提交代码
    await api.post('/submissions/', {
      problem_id: problemId,
      language: language.value,
      code: code.value,
    });

    alert('Submitted!');
    code.value = '';

    submissionListRef.value.fetchSubmissions();
  } catch (err) {
    console.error(err);
  }
}
</script>

<style scoped>
.problem-detail {
  max-width: 900px;
  margin: 0 auto;
}

.card {
  background: #fff;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.difficulty {
  font-size: 0.9em;
  padding: 2px 8px;
  border-radius: 4px;
  background: #eee;
}

.meta {
  display: flex;
  gap: 15px;
  color: #666;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.sample {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.io-block {
  flex: 1;
}

.io-label {
  font-size: 0.85em;
  font-weight: 600;
  color: #666;
  margin-bottom: 4px;
}

.io-block pre {
  background: #f6f8fa;
  padding: 8px;
  border-radius: 4px;
  white-space: pre-wrap;
}

.testcase {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.submit-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.code-editor {
  display: flex;
  gap: 10px;
}

textarea {
  width: 50%;
  height: 200px;
  font-family: monospace;
}

.highlight {
  width: 50%;
  background: #f6f8fa;
  padding: 10px;
  overflow: auto;
}

/* 高亮样式 */
:deep(.kw) {
  color: #409eff;
}

:deep(.str) {
  color: #d79d46;
}

:deep(.num) {
  color: #acef8b;
}
</style>
