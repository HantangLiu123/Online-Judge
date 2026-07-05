<template>
  <div class="user-list">
    <h1>Manage Users</h1>

    <div class="toolbar">
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
          <th>ID</th>
          <th>Username</th>
          <th>Role</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.role }}</td>
          <td>
            <button v-if="user.role !== 'admin'" @click="changeUserRole(user, 'admin')">Make Admin</button>
            <button v-if="user.role !== 'user'" @click="changeUserRole(user, 'user')">Make User</button>
            <button v-if="user.role !== 'banned'" @click="changeUserRole(user, 'banned')">Ban User</button>
          </td>
          <td>
            <router-link :to="'/users/' + user.id">View Details</router-link>
          </td>
        </tr>
      </tbody>
    </table>

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
  name: 'ManageUsers',

  components: {
    Pagination,
  },

  data() {
    return {
      users: [], // Load user data through API.
      currentPage: 1,
      pageSize: 10,
      totalPages: 0,
    };
  },

  watch: {
    currentPage() {
      this.fetchUsers();
    },
  },

  methods: {
    async changeUserRole(user, role) {
      try {
        // Call API to change role
        const response = await api.put('/users/' + user.id + '/role', { 'role': role });
        const data = response.data;
        alert('User ' + data.user_id + ' role updated to ' + data.role + ' successfully');
        this.fetchUsers(); // Refresh user list
      } catch (error) {
        console.error(error);
        alert('Failed to change role');
      }
    },

    async fetchUsers() {
      try {
        // Fetch users from API with pagination
        const response = await api.get('/users/', {
          page: this.currentPage,
          page_size: this.pageSize
        });
        this.users = response.data.users;
        this.totalPages = response.data.total_page;
      } catch (error) {
        console.error(error);
      }
    }
  },

  mounted() {
    // Load users via API
    this.fetchUsers();
  },

  onPageSizeChange() {
    this.currentPage = 1;
    this.fetchUsers();
  }
};
</script>

<style scoped>
.user-list {
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
