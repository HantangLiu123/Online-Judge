<template>
  <div class="problem-list">
    <h1>Problem List</h1>

    <!-- 工具条 -->
    <div class="toolbar">
      <div class="filter">
        <label for="difficulty">Difficulty:</label>
        <select
          id="difficulty"
          v-model="difficulty"
          @change="onFilterChange"
        >
          <option value="">All</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>

      <div class="page-size">
        <label for="pageSize">Page size:</label>
        <input
          id="pageSize"
          type="number"
          min="1"
          v-model.number="pageSize"
          @change="onPageSizeChange"
        />
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Title</th>
          <th>Difficulty</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="problem in problems" :key="problem.id">
          <td>{{ problem.title }}</td>
          <td>{{ problem.difficulty }}</td>
          <td>
            <router-link :to="'/problems/' + problem.id">
              View
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <Pagination
        v-model:currentPage="currentPage"
        :total-pages="totalPages"
      />
    </div>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination.vue';
import api from '@/api/request.js';

export default {
  name: 'ProblemList',

  components: {
    Pagination
  },

  data() {
    return {
      problems: [],
      currentPage: 1,
      totalPages: 0,

      pageSize: 10,
      hardness: ''
    };
  },

  mounted() {
    this.fetchProblems();
  },

  watch: {
    currentPage() {
      this.fetchProblems();
    }
  },

  methods: {
    async fetchProblems() {
      const params = new URLSearchParams({
        page: this.currentPage,
        page_size: this.pageSize
      });

      if (this.difficulty) {
        params.append('difficulty', this.difficulty);
      }

      const res = await api.get('/problems/', params);
      const data = res.data;

      this.problems = data.problems;
      this.totalPages = data.total_page;

      // 防止页码越界
      if (this.currentPage > this.totalPages) {
        this.currentPage = this.totalPages || 1;
      }
    },

    onFilterChange() {
      this.currentPage = 1;
      this.fetchProblems();
    },

    onPageSizeChange() {
      if (this.pageSize < 1) {
        this.pageSize = 1;
      }
      this.currentPage = 1;
      this.fetchProblems();
    }
  }
};
</script>

<style scoped>
.problem-list {
  max-width: 900px;
}

/* 工具条：轻量、横向 */
.toolbar {
  margin-bottom: 8px;
  display: flex;
  gap: 16px;
  font-size: 14px;
}

.toolbar label {
  margin-right: 4px;
}

.page-size input {
  width: 60px;
}

/* 表格风格保持原样 */
table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 6px 8px;
  text-align: left;
}

thead th {
  border-bottom: 1px solid #ccc;
}

tbody tr:not(:last-child) td {
  border-bottom: 1px solid #eee;
}

/* 分页 */
.pagination-wrapper {
  margin-top: 12px;
  display: flex;
  justify-content: center;
}
</style>
