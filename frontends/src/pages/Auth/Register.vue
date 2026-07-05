<template>
  <div class="register">
    <h1>Register</h1>
    <form @submit.prevent="register">
      <label for="username">Username:</label>
      <input id="username" v-model="username" type="text">
      <label for="password">Password:</label>
      <input id="password" v-model="password" type="password">
      <button type="submit">Register</button>
    </form>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
export default {
  data() {
    return {
      username: '',
      password: ''
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  methods: {
    async register() {
      try {
        // Call the API for registration
        alert('Registration successful!');
        this.router.push('/auth/login');
      } catch (error) {
        console.error(error);
        alert('Registration failed!');
      }
    }
  }
};
</script>

<style scoped>
/* 页面级容器，占满宽度，用来居中 */
.register {
  min-height: calc(100vh - 56px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 80px;
  background-color: #f5f6f8;
}

/* 真正的卡片 */
.register form {
  width: 360px;
  background: #fff;
  padding: 32px;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* 标题 */
.register h1 {
  position: absolute;
  top: 80px;
  transform: translateX(-50%);
  left: 50%;
  margin-bottom: 0;
  font-size: 26px;
  color: #333;
}

/* 表单布局 */
.register form {
  display: flex;
  flex-direction: column;
}

/* label */
.register label {
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}

/* 输入框 */
.register input {
  height: 38px;
  padding: 0 10px;
  margin-bottom: 18px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.register input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.15);
}

/* 按钮 */
.register button {
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

.register button:hover {
  background-color: #337ecc;
}

.register button:active {
  transform: scale(0.98);
}
</style>