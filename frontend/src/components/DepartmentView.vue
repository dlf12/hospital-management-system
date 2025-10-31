<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '../api/apiClient';

const props = defineProps({
  department: String
});

// 数据状态
const patients = ref([]);
const templates = ref([]);
const searchQuery = ref('');
const page = ref(1);
const perPage = ref(20);
const total = ref(0);
const loading = ref(false);

// 表单状态
const showAddPatientModal = ref(false);
const showEditPatientModal = ref(false);
const showRecordModal = ref(false);

const newPatient = ref({
  name: '',
  id_card: '',
  age: '',
  gender: '男',
  phone_number: '',
  department: props.department
});

const editingPatient = ref(null);

// 病历相关
const selectedPatient = ref(null);
const patientRecords = ref([]);
const selectedRecord = ref(null);
const selectedTemplateId = ref('');
const aiTemplateSuggestions = ref([]);
const aiGenerateLoading = ref(false);
const aiTemplateLoading = ref(false);

const recordForm = ref({
  symptom: '',
  diagnosis: '',
  treatment_plan: '',
  medical_history: '',
  allergy_history: ''
});

// API 调用
const fetchPatients = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/patients', {
      params: {
        search: searchQuery.value,
        page: page.value,
        per_page: perPage.value,
        department: props.department
      }
    });
    patients.value = response.data.items || response.data;
    total.value = response.data.total || 0;
  } catch (error) {
    console.error('获取病人列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const fetchTemplates = async () => {
  try {
    const response = await apiClient.get('/templates');
    templates.value = response.data;
  } catch (error) {
    console.error('获取模板失败:', error);
    templates.value = [];
  }
};

// 病人操作
const openAddPatientModal = () => {
  newPatient.value = {
    name: '',
    id_card: '',
    age: '',
    gender: '男',
    phone_number: '',
    department: props.department
  };
  showAddPatientModal.value = true;
};

const addPatient = async () => {
  try {
    await apiClient.post('/patients', newPatient.value);
    showAddPatientModal.value = false;
    await fetchPatients();
    alert('添加成功');
  } catch (error) {
    alert(error.response?.data?.message || '添加失败');
  }
};

const openEditPatientModal = (patient) => {
  editingPatient.value = { ...patient };
  showEditPatientModal.value = true;
};

const updatePatient = async () => {
  try {
    await apiClient.put(`/patients/${editingPatient.value.id}`, editingPatient.value);
    showEditPatientModal.value = false;
    await fetchPatients();
    alert('更新成功');
  } catch (error) {
    alert('更新失败');
  }
};

const deletePatient = async (patient) => {
  if (!confirm(`确定要删除病人 ${patient.name} 及其所有病历吗？`)) return;
  try {
    await apiClient.delete(`/patients/${patient.id}`);
    await fetchPatients();
    alert('删除成功');
  } catch (error) {
    alert('删除失败');
  }
};

// 病历操作
const openRecordModal = async (patient) => {
  selectedPatient.value = patient;
  try {
    const response = await apiClient.get(`/patients/${patient.id}/records`);
    patientRecords.value = response.data;
  } catch (error) {
    console.error('获取病历失败:', error);
    patientRecords.value = [];
  }
  
  // 重置表单
  recordForm.value = {
    symptom: '',
    diagnosis: '',
    treatment_plan: '',
    medical_history: '',
    allergy_history: ''
  };
  selectedRecord.value = null;
  selectedTemplateId.value = '';
  aiTemplateSuggestions.value = [];
  
  await fetchTemplates();
  showRecordModal.value = true;
};

const selectRecord = (record) => {
  selectedRecord.value = record;
  recordForm.value = {
    symptom: record.symptom || '',
    diagnosis: record.diagnosis,
    treatment_plan: record.treatment_plan,
    medical_history: record.medical_history || '',
    allergy_history: record.allergy_history || ''
  };
  aiTemplateSuggestions.value = [];
};

const addNewRecord = () => {
  selectedRecord.value = null;
  recordForm.value = {
    symptom: '',
    diagnosis: '',
    treatment_plan: '',
    medical_history: '',
    allergy_history: ''
  };
  aiTemplateSuggestions.value = [];
};

const saveRecord = async () => {
  if (!recordForm.value.symptom) {
    alert('症状不能为空');
    return;
  }
  if (!recordForm.value.diagnosis || !recordForm.value.treatment_plan) {
    alert('诊断和治疗方案不能为空');
    return;
  }
  
  try {
    if (selectedRecord.value) {
      // 更新现有病历
      await apiClient.put(
        `/patients/${selectedPatient.value.id}/records/${selectedRecord.value.id}`,
        recordForm.value
      );
      alert('更新成功');
    } else {
      // 添加新病历
      await apiClient.post(
        `/patients/${selectedPatient.value.id}/records`,
        recordForm.value
      );
      alert('添加成功');
    }
    
    // 刷新病历列表
    const response = await apiClient.get(`/patients/${selectedPatient.value.id}/records`);
    patientRecords.value = response.data;
    
    // 重置表单
    addNewRecord();
  } catch (error) {
    alert('保存失败');
  }
};

const applyTemplate = () => {
  if (!selectedTemplateId.value) return;
  
  const template = templates.value.find(t => t.id == selectedTemplateId.value);
  if (!template) return;
  
  let content = template.content;
  try {
    if (typeof content === 'string') {
      content = JSON.parse(content);
    }
  } catch (e) {
    content = {};
  }
  
  recordForm.value.symptom = content.symptom || recordForm.value.symptom;
  recordForm.value.diagnosis = content.diagnosis || recordForm.value.diagnosis;
  recordForm.value.treatment_plan = content.treatment_plan || recordForm.value.treatment_plan;
  recordForm.value.medical_history = content.medical_history || recordForm.value.medical_history;
  recordForm.value.allergy_history = content.allergy_history || recordForm.value.allergy_history;
};

const exportAsTemplate = async () => {
  if (!selectedRecord.value) {
    alert('请先选择一条病历');
    return;
  }
  
  const name = prompt('请输入模板名称:');
  if (!name) return;
  
  try {
    await apiClient.post(
      `/patients/${selectedPatient.value.id}/records/${selectedRecord.value.id}/save_as_template`,
      { name }
    );
    await fetchTemplates();
    alert('导出模板成功');
  } catch (error) {
    alert('导出模板失败');
  }
};

const aiGenerateSuggestions = async () => {
  if (!recordForm.value.symptom) {
    alert('请先填写症状');
    return;
  }

  aiGenerateLoading.value = true;
  try {
    const payload = {
      symptom: recordForm.value.symptom,
      medical_history: recordForm.value.medical_history,
      allergy_history: recordForm.value.allergy_history,
      age: selectedPatient.value?.age,
      gender: selectedPatient.value?.gender
    };

    const { data } = await apiClient.post('/ai/generate_record_suggestion', payload);
    if (data?.diagnosis) {
      recordForm.value.diagnosis = data.diagnosis;
    }
    if (data?.treatment_plan) {
      recordForm.value.treatment_plan = data.treatment_plan;
    }
  } catch (error) {
    alert(error.response?.data?.message || 'AI 生成失败');
  } finally {
    aiGenerateLoading.value = false;
  }
};

const aiSuggestTemplates = async () => {
  if (!recordForm.value.symptom) {
    alert('请先填写症状');
    return;
  }

  aiTemplateLoading.value = true;
  try {
    const { data } = await apiClient.post('/ai/suggest_templates', {
      symptom: recordForm.value.symptom
    });
    aiTemplateSuggestions.value = data?.items || [];
    if (!aiTemplateSuggestions.value.length) {
      alert('未找到匹配的模板');
    }
  } catch (error) {
    aiTemplateSuggestions.value = [];
    alert(error.response?.data?.message || 'AI 推荐失败');
  } finally {
    aiTemplateLoading.value = false;
  }
};

const useSuggestedTemplate = async (templateId) => {
  if (!templateId) return;
  selectedTemplateId.value = String(templateId);
  await applyTemplate();
};

// 生命周期
onMounted(() => {
  fetchPatients();
  fetchTemplates();
});
</script>

<template>
  <div class="department-view">
    <!-- 头部搜索栏 -->
    <div class="header-section">
      <div class="header-title">
        <h2>{{ department }} - 病人列表</h2>
      </div>
      <div class="header-actions">
        <input
          v-model="searchQuery"
          @input="fetchPatients"
          placeholder="搜索病人姓名或身份证号..."
          class="search-input"
        />
        <button @click="openAddPatientModal" class="btn-add">
          ➕ 新增
        </button>
      </div>
    </div>

    <!-- 病人列表表格 -->
    <div class="table-container">
      <table class="patient-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>账号</th>
            <th>姓名</th>
            <th>年龄</th>
            <th>性别</th>
            <th>角色</th>
            <th>电话</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="patient in patients" :key="patient.id">
            <td>{{ patient.id }}</td>
            <td>{{ patient.id_card.substring(0, 6) }}</td>
            <td>{{ patient.name }}</td>
            <td>{{ patient.age }}</td>
            <td>
              <span :class="['gender-badge', patient.gender === '男' ? 'male' : 'female']">
                {{ patient.gender }}
              </span>
            </td>
            <td>
              <span class="role-badge">患者</span>
            </td>
            <td>{{ patient.phone_number || '未填写' }}</td>
            <td class="action-buttons">
              <button @click="openEditPatientModal(patient)" class="btn-edit">
                编辑
              </button>
              <button @click="openRecordModal(patient)" class="btn-record">
                病历编辑
              </button>
              <button @click="deletePatient(patient)" class="btn-delete">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="patients.length === 0 && !loading" class="empty-state">
        <p>暂无病人数据</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
    </div>

    <!-- 添加病人模态框 -->
    <div v-if="showAddPatientModal" class="modal-overlay" @click.self="showAddPatientModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加新病人</h3>
          <button @click="showAddPatientModal = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="addPatient" class="modal-form">
          <div class="form-group">
            <label>姓名 <span class="required">*</span></label>
            <input v-model="newPatient.name" required placeholder="请输入姓名" />
          </div>
          <div class="form-group">
            <label>身份证号 <span class="required">*</span></label>
            <input v-model="newPatient.id_card" required placeholder="请输入身份证号" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>年龄</label>
              <input v-model.number="newPatient.age" type="number" placeholder="请输入年龄" />
            </div>
            <div class="form-group">
              <label>性别</label>
              <select v-model="newPatient.gender">
                <option>男</option>
                <option>女</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>联系电话</label>
            <input v-model="newPatient.phone_number" placeholder="请输入联系电话" />
          </div>
          <div class="form-actions">
            <button type="button" @click="showAddPatientModal = false" class="btn-cancel">
              取消
            </button>
            <button type="submit" class="btn-submit">
              添加
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑病人模态框 -->
    <div v-if="showEditPatientModal" class="modal-overlay" @click.self="showEditPatientModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>编辑病人信息</h3>
          <button @click="showEditPatientModal = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="updatePatient" class="modal-form">
          <div class="form-group">
            <label>姓名 <span class="required">*</span></label>
            <input v-model="editingPatient.name" required placeholder="请输入姓名" />
          </div>
          <div class="form-group">
            <label>身份证号 <span class="required">*</span></label>
            <input v-model="editingPatient.id_card" required placeholder="请输入身份证号" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>年龄</label>
              <input v-model.number="editingPatient.age" type="number" placeholder="请输入年龄" />
            </div>
            <div class="form-group">
              <label>性别</label>
              <select v-model="editingPatient.gender">
                <option>男</option>
                <option>女</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>联系电话</label>
            <input v-model="editingPatient.phone_number" placeholder="请输入联系电话" />
          </div>
          <div class="form-actions">
            <button type="button" @click="showEditPatientModal = false" class="btn-cancel">
              取消
            </button>
            <button type="submit" class="btn-submit">
              保存
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 病历编辑模态框 -->
    <div v-if="showRecordModal" class="modal-overlay" @click.self="showRecordModal = false">
      <div class="modal-content large">
        <div class="modal-header">
          <h3>病历管理 - {{ selectedPatient?.name }}</h3>
          <button @click="showRecordModal = false" class="close-btn">✕</button>
        </div>
        
        <div class="record-modal-body">
          <!-- 左侧：病历列表 -->
          <div class="record-list-section">
            <div class="section-header">
              <h4>病历列表</h4>
              <button @click="addNewRecord" class="btn-new-record">+ 新增病历</button>
            </div>
            <div class="record-list">
              <div
                v-for="record in patientRecords"
                :key="record.id"
                :class="['record-item', { active: selectedRecord?.id === record.id }]"
                @click="selectRecord(record)"
              >
                <div class="record-date">{{ record.record_date }}</div>
                <div class="record-preview">{{ (record.symptom || record.diagnosis || '').substring(0, 30) }}...</div>
              </div>
              <div v-if="patientRecords.length === 0" class="empty-records">
                暂无病历记录
              </div>
            </div>
          </div>

          <!-- 右侧：病历编辑 -->
          <div class="record-edit-section">
            <div class="section-header">
              <h4>{{ selectedRecord ? '编辑病历' : '新增病历' }}</h4>
              <div class="template-actions">
                <select v-model="selectedTemplateId" @change="applyTemplate" class="template-select">
                  <option value="">选择模板（可选）</option>
                  <option v-for="t in templates" :key="t.id" :value="t.id">
                    {{ t.name }}
                  </option>
                </select>
                <button @click="aiSuggestTemplates" class="btn-secondary" :disabled="aiTemplateLoading">
                  {{ aiTemplateLoading ? '推荐中...' : 'AI 推荐模板' }}
                </button>
                <button @click="aiGenerateSuggestions" class="btn-primary" :disabled="aiGenerateLoading">
                  {{ aiGenerateLoading ? '生成中...' : 'AI 生成建议' }}
                </button>
                <button @click="exportAsTemplate" class="btn-export" :disabled="!selectedRecord">
                  📤 导出为模板
                </button>
              </div>
            </div>

            <div v-if="aiTemplateSuggestions.length" class="ai-suggestion-list">
              <span class="suggestion-title">AI 推荐模板：</span>
              <div class="suggestion-tags">
                <button
                  v-for="item in aiTemplateSuggestions"
                  :key="item.id"
                  type="button"
                  class="btn-secondary"
                  @click="useSuggestedTemplate(item.id)"
                >
                  {{ item.name }}
                </button>
              </div>
            </div>

            <form @submit.prevent="saveRecord" class="record-form">
              <div class="form-group">
                <label>症状 <span class="required">*</span></label>
                <textarea
                  v-model="recordForm.symptom"
                  rows="3"
                  placeholder="请输入症状信息"
                  required
                ></textarea>
              </div>
              <div class="form-group">
                <label>诊断 <span class="required">*</span></label>
                <textarea
                  v-model="recordForm.diagnosis"
                  rows="4"
                  placeholder="请输入诊断信息"
                  required
                ></textarea>
              </div>

              <div class="form-group">
                <label>治疗方案 <span class="required">*</span></label>
                <textarea
                  v-model="recordForm.treatment_plan"
                  rows="4"
                  placeholder="请输入治疗方案"
                  required
                ></textarea>
              </div>

              <div class="form-group">
                <label>既往病史</label>
                <textarea
                  v-model="recordForm.medical_history"
                  rows="3"
                  placeholder="请输入既往病史（选填）"
                ></textarea>
              </div>

              <div class="form-group">
                <label>过敏史</label>
                <textarea
                  v-model="recordForm.allergy_history"
                  rows="3"
                  placeholder="请输入过敏史（选填）"
                ></textarea>
              </div>

              <div class="form-actions">
                <button type="button" @click="addNewRecord" class="btn-reset">
                  重置
                </button>
                <button type="submit" class="btn-submit">
                  {{ selectedRecord ? '更新病历' : '添加病历' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.department-view {
  padding: 1.5rem;
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 头部区域 */
.header-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2d3748;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  width: 300px;
  font-size: 0.95rem;
  background: #ffffff;
  color: #2d3748;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn-add {
  padding: 0.75rem 1.5rem;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-add:hover {
  background: #38a169;
  transform: translateY(-1px);
}

/* 表格区域 */
.table-container {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.patient-table {
  width: 100%;
  border-collapse: collapse;
}

.patient-table thead {
  background: #f7fafc;
  position: sticky;
  top: 0;
  z-index: 1;
}

.patient-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid #e2e8f0;
}

.patient-table td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  color: #2d3748;
}

.patient-table tbody tr {
  transition: background 0.2s ease;
}

.patient-table tbody tr:hover {
  background: #f7fafc;
}

/* 徽章样式 */
.gender-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.gender-badge.male {
  background: #bee3f8;
  color: #2c5282;
}

.gender-badge.female {
  background: #fbb6ce;
  color: #97266d;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  background: #c6f6d5;
  color: #22543d;
  font-size: 0.85rem;
  font-weight: 500;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-buttons button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-edit {
  background: #f6ad55;
  color: white;
}

.btn-edit:hover {
  background: #ed8936;
}

.btn-record {
  background: #4299e1;
  color: white;
}

.btn-record:hover {
  background: #3182ce;
}

.btn-delete {
  background: #fc8181;
  color: white;
}

.btn-delete:hover {
  background: #f56565;
}

/* 模态框 */
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
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-content.large {
  max-width: 1200px;
  height: 85vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f7fafc;
}

.modal-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1.25rem;
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
  background: #e2e8f0;
  color: #4a5568;
}

/* 表单样式 */
.modal-form {
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
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.2s ease;
  font-family: inherit;
  background: #ffffff;
  color: #2d3748;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
  line-height: 1.5;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.btn-cancel,
.btn-reset {
  padding: 0.75rem 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #4a5568;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-cancel:hover,
.btn-reset:hover {
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

/* 病历模态框 */
.record-modal-body {
  display: grid;
  grid-template-columns: 300px 1fr;
  height: calc(85vh - 70px);
}

.record-list-section {
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  background: #f7fafc;
}

.record-edit-section {
  display: flex;
  flex-direction: column;
  background: white;
}

.section-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h4 {
  margin: 0;
  color: #2d3748;
  font-size: 1.1rem;
  font-weight: 600;
}

.btn-new-record {
  padding: 0.5rem 1rem;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-new-record:hover {
  background: #38a169;
}

.record-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.record-item {
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
  border: 2px solid transparent;
}

.record-item:hover {
  background: #edf2f7;
}

.record-item.active {
  background: #ebf8ff;
  border-color: #4299e1;
}

.record-date {
  font-weight: 500;
  color: #2d3748;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.record-preview {
  color: #718096;
  font-size: 0.85rem;
}

.empty-records {
  text-align: center;
  color: #a0aec0;
  padding: 2rem 1rem;
}

.record-form {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.template-select {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.85rem;
  background: white;
  color: #2d3748;
  cursor: pointer;
}

.ai-suggestion-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  padding: 0 1.5rem;
  margin-top: 0.75rem;
}

.suggestion-title {
  font-weight: 600;
  color: #4a5568;
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-export {
  padding: 0.5rem 1rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-export:hover:not(:disabled) {
  background: #3182ce;
}

.btn-export:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 空状态和加载 */
.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #a0aec0;
}

.spinner {
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
</style>
