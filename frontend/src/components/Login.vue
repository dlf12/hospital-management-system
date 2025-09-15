<script setup>
import { ref } from 'vue';
import apiClient from '../api/apiClient';

const emit = defineEmits(['login-success']);

// --- 响应式变量 ---
const username = ref('');
const password = ref('');
const errorMessage = ref('');
const successMessage = ref(''); // 新增：用于显示注册成功等成功信息

// 新增：一个状态，用于切换登录/注册模式
const isRegisterMode = ref(false);

// --- 模式切换函数 ---
const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value;
  // 切换模式时清空所有消息和输入
  username.value = '';
  password.value = '';
  errorMessage.value = '';
  successMessage.value = '';
};

// --- 逻辑处理函数 ---

// 处理登录
const handleLogin = async () => {
  try {
    const response = await apiClient.post('/login', {
      username: username.value,
      password: password.value,
    });
    emit('login-success', response.data.access_token);
  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || '登录失败，请重试！';
    } else {
      errorMessage.value = '无法连接到服务器。';
    }
  }
};

// 新增：处理注册
const handleRegister = async () => {
  try {
    const response = await apiClient.post('/register', {
      username: username.value,
      password: password.value,
    });
    // 注册成功
    successMessage.value = `${response.data.message}，请登录。`;
    // 自动切换回登录模式
    isRegisterMode.value = false;
    errorMessage.value = '';
    // 清空密码框，保留用户名方便用户直接登录
    password.value = '';
  } catch (error) {
    if (error.response) {
      // 例如，用户名已存在
      errorMessage.value = error.response.data.message || '注册失败，请重试！';
    } else {
      errorMessage.value = '无法连接到服务器。';
    }
  }
};

// 统一的表单提交入口
const handleSubmit = () => {
  // 提交前清空消息
  errorMessage.value = '';
  successMessage.value = '';

  if (!username.value || !password.value) {
    errorMessage.value = '用户名和密码不能为空！';
    return;
  }

  // 根据当前模式调用不同的函数
  if (isRegisterMode.value) {
    handleRegister();
  } else {
    handleLogin();
  }
};
</script>

<template>
  <div class="login-container">
    <!-- 标题根据模式动态变化 -->
    <h2>{{ isRegisterMode ? '创建新账户' : '系统登录' }}</h2>

    <!-- 表单提交时调用统一的 handleSubmit 函数 -->
    <form @submit.prevent="handleSubmit">
      <input v-model="username" placeholder="用户名" required />
      <input v-model="password" type="password" placeholder="密码" required />
      <!-- 按钮文字根据模式动态变化 -->
      <button type="submit">{{ isRegisterMode ? '注册' : '登录' }}</button>
    </form>

    <!-- 消息提示区 -->
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="successMessage" class="success-message">{{ successMessage }}</p>

    <!-- 新增：模式切换链接 -->
    <p class="toggle-mode">
      {{ isRegisterMode ? '已有账户?' : '还没有账户?' }}
      <a href="#" @click.prevent="toggleMode">
        {{ isRegisterMode ? '立即登录' : '立即注册' }}
      </a>
    </p>
  </div>
</template>

<style scoped>
/* 原有样式保持不变 */
.login-container { max-width: 400px; margin: 80px auto; padding: 2.5em; background-color: #ffffff; border-radius: 12px; box-shadow: var(--card-shadow); text-align: center; border: 1px solid var(--border-color); }
h2 { margin-top: 0; margin-bottom: 1.5em; color: var(--text-color); font-weight: 600; }
form { display: flex; flex-direction: column; gap: 1.5em; }
button[type="submit"] { background-color: var(--primary-color); color: white; font-size: 1.1em; border: none; }
button[type="submit"]:hover { background-color: var(--primary-hover-color); }

/* 消息样式 */
.error-message { color: var(--danger-color); margin-top: 1.5em; font-size: 0.9em; }
/* 新增：成功消息样式 */
.success-message { color: var(--success-color); margin-top: 1.5em; font-size: 0.9em; }

/* 新增：模式切换链接样式 */
.toggle-mode {
  margin-top: 2em;
  font-size: 0.9em;
  color: var(--text-secondary-color);
}
.toggle-mode a {
  font-weight: 600;
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.2s;
}
.toggle-mode a:hover {
  color: var(--primary-hover-color);
}
</style>