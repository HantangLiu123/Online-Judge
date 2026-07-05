<template>
  <div class="user-detail-page">
    <div class="user-card">
      <h1>User Profile</h1>

      <div class="info-list">
        <div class="info-item">
          <span class="label">User ID</span>
          <span class="value">{{ user.user_id }}</span>
        </div>

        <div class="info-item">
          <span class="label">Username</span>
          <span class="value">{{ user.username }}</span>
        </div>

        <div class="info-item">
          <span class="label">Role</span>
          <span class="value role" :class="user.role">
            {{ user.role }}
          </span>
        </div>

        <div class="info-item">
          <span class="label">Join Time</span>
          <span class="value">{{ user.join_time }}</span>
        </div>

        <div class="info-item">
          <span class="label">Submissions</span>
          <span class="value">{{ user.submit_count }}</span>
        </div>

        <div class="info-item">
          <span class="label">Solved</span>
          <span class="value">{{ user.resolve_count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/api/request.js';

export default {
  name: 'UserDetail',
  setup() {
    const route = useRoute();
    const user = ref({
      user_id: '',
      username: '',
      join_time: '',
      role: '',
      submit_count: 0,
      resolve_count: 0,
    });

    onMounted(() => {
      try {
        const userId = route.params.id;
        api.get(`/users/${userId}`).then((res) => {
          user.value = res.data;
        });
      } catch (error) {
        console.error(error);
      }
    });

    return { user };
  },
};
</script>

<style scoped>
/* 页面容器 */
.user-detail-page {
  min-height: calc(100vh - 56px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 80px;
  background-color: #f5f6f8;
}

/* 主卡片 */
.user-card {
  width: 420px;
  background: #fff;
  padding: 32px;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* 标题 */
.user-card h1 {
  text-align: center;
  margin-bottom: 28px;
  font-size: 24px;
  color: #333;
}

/* 信息列表 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 单条信息 */
.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 15px;
}

/* 左侧 label */
.label {
  color: #666;
}

/* 右侧 value */
.value {
  color: #333;
  font-weight: 500;
}

/* 角色样式 */
.value.role {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 13px;
  text-transform: capitalize;
}

.value.role.user {
  background-color: rgba(64, 158, 255, 0.12);
  color: #409eff;
}

.value.role.admin {
  background-color: rgba(245, 108, 108, 0.12);
  color: #f56c6c;
}
</style>
