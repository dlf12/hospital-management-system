<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '../api/apiClient';

const props = defineProps({
  department: String
});

// 数据状态
const patients = ref([]);
const selectedPatient = ref(null);
const patientRecords = ref([]);
const selectedRecord = ref(null);
const templates = ref([]);

// 搜索和分页
const searchQuery = ref('');
const page = ref(1);
const perPage = ref(20);
const total = ref(0);

// 界面状态
const showPatientForm = ref(false);
const showRecordForm = ref(false);
const showRecordDetail = ref(false);
const loading = ref(false);

// 表单数据
const newPatient = ref({
  name: '',
  id_card: '',
  age: '',
  gender: '男',
  phone_number: '',
  department: props.department
});

const newRecord = ref({
  diagnosis: '',
  treatment_plan: ''
});

const editingPatient = ref(null);

// 计算属性 - 功能按钮状态
const buttonStates = computed(() => ({
  addPatient: true,
  deletePatient: !!selectedPatient.value,
  editRecord: !!selectedPatient.value,
  importTemplate: showRecordDetail.value,
  exportTemplate: showRecordDetail.value && !!selectedRecord.value
}));

// API 调用函数
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

const fetchPatientRecords = async (patientId) => {
  try {
    const response = await apiClient.get(`/patients/${patientId}/records`);
    patientRecords.value = response.data;
  } catch (error) {
    console.error('获取病历失败:', error);
    patientRecords.value = [];
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

// 事件处理函数
const selectPatient = async (patient) => {
  selectedPatient.value = patient;
  selectedRecord.value = null;
  showRecordDetail.value = false;
  await fetchPatientRecords(patient.id);
};

const selectRecord = (record) => {
  selectedRecord.value = record;
  showRecordDetail.value = true;
};

const addPatient = async () => {
  try {
    await apiClient.post('/patients', newPatient.value);
    newPatient.value = {
      name: '',
      id_card: '',
      age: '',
      gender: '男',
      phone_number: '',
      department: props.department
    };
    showPatientForm.value = false;
    await fetchPatients();
    alert('添加成功');
  } catch (error) {
    alert(error.response?.data?.message || '添加失败');
  }
};

const deletePatient = async () => {
  if (!selectedPatient.value) return;
  if (!confirm(`确定要删除病人 ${selectedPatient.value.name} 及其所有病历吗？`)) return;

  try {
    await apiClient.delete(`/patients/${selectedPatient.value.id}`);
    selectedPatient.value = null;
    patientRecords.value = [];
    showRecordDetail.value = false;
    await fetchPatients();
    alert('删除成功');
  } catch (error) {
    alert('删除失败');
  }
};

const addRecord = async () => {
  if (!selectedPatient.value) return;
  try {
    await apiClient.post(`/patients/${selectedPatient.value.id}/records`, newRecord.value);
    newRecord.value = { diagnosis: '', treatment_plan: '' };
    showRecordForm.value = false;
    await fetchPatientRecords(selectedPatient.value.id);
    alert('添加病历成功');
  } catch (error) {
    alert('添加病历失败');
  }
};

const importTemplate = async (templateId) => {
  const template = templates.value.find(t => t.id === templateId);
  if (!template) return;

  let content = template.content;
  try {
    if (typeof content === 'string') {
      content = JSON.parse(content);
    }
  } catch (e) {
    content = {};
  }

  newRecord.value.diagnosis = content.diagnosis || '';
  newRecord.value.treatment_plan = content.treatment_plan || '';
};

const exportAsTemplate = async () => {
  if (!selectedRecord.value) return;
  const name = prompt('请输入模板名称:');
  if (!name) return;

  try {
    await apiClient.post(`/patients/${selectedPatient.value.id}/records/${selectedRecord.value.id}/save_as_template`, { name });
    await fetchTemplates();
    alert('导出模板成功');
  } catch (error) {
    alert('导出模板失败');
  }
};

// 生命周期
onMounted(() => {
  fetchPatients();
  fetchTemplates();
});
</script>

<template>
  <div class="department-view">
    <!-- 主要显示区域 - 病人列表 -->
    <div class="patient-list-section">
      <div class="section-header">
        <h2>{{ department }} - 病人列表</h2>
        <div class="search-controls">
          <input
              v-model="searchQuery"
              @input="fetchPatients"
              placeholder="搜索病人姓名或身份证号..."
              class="search-input"
          />
        </div>
      </div>

      <div class="patient-list" v-if="!loading">
        <div
            v-for="patient in patients"
            :key="patient.id"
            :class="['patient-row', { active: selectedPatient?.id === patient.id }]"
            @click="selectPatient(patient)"
        >
          <div class="patient-avatar">
            {{ patient.name.charAt(0) }}
          </div>
          <div class="patient-info">
            <div class="patient-name">{{ patient.name }}</div>
            <div class="patient-details">
              {{ patient.gender }} | {{ patient.age }}岁 | {{ patient.id_card }}
            </div>
            <div class="patient-contact" v-if="patient.phone_number">
              📞 {{ patient.phone_number }}
            </div>
          </div>
          <div class="patient-status">
            <span class="status-badge">在院</span>
          </div>
        </div>
      </div>

      <div v-else class="loading">
        加载中...
      </div>

      <div v-if="patients.length === 0 && !loading" class="empty-state">
        暂无病人数据
      </div>
    </div>

    <!-- 详细信息展示区域 -->
    <div class="detail-section">
      <div v-if="!selectedPatient" class="no-selection">
        <div class="placeholder-icon">👤</div>
        <p>请选择一个病人查看详细信息</p>
      </div>

      <div v-else class="patient-detail">
        <!-- 病人基本信息 -->
        <div class="detail-card">
          <h3>基本信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>姓名:</label>
              <span>{{ selectedPatient.name }}</span>
            </div>
            <div class="info-item">
              <label>性别:</label>
              <span>{{ selectedPatient.gender }}</span>
            </div>
            <div class="info-item">
              <label>年龄:</label>
              <span>{{ selectedPatient.age }}岁</span>
            </div>
            <div class="info-item">
              <label>身份证:</label>
              <span>{{ selectedPatient.id_card }}</span>
            </div>
            <div class="info-item">
              <label>联系电话:</label>
              <span>{{ selectedPatient.phone_number || '未填写' }}</span>
            </div>
          </div>
        </div>

        <!-- 病历信息菜单 -->
        <div class="detail-card">
          <h3>病历信息</h3>
          <div class="record-menu">
            <div
                v-for="record in patientRecords"
                :key="record.id"
                :class="['record-item', { active: selectedRecord?.id === record.id }]"
                @click="selectRecord(record)"
            >
              <div class="record-date">{{ record.record_date }}</div>
              <div class="record-preview">{{ record.diagnosis.substring(0, 30) }}...</div>
            </div>
          </div>

          <div v-if="patientRecords.length === 0" class="empty-records">
            暂无病历记录
          </div>
        </div>

        <!-- 病历详情 -->
        <div v-if="showRecordDetail && selectedRecord" class="detail-card">
          <h3>病历详情</h3>
          <div class="record-detail">
            <div class="detail-item">
              <label>诊断:</label>
              <div class="detail-content">{{ selectedRecord.diagnosis }}</div>
            </div>
            <div class="detail-item">
              <label>治疗方案:</label>
              <div class="detail-content">{{ selectedRecord.treatment_plan }}</div>
            </div>
            <div class="detail-item">
              <label>记录时间:</label>
              <div class="detail-content">{{ selectedRecord.record_date }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑功能区 -->
    <div class="function-section">
      <h3>功能操作</h3>
      <div class="function-buttons">
        <button
            :class="['func-btn', 'add-patient', { disabled: !buttonStates.addPatient }]"
            :disabled="!buttonStates.addPatient"
            @click="showPatientForm = true"
        >
          ➕ 添加病人
        </button>

        <button
            :class="['func-btn', 'delete-patient', { disabled: !buttonStates.deletePatient }]"
            :disabled="!buttonStates.deletePatient"
            @click="deletePatient"
        >
          🗑️ 删除病人
        </button>

        <button
            :class="['func-btn', 'edit-record', { disabled: !buttonStates.editRecord }]"
            :disabled="!buttonStates.editRecord"
            @click="showRecordForm = true"
        >
          📝 编辑病历
        </button>

        <hr class="function-divider" />

        <button
            :class="['func-btn', 'import-template', { disabled: !buttonStates.importTemplate }]"
            :disabled="!buttonStates.importTemplate"
        >
          📥 导入模板
        </button>

        <button
            :class="['func-btn', 'export-template', { disabled: !buttonStates.exportTemplate }]"
            :disabled="!buttonStates.exportTemplate"
            @click="exportAsTemplate"
        >
          📤 导出为模板
        </button>
      </div>
    </div>

    <!-- 添加病人模态框 -->
    <div v-if="showPatientForm" class="modal-overlay" @click.self="showPatientForm = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加新病人</h3>
          <button @click="showPatientForm = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="addPatient" class="patient-form">
          <div class="form-group">
            <label>姓名:</label>
            <input v-model="newPatient.name" required />
          </div>
          <div class="form-group">
            <label>身份证号:</label>
            <input v-model="newPatient.id_card" required />
          </div>
          <div class="form-group">
            <label>年龄:</label>
            <input v-model.number="newPatient.age" type="number" />
          </div>
          <div class="form-group">
            <label>性别:</label>
            <select v-model="newPatient.gender">
              <option>男</option>
              <option>女</option>
            </select>
          </div>
          <div class="form-group">
            <label>联系电话:</label>
            <input v-model="newPatient.phone_number" />
          </div>
          <div class="form-actions">
            <button type="button" @click="showPatientForm = false" class="btn-cancel">取消</button>
            <button type="submit" class="btn-submit">添加</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 添加病历模态框 -->
    <div v-if="showRecordForm" class="modal-overlay" @click.self="showRecordForm = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加病历 - {{ selectedPatient?.name }}</h3>
          <button @click="showRecordForm = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="addRecord" class="record-form">
          <div class="form-group">
            <label>选择模板:</label>
            <select @change="importTemplate($event.target.value)">
              <option value="">请选择模板（可选）</option>
              <option v-for="template in templates" :key="template.id" :value="template.id">
                {{ template.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>诊断:</label>
            <textarea v-model="newRecord.diagnosis" rows="4" required></textarea>
          </div>
          <div class="form-group">
            <label>治疗方案:</label>
            <textarea v-model="newRecord.treatment_plan" rows="4" required></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showRecordForm = false" class="btn-cancel">取消</button>
            <button type="submit" class="btn-submit">添加病历</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.department-view {
  display: grid;
  grid-template-columns: 1fr 350px 200px;
  gap: 1.5rem;
  height: calc(100vh - 140px);
  overflow: hidden;
}

/* 主要显示区域 - 病人列表 */
.patient-list-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  margin: 0;
  color: #2d3748;
  font-size: 1.25rem;
  font-weight: 600;
}

.search-input {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  width: 280px;
}

.patient-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.patient-row {
  display: flex;
  align-items: center;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.patient-row:hover {
  background: #f7fafc;
}

.patient-row.active {
  background: #ebf8ff;
  border-color: #3182ce;
}

.patient-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1.2rem;
  margin-right: 1rem;
}

.patient-info {
  flex: 1;
}

.patient-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.patient-details {
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.patient-contact {
  color: #4a5568;
  font-size: 0.85rem;
}

.patient-status {
  display: flex;
  align-items: center;
}

.status-badge {
  background: #c6f6d5;
  color: #22543d;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* 详细信息展示区域 */
.detail-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  overflow-y: auto;
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #a0aec0;
  text-align: center;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.detail-card {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.detail-card:last-child {
  border-bottom: none;
}

.detail-card h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
  font-size: 1.1rem;
  font-weight: 600;
}

.info-grid {
  display: grid;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item label {
  min-width: 80px;
  font-weight: 500;
  color: #4a5568;
  font-size: 0.9rem;
}

.info-item span {
  color: #2d3748;
}

.record-menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.record-item {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.record-item:hover {
  background: #f7fafc;
}

.record-item.active {
  background: #ebf8ff;
  border-color: #3182ce;
}

.record-date {
  font-weight: 500;
  color: #2d3748;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.record-preview {
  color: #718096;
  font-size: 0.8rem;
}

.detail-item {
  margin-bottom: 1rem;
}

.detail-item label {
  display: block;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.detail-content {
  color: #2d3748;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* 编辑功能区 */
.function-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  height: fit-content;
}

.function-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
  font-size: 1.1rem;
  font-weight: 600;
}

.function-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.func-btn {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  text-align: left;
  font-weight: 500;
}

.func-btn:not(.disabled):hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.func-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f7fafc;
}

.func-btn.add-patient:not(.disabled) {
  background: #c6f6d5;
  border-color: #68d391;
  color: #22543d;
}

.func-btn.delete-patient:not(.disabled) {
  background: #fed7d7;
  border-color: #fc8181;
  color: #c53030;
}

.func-btn.edit-record:not(.disabled) {
  background: #bee3f8;
  border-color: #63b3ed;
  color: #2c5282;
}

.function-divider {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 0.5rem 0;
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
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
}

.close-btn:hover {
  background: #f7fafc;
  color: #4a5568;
}

.patient-form,
.record-form {
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
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-cancel {
  padding: 0.75rem 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #4a5568;
  cursor: pointer;
}

.btn-submit {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: #3182ce;
  color: white;
  cursor: pointer;
  font-weight: 500;
}

.loading,
.empty-state,
.empty-records {
  text-align: center;
  color: #a0aec0;
  padding: 2rem;
}
</style>