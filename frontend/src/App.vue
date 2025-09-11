<script setup>
import { ref } from 'vue';
import PatientManager from './components/PatientManager.vue';
import Login from './components/Login.vue';

// 跟踪登录状态
const isLoggedIn = ref(false);

// 登录成功时调用
const onLoginSuccess = () => {
  isLoggedIn.value = true;
};

// 新增：处理登出逻辑
const handleLogout = () => {
  isLoggedIn.value = false;
  // 未来如果使用 token，可以在这里清除 token
};
</script>

<template>
  <!-- 新增：统一的页眉 -->
  <header class="app-header">
    <h1>医院病历管理系统</h1>
    <!-- 仅在登录后显示登出按钮 -->
    <button v-if="isLoggedIn" @click="handleLogout" class="logout-button">
      登出
    </button>
  </header>

  <main>
    <!-- 条件渲染逻辑保持不变 -->
    <Login v-if="!isLoggedIn" @login-success="onLoginSuccess" />
    <PatientManager v-else />
  </main>
</template>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5%; /* 左右留白 */
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  width: 100%;
  position: fixed; /* 固定在顶部 */
  top: 0;
  left: 0;
  z-index: 1001; /* 确保在最上层 */
  box-sizing: border-box; /* 让 padding 不会撑大宽度 */
}

.app-header h1 {
  font-size: 1.5em; /* 调整标题大小 */
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

/* main 区域需要增加上边距，避免被 header 遮挡 */
main {
  padding-top: 100px;
  text-align: center;
}
</style>