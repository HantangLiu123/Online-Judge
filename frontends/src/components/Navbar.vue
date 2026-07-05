<template>
  <nav class="navbar">
    <ul>
      <li><router-link to="/auth/login">Login</router-link></li>
      <li><router-link to="/auth/register">Register</router-link></li>
      <li><router-link to="/problems">Problems</router-link></li>
      <li v-if="userStore.isLoggedIn"><router-link to="/submissions">Submissions</router-link></li>
      <li v-if="isAdmin"><router-link to="/admin/manage-users">Manage Users</router-link></li>
    </ul>
    <button class="logout-button" v-if="userStore.isLoggedIn" @click="userStore.logout()">Logout</button>
  </nav>
</template>

<script>
import { computed } from 'vue';
import { useUserStore} from '../store/auth';

export default {
  setup() {
    const userStore = useUserStore();
    const isAdmin = computed(() => userStore.user?.role === 'admin');
    return { userStore, isAdmin };
  },
};
</script>

<style>
.navbar {
  height: 56px;
  background-color: #2f2f2f;
  padding: 0 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

/* 左侧导航列表 */
.navbar ul {
  list-style: none;
  display: flex;
  gap: 20px;
  margin: 0;
  padding: 0;
}

/* 普通链接 */
.navbar a {
  color: #ddd;
  text-decoration: none;
  font-size: 15px;
  padding: 6px 2px;
  position: relative;
  transition: color 0.2s;
}

/* hover */
.navbar a:hover {
  color: #fff;
}

/* 当前路由高亮（Vue Router 自动加的类） */
.navbar a.router-link-active {
  color: #409eff;
}

/* 底部高亮线（可选但好看） */
.navbar a.router-link-active::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 100%;
  height: 2px;
  background-color: #409eff;
}

/* 右侧退出按钮 */
.logout-button {
  margin-left: auto;
  background-color: transparent;
  color: #ddd;
  border: 1px solid #555;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

/* hover */
.logout-button:hover {
  background-color: #409eff;
  border-color: #409eff;
  color: #fff;
}
</style>