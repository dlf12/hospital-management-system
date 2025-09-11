<script setup>
// 1. 导入需要的工具
import { ref } from 'vue';      // 'ref' 用来创建响应式变量，当变量改变时，界面会自动更新
import axios from 'axios';    // 用来发送 HTTP 请求给后端

// 2. 定义一个 emit 函数，用于向父组件（App.vue）发送“登录成功”的信号
const emit = defineEmits(['login-success']);

// 3. 创建响应式变量来绑定表单输入
const username = ref('');      // 对应用户名输入框
const password = ref('');      // 对应密码输入框
const errorMessage = ref('');  // 用来存储登录失败时的错误信息

// 4. 定义处理登录的函数
const handleLogin = async () => {
  // 清空之前的错误信息
  errorMessage.value = '';

  try {
    // 5. 使用 axios 发送 POST 请求到后端的 /api/login 接口
    const response = await axios.post('http://127.0.0.1:5000/api/login', {
      username: username.value,
      password: password.value,
    });

    // 6. 如果请求成功（没有抛出错误），就意味着登录成功
    console.log("登录成功:", response.data.message);

    // 7. 发送 'login-success' 事件，通知父组件
    emit('login-success');

  } catch (error) {
    // 8. 如果请求失败（比如后端返回 401 错误），代码会进入 catch 块
    if (error.response) {
      // 从后端的响应中获取错误信息并显示
      errorMessage.value = error.response.data.message || '登录失败，请重试！';
    } else {
      errorMessage.value = '无法连接到服务器，请检查后端是否运行。';
    }
    console.error("登录失败:", error);
  }
};
</script>

<template>
  <div class="login-container">
    <h2>系统登录</h2>

    <!-- 使用 @submit.prevent 来监听表单提交事件，并调用 handleLogin 函数 -->
    <form @submit.prevent="handleLogin">

      <!-- 使用 v-model 将输入框的值与 script 中的响应式变量双向绑定 -->
      <input v-model="username" placeholder="用户名" required />
      <input v-model="password" type="password" placeholder="密码" required />

      <button type="submit">登录</button>
    </form>

    <!-- 如果 errorMessage 有内容，就显示这个错误提示 -->
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  </div>
</template>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 80px auto;
  padding: 2.5em;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  text-align: center;
  border: 1px solid var(--border-color);
}

h2 {
  margin-top: 0;
  margin-bottom: 1.5em;
  color: var(--text-color);
  font-weight: 600;
}

.error-message {
  color: var(--danger-color);
  margin-top: 1.5em;
  font-size: 0.9em;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1.5em; /* 使用 gap 增加间距 */
}

input {
  /* 样式已在 style.css 中统一，这里可以留空或微调 */
}

button[type="submit"] {
  background-color: var(--primary-color);
  color: white;
  font-size: 1.1em;
  border: none;
}

button[type="submit"]:hover {
  background-color: var(--primary-hover-color);
}
</style>