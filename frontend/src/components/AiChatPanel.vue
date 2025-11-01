<script setup>
import { ref, watch, nextTick, computed } from 'vue';
import apiClient from '../api/apiClient';

const props = defineProps({
  show: Boolean,
  patientInfo: Object,
  recordForm: Object
});

const emit = defineEmits(['close', 'apply-data']);

const messages = ref([]);
const loading = ref(false);
const messagesContainer = ref(null);

// 初始化欢迎消息
const initWelcomeMessage = () => {
  messages.value = [{
    type: 'ai',
    content: '您好！我是医疗AI助手，已成功接入。\n\n我可以为您提供：\n\n1️⃣ 智能推荐模板 - 基于症状匹配相似病历\n2️⃣ 智能诊断建议 - 生成诊断和治疗方案\n\n请选择您需要的功能：',
    buttons: [
      { label: '智能推荐模板', action: 'recommend' },
      { label: '智能诊断建议', action: 'diagnose' }
    ]
  }];
};

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 添加消息
const addMessage = async (message) => {
  messages.value.push(message);
  await scrollToBottom();
};

// 处理用户选择
const handleUserChoice = async (action, data) => {
  // 添加用户消息
  let userMessage = '';
  if (action === 'recommend') userMessage = '智能推荐模板';
  else if (action === 'diagnose') userMessage = '智能诊断建议';
  else if (action === 'reset') userMessage = '返回主菜单';
  else if (action === 'close') {
    emit('close');
    return;
  } else if (action === 'apply-template') {
    await handleApplyTemplate(data);
    return;
  } else if (action === 'apply-diagnosis') {
    await handleApplyDiagnosis(data);
    return;
  } else if (action === 'regenerate') {
    userMessage = '重新生成';
    await handleGenerateDiagnosis();
    return;
  }

  if (userMessage) {
    await addMessage({
      type: 'user',
      content: userMessage
    });
  }

  // 处理返回主菜单
  if (action === 'reset') {
    await addMessage({
      type: 'ai',
      content: '请选择您需要的功能：',
      buttons: [
        { label: '智能推荐模板', action: 'recommend' },
        { label: '智能诊断建议', action: 'diagnose' }
      ]
    });
    return;
  }

  // 前置条件检查
  if (!props.recordForm?.symptom || !props.recordForm.symptom.trim()) {
    await addMessage({
      type: 'ai',
      content: '⚠️ 请先在左侧病历编辑框填写症状信息，以便为您提供准确的建议。',
      buttons: [{ label: '知道了', action: 'reset' }]
    });
    return;
  }

  // 调用对应的API
  if (action === 'recommend') {
    await handleRecommendTemplate();
  } else if (action === 'diagnose') {
    await handleGenerateDiagnosis();
  }
};

// 智能推荐模板
const handleRecommendTemplate = async () => {
  loading.value = true;
  await addMessage({
    type: 'ai',
    content: '🔍 正在分析症状，为您推荐合适的模板...',
    isLoading: true
  });

  try {
    const { data } = await apiClient.post('/ai/suggest_templates', {
      symptom: props.recordForm.symptom
    });

    // 移除加载消息
    messages.value = messages.value.filter(m => !m.isLoading);

    if (data.items && data.items.length > 0) {
      const template = data.items[0]; // 取第一个推荐

      // 获取模板详情
      const templateDetail = await apiClient.get(`/templates/${template.id}`);
      const content = typeof templateDetail.data.content === 'string'
        ? JSON.parse(templateDetail.data.content)
        : templateDetail.data.content;

      const preview = `【诊断】${content.diagnosis || '未填写'}\n【治疗方案】${(content.treatment_plan || '未填写').substring(0, 50)}...`;

      await addMessage({
        type: 'ai',
        content: `✅ 基于症状"${props.recordForm.symptom}"，为您推荐以下模板：\n\n📋 【${template.name}】\n${preview}\n\n是否应用此模板？`,
        buttons: [
          { label: '✔ 应用此模板', action: 'apply-template', data: template.id },
          { label: '↩ 返回', action: 'reset' }
        ]
      });
    } else {
      await addMessage({
        type: 'ai',
        content: '😔 抱歉，暂未找到与症状匹配的模板。\n\n建议您使用"智能诊断建议"功能生成新的诊断方案。',
        buttons: [
          { label: '智能诊断建议', action: 'diagnose' },
          { label: '↩ 返回', action: 'reset' }
        ]
      });
    }
  } catch (error) {
    messages.value = messages.value.filter(m => !m.isLoading);
    await addMessage({
      type: 'ai',
      content: `❌ 推荐失败：${error.response?.data?.message || '请稍后重试'}`,
      buttons: [{ label: '↩ 返回', action: 'reset' }]
    });
  } finally {
    loading.value = false;
  }
};

// 智能诊断建议
const handleGenerateDiagnosis = async () => {
  loading.value = true;
  await addMessage({
    type: 'ai',
    content: '🤔 AI正在思考中，为您生成诊断建议...',
    isLoading: true
  });

  try {
    const { data } = await apiClient.post('/ai/generate_record_suggestion', {
      symptom: props.recordForm.symptom,
      medical_history: props.recordForm.medical_history,
      allergy_history: props.recordForm.allergy_history,
      age: props.patientInfo?.age,
      gender: props.patientInfo?.gender
    });

    // 移除加载消息
    messages.value = messages.value.filter(m => !m.isLoading);

    if (data.diagnosis || data.treatment_plan) {
      const diagnosisText = data.diagnosis || '暂无诊断建议';
      const treatmentText = data.treatment_plan || '暂无治疗方案';

      await addMessage({
        type: 'ai',
        content: `✅ 根据症状分析，生成以下建议：\n\n【诊断建议】\n${diagnosisText}\n\n【治疗方案】\n${treatmentText}\n\n是否将以上内容应用到病历？`,
        buttons: [
          { label: '✔ 应用到病历', action: 'apply-diagnosis', data: { diagnosis: data.diagnosis, treatment_plan: data.treatment_plan } },
          { label: '🔄 重新生成', action: 'regenerate' },
          { label: '↩ 返回', action: 'reset' }
        ]
      });
    } else {
      await addMessage({
        type: 'ai',
        content: '❌ AI生成内容为空，请检查症状描述是否准确。',
        buttons: [
          { label: '🔄 重新生成', action: 'regenerate' },
          { label: '↩ 返回', action: 'reset' }
        ]
      });
    }
  } catch (error) {
    messages.value = messages.value.filter(m => !m.isLoading);
    await addMessage({
      type: 'ai',
      content: `❌ AI生成失败：${error.response?.data?.message || '请稍后重试'}`,
      buttons: [
        { label: '🔄 重新生成', action: 'regenerate' },
        { label: '↩ 返回', action: 'reset' }
      ]
    });
  } finally {
    loading.value = false;
  }
};

// 应用模板
const handleApplyTemplate = async (templateId) => {
  await addMessage({
    type: 'user',
    content: '应用此模板'
  });

  try {
    const templateDetail = await apiClient.get(`/templates/${templateId}`);
    const content = typeof templateDetail.data.content === 'string'
      ? JSON.parse(templateDetail.data.content)
      : templateDetail.data.content;

    emit('apply-data', {
      type: 'template',
      data: content
    });

    await addMessage({
      type: 'ai',
      content: '✅ 已成功应用模板到病历！',
      buttons: [
        { label: '继续使用AI助手', action: 'reset' },
        { label: '关闭', action: 'close' }
      ]
    });
  } catch (error) {
    await addMessage({
      type: 'ai',
      content: `❌ 应用模板失败：${error.response?.data?.message || '请稍后重试'}`,
      buttons: [{ label: '↩ 返回', action: 'reset' }]
    });
  }
};

// 应用诊断建议
const handleApplyDiagnosis = async (data) => {
  await addMessage({
    type: 'user',
    content: '应用到病历'
  });

  emit('apply-data', {
    type: 'diagnosis',
    data: data
  });

  await addMessage({
    type: 'ai',
    content: '✅ 已成功应用诊断建议到病历！',
    buttons: [
      { label: '继续使用AI助手', action: 'reset' },
      { label: '关闭', action: 'close' }
    ]
  });
};

// 监听显示状态变化
watch(() => props.show, (newVal) => {
  if (newVal) {
    initWelcomeMessage();
    scrollToBottom();
  }
});
</script>

<template>
  <transition name="slide">
    <div v-if="show" class="ai-chat-panel">
      <header class="chat-header">
        <div class="header-title">
          <span class="ai-icon">🤖</span>
          <h3>AI医疗助手</h3>
        </div>
        <button @click="$emit('close')" class="btn-close" title="关闭">✕</button>
      </header>

      <div class="messages-container" ref="messagesContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-wrapper', `message-${msg.type}`]"
        >
          <div v-if="msg.type === 'ai'" class="message-ai">
            <div class="ai-avatar">🤖</div>
            <div class="message-content">
              <div class="bubble">
                <pre v-if="!msg.isLoading">{{ msg.content }}</pre>
                <div v-else class="loading-dots">
                  <span>{{ msg.content }}</span>
                  <div class="dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
              <div v-if="msg.buttons && !msg.isLoading" class="button-group">
                <button
                  v-for="(btn, btnIndex) in msg.buttons"
                  :key="btnIndex"
                  @click="handleUserChoice(btn.action, btn.data)"
                  :class="['option-btn', { 'primary': btn.action.includes('apply') }]"
                  :disabled="loading"
                >
                  {{ btn.label }}
                </button>
              </div>
            </div>
          </div>

          <div v-else class="message-user">
            <div class="bubble">{{ msg.content }}</div>
          </div>
        </div>
      </div>

      <div class="chat-footer">
        <p class="footer-hint">💡 提示：选择按钮与AI交互</p>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

.ai-chat-panel {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.ai-icon {
  font-size: 1.75rem;
}

.chat-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.btn-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 1.5rem;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: #f8f9fa;
}

.message-wrapper {
  margin-bottom: 1.5rem;
}

.message-ai {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.ai-avatar {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  max-width: 85%;
}

.bubble {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.bubble pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #2d3748;
}

.loading-dots {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dots {
  display: flex;
  gap: 4px;
}

.dots span {
  width: 6px;
  height: 6px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.option-btn {
  padding: 0.6rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #4a5568;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-btn:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.option-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.option-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.option-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.message-user {
  display: flex;
  justify-content: flex-end;
}

.message-user .bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.75rem 1rem;
  max-width: 80%;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.chat-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  background: white;
}

.footer-hint {
  margin: 0;
  font-size: 0.85rem;
  color: #718096;
  text-align: center;
}

/* 滚动条美化 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>
