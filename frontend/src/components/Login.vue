<script setup>
import { ref } from 'vue';
import apiClient from '../api/apiClient';

const emit = defineEmits(['login-success']);

// 响应式变量
const username = ref('');
const password = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const isRegisterMode = ref(false);
const loading = ref(false);

// 模式切换
const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value;
  username.value = '';
  password.value = '';
  errorMessage.value = '';
  successMessage.value = '';
};

// 处理登录
const handleLogin = async () => {
  loading.value = true;
  try {
    const response = await apiClient.post('/login', {
      username: username.value,
      password: password.value,
    });
    emit('login-success', response.data.access_token);
  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || '登录失败，请重试';
    } else {
      errorMessage.value = '无法连接到服务器';
    }
  } finally {
    loading.value = false;
  }
};

// 处理注册
const handleRegister = async () => {
  loading.value = true;
  try {
    const response = await apiClient.post('/register', {
      username: username.value,
      password: password.value,
    });
    successMessage.value = `${response.data.message}，请登录`;
    isRegisterMode.value = false;
    errorMessage.value = '';
    password.value = '';
  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.message || '注册失败，请重试';
    } else {
      errorMessage.value = '无法连接到服务器';
    }
  } finally {
    loading.value = false;
  }
};

// 统一提交
const handleSubmit = () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!username.value || !password.value) {
    errorMessage.value = '用户名和密码不能为空';
    return;
  }

  if (isRegisterMode.value) {
    handleRegister();
  } else {
    handleLogin();
  }
};
</script>

<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-container">
      <div class="login-card">
        <!-- 系统标识 -->
        <div class="system-branding">
          <div class="brand-icon">
            <div class="medical-cross">+</div>
          </div>
          <h1 class="brand-title">医院病历管理系统</h1>
          <p class="brand-subtitle">Hospital Medical Record Management System</p>
        </div>

        <!-- 登录表单 -->
        <div class="form-section">
          <div class="form-header">
            <h2>{{ isRegisterMode ? '创建新账户' : '系统登录' }}</h2>
            <p>{{ isRegisterMode ? '请填写信息创建账户' : '请登录您的账户以继续' }}</p>
          </div>

          <form @submit.prevent="handleSubmit" class="login-form">
            <div class="input-group">
              <div class="input-wrapper">
                <span class="input-icon">👤</span>
                <input
                    v-model="username"
                    type="text"
                    placeholder="用户名"
                    class="form-input"
                    required
                    :disabled="loading"
                />
              </div>
            </div>

            <div class="input-group">
              <div class="input-wrapper">
                <span class="input-icon">🔒</span>
                <input
                    v-model="password"
                    type="password"
                    placeholder="密码"
                    class="form-input"
                    required
                    :disabled="loading"
                />
              </div>
            </div>

            <button
                type="submit"
                class="submit-button"
                :disabled="loading"
            >
              <span v-if="loading" class="loading-spinner"></span>
              <span v-else>{{ isRegisterMode ? '注册账户' : '登录系统' }}</span>
            </button>
          </form>

          <!-- 消息提示 -->
          <div v-if="errorMessage" class="message error-message">
            <span class="message-icon">⚠️</span>
            {{ errorMessage }}
          </div>

          <div v-if="successMessage" class="message success-message">
            <span class="message-icon">✅</span>
            {{ successMessage }}
          </div>

          <!-- 模式切换 -->
          <div class="mode-toggle">
            <span class="toggle-text">
              {{ isRegisterMode ? '已有账户？' : '还没有账户？' }}
            </span>
            <button
                type="button"
                @click="toggleMode"
                class="toggle-button"
                :disabled="loading"
            >
              {{ isRegisterMode ? '立即登录' : '立即注册' }}
            </button>
          </div>
        </div>

        <!-- 底部信息 -->
        <div class="footer-info">
          <p>专业 · 安全 · 高效</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
  animation: float 20s ease-in-out infinite;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -100px;
  animation: float 15s ease-in-out infinite reverse;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 20%;
  left: 10%;
  animation: float 25s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* 登录容器 */
.login-container {
  width: 100%;
  max-width: 480px;
  position: relative;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  animation: slideUp 0.8s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 系统标识 */
.system-branding {
  text-align: center;
  padding: 3rem 2rem 2rem;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-bottom: 1px solid #e2e8f0;
}

.brand-icon {
  margin: 0 auto 1.5rem;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.medical-cross {
  font-size: 2.5rem;
  color: white;
  font-weight: bold;
}

.brand-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  margin: 0;
  color: #718096;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 表单区域 */
.form-section {
  padding: 2.5rem;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
}

.form-header p {
  margin: 0;
  color: #718096;
  font-size: 0.95rem;
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  position: relative;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  z-index: 1;
  font-size: 1.1rem;
  color: #a0aec0;
}

.form-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  background: #f7fafc;
  cursor: not-allowed;
}

.submit-button {
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 消息提示 */
.message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-top: 1rem;
}

.error-message {
  background: #fed7d7;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.success-message {
  background: #c6f6d5;
  color: #22543d;
  border: 1px solid #9ae6b4;
}

.message-icon {
  font-size: 1rem;
}

/* 模式切换 */
.mode-toggle {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.toggle-text {
  color: #718096;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.toggle-button {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  text-decoration: underline;
}

.toggle-button:hover:not(:disabled) {
  color: #553c9a;
}

.toggle-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 底部信息 */
.footer-info {
  text-align: center;
  padding: 1.5rem;
  background: #f7fafc;
  border-top: 1px solid #e2e8f0;
}

.footer-info p {
  margin: 0;
  color: #a0aec0;
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: 2px;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .login-page {
    padding: 1rem;
  }

  .system-branding {
    padding: 2rem 1.5rem 1.5rem;
  }

  .brand-title {
    font-size: 1.5rem;
  }

  .form-section {
    padding: 2rem 1.5rem;
  }

  .brand-icon {
    width: 60px;
    height: 60px;
  }

  .medical-cross {
    font-size: 2rem;
  }
}
</style>