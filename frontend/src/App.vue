<script setup>
// 1. 导入需要的工具和子组件
import { ref } from 'vue';
import PatientManager from './components/PatientManager.vue';
import Login from './components/Login.vue';

// 2. 创建一个响应式变量来跟踪登录状态
//    默认值为 false，表示用户初始为“未登录”状态
const isLoggedIn = ref(false);

// 3. 定义一个函数，用来响应 Login.vue 组件发出的 'login-success' 事件
//    当这个函数被调用时，就将登录状态改为 true
const onLoginSuccess = () => {
  isLoggedIn.value = true;
};
</script>

<template>
  <main>
    <h1>医院病历管理系统</h1>

    <!--
      这里是条件渲染的核心：
      v-if="!isLoggedIn" 的意思是：如果 isLoggedIn 是 false（即“未登录”），
      就显示 Login 组件。

      @login-success="onLoginSuccess" 是在监听子组件的事件。
      当 Login 组件内部 emit('login-success') 时，就会触发这里的 onLoginSuccess 函数。
    -->
    <Login v-if="!isLoggedIn" @login-success="onLoginSuccess" />

    <!--
      v-else 的意思是：如果上面的 v-if 条件不满足（即 isLoggedIn 是 true），
      就显示 PatientManager 组件。
    -->
    <PatientManager v-else />
  </main>
</template>

<style scoped>
main {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
