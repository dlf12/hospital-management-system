<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api/apiClient';

// 数据状态
const templates = ref([]);
const loading = ref(false);
const showCreateForm = ref(false);
const editingTemplate = ref(null);

// 表单数据
const newTemplate = ref({
  name: '',
  description: '',
  content: {
    diagnosis: '',
    treatment_plan: ''
  },
  is_shared: false
});

// API 调用函数
const fetchTemplates = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/templates', { params: { mine: true } });
    templates.value = response.data || [];
  } catch (error) {
    console.error('获取模板失败:', error);
    templates.value = [];
  } finally {
    loading.value = false;
  }
};

const createTemplate = async () => {
  try {
    await apiClient.post('/templates', newTemplate.value);
    resetForm();
    showCreateForm.value = false;
    await fetchTemplates();
    alert('创建模板成功');
  } catch (error) {
    alert(error.response?.data?.message || '创建模板失败');
  }
};

const updateTemplate = async () => {
  if (!editingTemplate.value) return;
  try {
    await apiClient.put(`/templates/${editingTemplate.value.id}`, editingTemplate.value);
    editingTemplate.value = null;
    await fetchTemplates();
    alert('更新模板成功');
  } catch (error) {
    alert(error.response?.data?.message || '更新模板失败');
  }
};

const deleteTemplate = async (template) => {
  if (!confirm(`确定要删除模板 "${template.name}" 吗？`)) return;
  try {
    await apiClient.delete(`/templates/${template.id}`);
    await fetchTemplates();
    alert('删除模板成功');
  } catch (error) {
    alert('删除模板失败');
  }
};

const startEdit = (template) => {
  editingTemplate.value = { ...template };
  // 确保content是对象格式
  if (typeof editingTemplate.value.content === 'string') {
    try {
      editingTemplate.value.content = JSON.parse(editingTemplate.value.content);
    } catch (e) {
      editingTemplate.value.content = { diagnosis: '', treatment_plan: '' };
    }
  }
};

const cancelEdit = () => {
  editingTemplate.value = null;
};

const resetForm = () => {
  newTemplate.value = {
    name: '',
    description: '',
    content: {
      diagnosis: '',
      treatment_plan: ''
    },
    is_shared: false
  };
};

// 生命周期
onMounted(fetchTemplates);
</script>

<template>
  <div class="template-manager">
    <div class="template-header">
      <div class="header-left">
        <h2>模板管理</h2>
        <p class="header-subtitle">管理诊断和治疗方案模板，提高工作效率</p>
      </div>
      <button @click="showCreateForm = true" class="btn-create">
        <span class="btn-icon">+</span>
        新建模板
      </button>
    </div>

    <!-- 模板列表 -->
    <div class="template-grid">
      <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
      >
        <div class="template-card-header">
          <div class="template-info">
            <h3 class="template-name">{{ template.name }}</h3>
            <p class="template-description" v-if="template.description">
              {{ template.description }}
            </p>
            <div class="template-meta">
              <span class="meta-item">
                <span class="meta-icon">📅</span>
                {{ template.updated_at || template.created_at }}
              </span>
              <span v-if="template.is_shared" class="meta-item shared">
                <span class="meta-icon">🌐</span>
                已共享
              </span>
            </div>
          </div>
          <div class="template-actions">
            <button @click="startEdit(template)" class="btn-action edit">
              <span class="action-icon">✏️</span>
            </button>
            <button @click="deleteTemplate(template)" class="btn-action delete">
              <span class="action-icon">🗑️</span>
            </button>
          </div>
        </div>

        <div class="template-preview">
          <div class="preview-section" v-if="template.content.diagnosis || (typeof template.content === 'string' && template.content.includes('diagnosis'))">
            <label>诊断:</label>
            <div class="preview-content">
              {{
                typeof template.content === 'object'
                    ? template.content.diagnosis
                    : (template.content.includes('{') ? JSON.parse(template.content).diagnosis : template.content)
              }}
            </div>
          </div>
          <div class="preview-section" v-if="template.content.treatment_plan || (typeof template.content === 'string' && template.content.includes('treatment_plan'))">
            <label>治疗方案:</label>
            <div class="preview-content">
              {{
                typeof template.content === 'object'
                    ? template.content.treatment_plan
                    : (template.content.includes('{') ? JSON.parse(template.content).treatment_plan : template.content)
              }}
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="templates.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>暂无模板</h3>
        <p>创建您的第一个模板，提高诊疗效率</p>
        <button @click="showCreateForm = true" class="btn-create-first">
          创建模板
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
    </div>

    <!-- 创建模板模态框 -->
    <div v-if="showCreateForm" class="modal-overlay" @click.self="showCreateForm = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>创建新模板</h3>
          <button @click="showCreateForm = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="createTemplate" class="template-form">
          <div class="form-group">
            <label>模板名称 <span class="required">*</span></label>
            <input
                v-model="newTemplate.name"
                placeholder="输入模板名称"
                required
            />
          </div>

          <div class="form-group">
            <label>模板描述</label>
            <input
                v-model="newTemplate.description"
                placeholder="简短描述此模板的用途（可选）"
            />
          </div>

          <div class="form-group">
            <label>诊断内容 <span class="required">*</span></label>
            <textarea
                v-model="newTemplate.content.diagnosis"
                rows="4"
                placeholder="输入标准诊断内容"
                required
            ></textarea>
          </div>

          <div class="form-group">
            <label>治疗方案 <span class="required">*</span></label>
            <textarea
                v-model="newTemplate.content.treatment_plan"
                rows="4"
                placeholder="输入标准治疗方案"
                required
            ></textarea>
          </div>

          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input
                  type="checkbox"
                  v-model="newTemplate.is_shared"
              />
              <span class="checkbox-text">
                <span class="checkbox-title">共享模板</span>
                <span class="checkbox-subtitle">允许其他用户使用此模板</span>
              </span>
            </label>
          </div>

          <div class="form-actions">
            <button type="button" @click="showCreateForm = false; resetForm();" class="btn-cancel">
              取消
            </button>
            <button type="submit" class="btn-submit">
              创建模板
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑模板模态框 -->
    <div v-if="editingTemplate" class="modal-overlay" @click.self="cancelEdit">
      <div class="modal-content">
        <div class="modal-header">
          <h3>编辑模板</h3>
          <button @click="cancelEdit" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="updateTemplate" class="template-form">
          <div class="form-group">
            <label>模板名称 <span class="required">*</span></label>
            <input
                v-model="editingTemplate.name"
                placeholder="输入模板名称"
                required
            />
          </div>

          <div class="form-group">
            <label>模板描述</label>
            <input
                v-model="editingTemplate.description"
                placeholder="简短描述此模板的用途（可选）"
            />
          </div>

          <div class="form-group">
            <label>诊断内容 <span class="required">*</span></label>
            <textarea
                v-model="editingTemplate.content.diagnosis"
                rows="4"
                placeholder="输入标准诊断内容"
                required
            ></textarea>
          </div>

          <div class="form-group">
            <label>治疗方案 <span class="required">*</span></label>
            <textarea
                v-model="editingTemplate.content.treatment_plan"
                rows="4"
                placeholder="输入标准治疗方案"
                required
            ></textarea>
          </div>

          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input
                  type="checkbox"
                  v-model="editingTemplate.is_shared"
              />
              <span class="checkbox-text">
                <span class="checkbox-title">共享模板</span>
                <span class="checkbox-subtitle">允许其他用户使用此模板</span>
              </span>
            </label>
          </div>

          <div class="form-actions">
            <button type="button" @click="cancelEdit" class="btn-cancel">
              取消
            </button>
            <button type="submit" class="btn-submit">
              保存更改
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.template-manager {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* 头部区域 */
.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.header-left h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: #2d3748;
}

.header-subtitle {
  margin: 0;
  color: #718096;
  font-size: 1rem;
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}

.btn-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

/* 模板网格 */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.template-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  overflow: hidden;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e0;
}

.template-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  border-bottom: 1px solid #f7fafc;
}

.template-info {
  flex: 1;
}

.template-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
}

.template-description {
  margin: 0 0 1rem 0;
  color: #718096;
  font-size: 0.9rem;
  line-height: 1.5;
}

.template-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #a0aec0;
}

.meta-item.shared {
  color: #38a169;
  font-weight: 500;
}

.meta-icon {
  font-size: 0.9rem;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  width: 36px;
  height: 36px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action.edit:hover {
  background: #ebf8ff;
  border-color: #63b3ed;
}

.btn-action.delete:hover {
  background: #fed7d7;
  border-color: #fc8181;
}

.action-icon {
  font-size: 0.9rem;
}

/* 模板预览 */
.template-preview {
  padding: 1.5rem;
  background: #f7fafc;
}

.preview-section {
  margin-bottom: 1rem;
}

.preview-section:last-child {
  margin-bottom: 0;
}

.preview-section label {
  display: block;
  font-weight: 500;
  color: #4a5568;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.preview-content {
  color: #2d3748;
  font-size: 0.9rem;
  line-height: 1.5;
  max-height: 60px;
  overflow: hidden;
  position: relative;
}

.preview-content::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 20px;
  background: linear-gradient(transparent, #f7fafc);
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #a0aec0;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  color: #4a5568;
}

.empty-state p {
  margin: 0 0 2rem 0;
  font-size: 1rem;
}

.btn-create-first {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* 加载状态 */
.loading-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #a0aec0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1.3rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #a0aec0;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f7fafc;
  color: #4a5568;
}

/* 表单样式 */
.template-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #4a5568;
  font-size: 0.9rem;
}

.required {
  color: #e53e3e;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.2s ease;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
  line-height: 1.5;
}

.checkbox-group {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  background: #f7fafc;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  margin-bottom: 0;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
  margin-top: 0.1rem;
}

.checkbox-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.checkbox-title {
  font-weight: 500;
  color: #2d3748;
}

.checkbox-subtitle {
  font-size: 0.85rem;
  color: #718096;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.btn-cancel {
  padding: 0.75rem 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #4a5568;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.btn-submit {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-submit:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}
</style>