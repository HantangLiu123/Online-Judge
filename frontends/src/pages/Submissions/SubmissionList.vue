<template>
  <div class="submission-list">
    <h1>Submission List</h1>

    <!-- 工具条 -->
    <div class="toolbar">
      <p v-if="isAdmin && !canFetch" class="hint">
        Please provide at least User ID or Problem ID to view submissions.
      </p>
      <div class="filter">
        <div v-if="isAdmin && showUserProblemFilters" class="user-filter">
          <label for="userID">User ID:</label>
          <input
            id="userID"
            type="number"
            v-model="userID"
            @change="onFilterChange"
          />
        </div>

        <div v-if="showUserProblemFilters" class="problem-filter">
          <label for="problemID">Problem ID:</label>
          <input
            id="problemID"
            type="text"
            v-model="problemID"
            @change="onFilterChange"
          />
        </div>

        <div class="status-filter">
          <label for="status">Status:</label>
          <select
            id="status"
            v-model="status"
            @change="onFilterChange"
          >
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="success">Success</option>
            <option value="error">Error</option>
          </select>
        </div>

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
          <th>Submission ID</th>
          <th>Submission Time</th>
          <th>Status</th>
          <th>Score</th>
          <th>Counts</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="submission in submissions" :key="submission.id">
          <td>{{ submission.id }}</td>
          <td>{{ formatDateTime(submission.submission_time) }}</td>
          <td>{{ submission.status }}</td>
          <td>{{ submission.score }}</td>
          <td>{{ submission.counts }}</td>
          <td>
            <router-link :to="'/submissions/' + submission.id">
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
import { useUserStore } from '@/store/auth';
import { computed } from 'vue';
import { formatDateTime } from '@/utils/manage-time.js';

export default {
  name: 'SubmissionList',

  components: {
    Pagination
  },

  data() {
    return {
      submissions: [],
      currentPage: 1,
      totalPages: 0,
      pageSize: 10,

      userID: null,
      problemID: null,
      status: ''
    };
  },

  setup() {
    const userStore = useUserStore();
    const isAdmin = computed(() => userStore.user?.role === 'admin');
    return { isAdmin, formatDateTime };
  },

  mounted() {
    this.fetchSubmissions();
  },

  props: {
    fixedUserID: {
      type: Number,
      default: null
    },
    fixedProblemID: {
      type: String,
      default: null
    },
  },

  watch: {
    currentPage() {
      this.fetchSubmissions();
    }
  },

  computed: {
    showUserProblemFilters() {
      return this.fixedUserID === null && this.fixedProblemID === null;
    },

    canFetch() {
      return !this.isAdmin || this.fixedUserID !== null || this.fixedProblemID !== null || this.userID !== null || this.problemID !== null;
    }
  },

  methods: {
    async fetchSubmissions() {
      if (!this.canFetch) {
        alert('Please provide at least User ID or Problem ID to view submissions.');
        this.submissions = [];
        this.totalPages = 0;
        return;
      }

      const params = new URLSearchParams({
        page: this.currentPage,
        page_size: this.pageSize
      });

      if (this.fixedUserID !== null) {
        params.append('user_id', this.fixedUserID);
      } else if (this.isAdmin) {
        if (this.userID) {
          params.append('user_id', this.userID);
        }
      } else {
        // 非管理员只能查看自己的提交
        const userStore = useUserStore();
        params.append('user_id', userStore.user?.user_id);
      }

      if (this.fixedProblemID !== null) {
        params.append('problem_id', this.fixedProblemID);
      } else if (this.problemID) {
        params.append('problem_id', this.problemID);
      }
      if (this.status) {
        params.append('submission_status', this.status);
      }

      const res = await api.get('/submissions/', params);
      const data = res.data;

      this.submissions = data.submissions;
      this.totalPages = data.total_page;

      // 防止页码越界
      if (this.currentPage > this.totalPages) {
        this.currentPage = this.totalPages || 1;
      }
    },

    onFilterChange() {
      this.currentPage = 1;
      this.fetchSubmissions();
    },

    onPageSizeChange() {
      if (this.pageSize < 1) {
        this.pageSize = 1;
      }
      this.currentPage = 1;
      this.fetchSubmissions();
    }
  },

  expose: ['fetchSubmissions']
};
</script>

<style scoped>
.submission-list {
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
