<script setup>
import { ref, onMounted } from 'vue';
import Login from './components/Login.vue';
import DepartmentView from './components/DepartmentView.vue';
import TemplateManager from './components/TemplateManager.vue';

// 登录状态管理
const isLoggedIn = ref(false);
const currentUser = ref('');

// 视图状态管理
const currentView = ref('departments'); // 'departments' | 'department' | 'templates'
const selectedDepartment = ref(null);

// 登录成功处理
const onLoginSuccess = (token) => {
  localStorage.setItem('accessToken', token);
  isLoggedIn.value = true;
  const userData = JSON.parse(atob(token.split('.')[1]));
  currentUser.value = userData.sub || '用户';
};

// 登出处理
const handleLogout = () => {
  localStorage.removeItem('accessToken');
  isLoggedIn.value = false;
  currentUser.value = '';
  currentView.value = 'departments';
  selectedDepartment.value = null;
};

// 返回主界面
const goBack = () => {
  if (currentView.value === 'department') {
    currentView.value = 'departments';
    selectedDepartment.value = null;
  } else if (currentView.value === 'templates') {
    currentView.value = 'departments';
  }
};

// 进入科室
const enterDepartment = (department) => {
  selectedDepartment.value = department;
  currentView.value = 'department';
};

// 打开模板管理
const openTemplateManager = () => {
  currentView.value = 'templates';
};

// 检查登录状态
onMounted(() => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    try {
      const userData = JSON.parse(atob(token.split('.')[1]));
      currentUser.value = userData.sub || '用户';
      isLoggedIn.value = true;
    } catch (e) {
      localStorage.removeItem('accessToken');
    }
  }
});
</script>

<template>
  <!-- 未登录状态 -->
  <div v-if="!isLoggedIn" class="login-wrapper">
    <Login @login-success="onLoginSuccess" />
  </div>

  <!-- 已登录状态 -->
  <div v-else class="app-container">
    <!-- 顶栏 -->
    <header class="top-bar">
      <div class="top-bar-left">
        <h1 class="system-title">医院病历管理系统</h1>
        <button
            v-if="currentView !== 'departments'"
            @click="goBack"
            class="btn btn-secondary"
        >
          返回
        </button>
      </div>
      <div class="top-bar-right">
        <button @click="openTemplateManager" class="btn btn-secondary">
          模板管理
        </button>
        <div class="user-info">
          <span class="user-name">{{ currentUser }}</span>
          <button @click="handleLogout" class="btn btn-logout">
            登出
          </button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 科室选择界面 -->
      <div v-if="currentView === 'departments'" class="departments-view">
        <h2 class="page-title">请选择科室</h2>
        <div class="departments-grid">
          <div
              class="department-card"
              @click="enterDepartment('内科')"
          >
            <div class="department-icon internal-medicine"></div>
            <h3>内科</h3>
            <p>内科疾病诊疗</p>
          </div>
          <div
              class="department-card"
              @click="enterDepartment('外科')"
          >
            <div class="department-icon surgery"></div>
            <h3>外科</h3>
            <p>外科手术治疗</p>
          </div>
          <div
              class="department-card"
              @click="enterDepartment('妇产科')"
          >
            <div class="department-icon gynecology"></div>
            <h3>妇产科</h3>
            <p>妇科产科诊疗</p>
          </div>
          <div
              class="department-card"
              @click="enterDepartment('儿科')"
          >
            <div class="department-icon pediatrics"></div>
            <h3>儿科</h3>
            <p>儿童疾病诊疗</p>
          </div>
        </div>
      </div>

      <!-- 科室病人管理界面 -->
      <DepartmentView
          v-else-if="currentView === 'department'"
          :department="selectedDepartment"
      />

      <!-- 模板管理界面 -->
      <TemplateManager
          v-else-if="currentView === 'templates'"
      />
    </main>
  </div>
</template>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 顶栏样式 */
.top-bar {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 2rem;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.system-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-left: 1rem;
  border-left: 1px solid #e2e8f0;
}

.user-name {
  font-weight: 500;
  color: #4a5568;
}

/* 主要内容区域 */
.main-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* 科室选择界面 */
.departments-view {
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 3rem;
}

.departments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.department-card {
  background: white;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.department-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.department-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  position: relative;
}

.department-icon::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1));
}

.internal-medicine {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.internal-medicine::before {
  content: '🫀';
}

.surgery {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.surgery::before {
  content: '🔬';
}

.gynecology {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.gynecology::before {
  content: '👶';
}

.pediatrics {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.pediatrics::before {
  content: '🧸';
}

.department-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.department-card p {
  color: #718096;
  font-size: 1rem;
  margin: 0;
}

/* 按钮样式 */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.btn-secondary {
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.btn-logout {
  background: #fed7d7;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.btn-logout:hover {
  background: #feb2b2;
}
</style>