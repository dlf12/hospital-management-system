<script setup>
import { ref, onMounted, watch } from 'vue';
import apiClient from '../api/apiClient'; // 导入 apiClient

// --- 响应式变量 ---
const patients = ref([]);
const newPatient = ref({ name: '', id_card: '', age: '', gender: '男', phone_number: '' });

// 病历管理相关
const selectedPatient = ref(null);
const patientRecords = ref([]);
const newRecord = ref({ diagnosis: '', treatment_plan: '' });
const showRecordModal = ref(false);

// 新增：病人编辑相关
const showEditPatientModal = ref(false);
const editingPatient = ref(null);

// 新增：搜索相关
const searchQuery = ref('');
let searchTimeout = null;

// --- API 调用函数 ---

// 1. 获取所有病人（支持搜索）
const fetchPatients = async () => {
  try {
    // 将搜索查询作为参数传递
    const response = await apiClient.get('/patients', {
      params: { search: searchQuery.value }
    });
    patients.value = response.data;
  } catch (error) {
    console.error("获取病人列表失败:", error);
    // 可选：如果 token 失效 (401)，可以触发登出
  }
};

// 2. 监听搜索框的变化
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  // 防抖处理：停止输入 300ms 后才发送请求
  searchTimeout = setTimeout(() => {
    fetchPatients();
  }, 300);
});


// 3. 添加病人
const addPatient = async () => {
  try {
    await apiClient.post('/patients', newPatient.value);
    newPatient.value = { name: '', id_card: '', age: '', gender: '男', phone_number: '' }; // 重置表单
    await fetchPatients();
  } catch (error) {
    console.error("添加病人失败:", error);
    alert(error.response?.data?.message || '添加失败，请检查输入！');
  }
};

// 4. 删除病人
const deletePatient = async (patientId) => {
  if (!confirm('确定要删除该病人及其所有病历吗？')) return;
  try {
    await apiClient.delete(`/patients/${patientId}`);
    await fetchPatients();
  } catch (error) {
    console.error("删除病人失败:", error);
  }
};

// 5. 更新病人
const updatePatient = async () => {
  if (!editingPatient.value) return;
  try {
    await apiClient.put(`/patients/${editingPatient.value.id}`, editingPatient.value);
    showEditPatientModal.value = false;
    await fetchPatients();
  } catch (error) {
    console.error("更新病人信息失败:", error);
    alert('更新失败，请重试！');
  }
};


// --- 病历相关函数 ---
const openRecordManager = async (patient) => {
  selectedPatient.value = patient;
  showRecordModal.value = true;
  try {
    const response = await apiClient.get(`/patients/${patient.id}/records`);
    patientRecords.value = response.data;
  } catch (error) {
    console.error(`获取病人 ${patient.name} 的病历失败:`, error);
    patientRecords.value = [];
  }
};

const addRecord = async () => {
  if (!newRecord.value.diagnosis || !newRecord.value.treatment_plan) {
    alert('诊断信息和治疗方案不能为空！');
    return;
  }
  try {
    await apiClient.post(`/patients/${selectedPatient.value.id}/records`, newRecord.value);
    newRecord.value = { diagnosis: '', treatment_plan: '' };
    await openRecordManager(selectedPatient.value); // 刷新列表
  } catch (error) {
    console.error("添加病历失败:", error);
  }
};

// --- 模态框控制函数 ---
const openEditPatientModal = (patient) => {
  // 创建一个病人的副本进行编辑，避免直接修改列表中的数据
  editingPatient.value = { ...patient };
  showEditPatientModal.value = true;
};

const closeRecordModal = () => {
  showRecordModal.value = false;
  selectedPatient.value = null;
};

const closeEditPatientModal = () => {
  showEditPatientModal.value = false;
  editingPatient.value = null;
};

// --- 生命周期钩子 ---
onMounted(fetchPatients);
</script>

<template>
  <div class="container">
    <!-- 新增病人表单 -->
    <div class="form-card">
      <h2>新增病人信息</h2>
      <form @submit.prevent="addPatient">
        <input v-model="newPatient.name" placeholder="姓名" required />
        <input v-model="newPatient.id_card" placeholder="身份证号" required />
        <input v-model.number="newPatient.age" type="number" placeholder="年龄" />
        <input v-model="newPatient.phone_number" placeholder="联系电话" />
        <select v-model="newPatient.gender">
          <option>男</option>
          <option>女</option>
        </select>
        <button type="submit">添加病人</button>
      </form>
    </div>

    <!-- 病人列表 -->
    <div class="list-card">
      <div class="list-header">
        <h2>病人信息列表</h2>
        <input v-model.trim="searchQuery" class="search-input" placeholder="按姓名或身份证号搜索..." />
      </div>
      <table>
        <thead>
        <tr>
          <th>姓名</th>
          <th>身份证号</th>
          <th>年龄</th>
          <th>性别</th>
          <th>联系电话</th>
          <th>操作</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="patient in patients" :key="patient.id">
          <td>{{ patient.name }}</td>
          <td>{{ patient.id_card }}</td>
          <td>{{ patient.age }}</td>
          <td>{{ patient.gender }}</td>
          <td>{{ patient.phone_number }}</td>
          <td>
            <button class="edit-btn" @click="openEditPatientModal(patient)">编辑</button>
            <button class="manage-btn" @click="openRecordManager(patient)">管理病历</button>
            <button class="delete-btn" @click="deletePatient(patient.id)">删除</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- 病历管理模态框 -->
    <div v-if="showRecordModal" class="modal-overlay" @click.self="closeRecordModal">
      <!-- ... 病历模态框内容保持不变 ... -->
    </div>

    <!-- 新增：编辑病人模态框 -->
    <div v-if="showEditPatientModal" class="modal-overlay" @click.self="closeEditPatientModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeEditPatientModal">&times;</button>
        <h3>编辑病人信息</h3>
        <form @submit.prevent="updatePatient" class="modal-form">
          <label>姓名:</label>
          <input v-model="editingPatient.name" required />
          <label>身份证号:</label>
          <input v-model="editingPatient.id_card" required />
          <label>年龄:</label>
          <input v-model.number="editingPatient.age" type="number" />
          <label>联系电话:</label>
          <input v-model="editingPatient.phone_number" />
          <label>性别:</label>
          <select v-model="editingPatient.gender">
            <option>男</option>
            <option>女</option>
          </select>
          <button type="submit">保存更新</button>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ... 原有样式 ... */
.container { display: flex; flex-direction: column; gap: 2em; }
.form-card, .list-card { background: #ffffff; border: 1px solid var(--border-color); border-radius: 12px; padding: 2em; box-shadow: var(--card-shadow); text-align: left; }
h2 { margin-top: 0; margin-bottom: 1.5em; font-size: 1.4em; font-weight: 600; color: var(--text-color); border-bottom: 1px solid var(--border-color); padding-bottom: 0.6em; }
.form-card form { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1.5em; align-items: center; }
.form-card form button { grid-column: -1; background-color: var(--success-color); color: white; border: none; }
.form-card form button:hover { background-color: var(--success-hover-color); }
table { width: 100%; border-collapse: collapse; margin-top: 1em; }
th, td { padding: 1em; text-align: left; border-bottom: 1px solid var(--border-color); }
thead th { font-weight: 600; color: var(--text-secondary-color); font-size: 0.9em; text-transform: uppercase; }
tbody tr:hover { background-color: var(--light-gray-color); }
td:last-child { display: flex; flex-wrap: wrap; gap: 0.8em; }

/* 新增样式 */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}
.search-input {
  max-width: 250px;
}
.edit-btn { background-color: #f39c12; color: white; }
.edit-btn:hover { background-color: #e67e22; }
.manage-btn { background-color: var(--primary-color); color: white; }
.manage-btn:hover { background-color: var(--primary-hover-color); }
.delete-btn { background-color: var(--danger-color); color: white; }
.delete-btn:hover { background-color: var(--danger-hover-color); }

.modal-overlay { /* ... */ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(5px); }
.modal-content { /* ... */ background-color: #fff; padding: 2.5em; border-radius: 12px; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.close-btn { /* ... */ position: absolute; top: 15px; right: 20px; font-size: 2em; background: none; border: none; color: var(--text-secondary-color); cursor: pointer; padding: 0; line-height: 1; }

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1em;
  margin-top: 1.5em;
}
.modal-form label {
  font-weight: 600;
  font-size: 0.9em;
  margin-bottom: -0.5em;
  color: var(--text-secondary-color);
}
.modal-form button {
  margin-top: 1em;
  background-color: var(--primary-color);
  color: white;
}
</style>