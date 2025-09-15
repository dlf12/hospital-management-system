<script setup>
import { ref, onMounted } from 'vue';
import PatientManager from './components/PatientManager.vue';
import Login from './components/Login.vue';
import apiClient from './api/apiClient'; // 导入 apiClient

// 跟踪登录状态
const isLoggedIn = ref(false);

// 登录成功时调用
const onLoginSuccess = (token) => {
  // 1. 将 token 存入 localStorage
  localStorage.setItem('accessToken', token);
  // 2. 更新登录状态
  isLoggedIn.value = true;
};

// 处理登出逻辑
const handleLogout = () => {
  // 1. 从 localStorage 中移除 token
  localStorage.removeItem('accessToken');
  // 2. 更新登录状态
  isLoggedIn.value = false;
};

// Vue 生命周期钩子，在组件挂载到 DOM 后执行
onMounted(() => {
  // 检查 localStorage 中是否存在 token，如果存在则认为用户已登录
  const token = localStorage.getItem('accessToken');
  if (token) {
    isLoggedIn.value = true;
  }
});
</script>

<template>
  <header class="app-header">
    <h1>医院病历管理系统</h1>
    <button v-if="isLoggedIn" @click="handleLogout" class="logout-button">
      登出
    </button>
  </header>

  <main>
    <Login v-if="!isLoggedIn" @login-success="onLoginSuccess" />
    <PatientManager v-else />
  </main>
</template>

<style scoped>
/* 样式保持不变 */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5%;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1001;
  box-sizing: border-box;
}

.app-header h1 {
  font-size: 1.5em;
  color: #2c3e50;
  margin: 0;
  padding: 20px 0;
}

.logout-button {
  background-color: transparent;
  color: #3498db;
  border: 1px solid #3498db;
  padding: 0.5em 1.2em;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-button:hover {
  background-color: #3498db;
  color: white;
}

main {
  padding-top: 100px;
  text-align: center;
}
</style>