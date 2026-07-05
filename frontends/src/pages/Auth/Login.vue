<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Login</h1>

      <form @submit.prevent="login">
        <div class="form-item">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter your username"
          />
        </div>

        <div class="form-item">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
          />
        </div>

        <button type="submit">Login</button>
      </form>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
import { useUserStore } from '../../store/auth';
import api from '@/api/request.js';
export default {
  data() {
    return {
      username: '',
      password: '',
    };
  },
  setup() {
    const router = useRouter();
    const userStore = useUserStore();
    return { router, userStore };
  },
  methods: {
    async login() {
      try {
        // Perform login API request here
        const response = await api.post('/auth/login', {
          username: this.username,
          password: this.password,
        });
        const userData = response.data;
        this.userStore.loginSuccess(userData); // Save user data to store
        alert('Login successful!');
        this.router.push('/problems'); // Redirect to problems page after success
      } catch (error) {
        console.error(error);
        alert('Login failed');
      }
    },
  },
};
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 56px); /* 如果你有 navbar */
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 80px;
  background-color: #f5f6f8;
}

/* 登录卡片 */
.login-card {
  width: 360px;
  background: #fff;
  padding: 32px;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* 标题 */
.login-card h1 {
  text-align: center;
  margin-bottom: 24px;
  font-size: 26px;
  color: #333;
}

/* 表单项 */
.form-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 18px;
}

.form-item label {
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}

/* 输入框 */
.form-item input {
  height: 38px;
  padding: 0 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-item input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.15);
}

/* 登录按钮 */
button {
  width: 100%;
  height: 40px;
  margin-top: 8px;
  background-color: #409eff;
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
}

button:hover {
  background-color: #337ecc;
}

button:active {
  transform: scale(0.98);
}
</style>