<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// --- 响应式变量定义 ---

// 后端 API 的基础地址
const API_URL = 'http://127.0.0.1:5000/api';

// 存储病人列表
const patients = ref([]);
// 存储新病人表单数据
const newPatient = ref({ name: '', id_card: '', age: '', gender: '男' });

// --- 新增：病历管理相关的响应式变量 ---
const selectedPatient = ref(null);    // 存储当前正在查看病历的病人对象
const patientRecords = ref([]);       // 存储所选病人的病历列表
const newRecord = ref({ diagnosis: '', treatment_plan: '' }); // 存储新病历的表单数据
const showRecordModal = ref(false);   // 控制病历模态框的显示与隐藏


// --- API 调用函数 ---

// 1. 获取所有病人
const fetchPatients = async () => {
  try {
    const response = await axios.get(`${API_URL}/patients`);
    patients.value = response.data;
  } catch (error) {
    console.error("获取病人列表失败:", error);
  }
};

// 2. 添加一个病人
const addPatient = async () => {
  if (!newPatient.value.name || !newPatient.value.id_card) {
    alert('姓名和身份证号不能为空！');
    return;
  }
  try {
    await axios.post(`${API_URL}/patients`, newPatient.value);
    newPatient.value = { name: '', id_card: '', age: '', gender: '男' };
    await fetchPatients();
  } catch (error) {
    console.error("添加病人失败:", error);
    alert('添加失败，可能是身份证号重复！');
  }
};

// 3. 删除一个病人
const deletePatient = async (patientId) => {
  if (!confirm('确定要删除该病人及其所有病历吗？')) return;
  try {
    await axios.delete(`${API_URL}/patients/${patientId}`);
    await fetchPatients();
  } catch (error) {
    console.error("删除病人失败:", error);
  }
};


// --- 新增：病历相关的函数 ---

// 4. 打开病历模态框并获取数据
const openRecordManager = async (patient) => {
  selectedPatient.value = patient;
  showRecordModal.value = true;
  try {
    const response = await axios.get(`${API_URL}/patients/${patient.id}/records`);
    patientRecords.value = response.data;
  } catch (error) {
    console.error(`获取病人 ${patient.name} 的病历失败:`, error);
    patientRecords.value = []; // 获取失败则清空
  }
};

// 5. 添加新病历
const addRecord = async () => {
  if (!newRecord.value.diagnosis || !newRecord.value.treatment_plan) {
    alert('诊断信息和治疗方案不能为空！');
    return;
  }
  try {
    // 向正确的病人ID下的 records 接口发送 POST 请求
    await axios.post(`${API_URL}/patients/${selectedPatient.value.id}/records`, newRecord.value);
    // 清空表单
    newRecord.value = { diagnosis: '', treatment_plan: '' };
    // 重新获取病历列表以刷新界面
    await openRecordManager(selectedPatient.value);
  } catch (error) {
    console.error("添加病历失败:", error);
    alert('添加病历失败，请重试！');
  }
};

// 6. 关闭模态框
const closeRecordModal = () => {
  showRecordModal.value = false;
  selectedPatient.value = null;
  patientRecords.value = [];
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
        <select v-model="newPatient.gender">
          <option>男</option>
          <option>女</option>
        </select>
        <button type="submit">添加病人</button>
      </form>
    </div>

    <!-- 病人列表 -->
    <div class="list-card">
      <h2>病人信息列表</h2>
      <table>
        <thead>
        <tr>
          <th>姓名</th>
          <th>身份证号</th>
          <th>年龄</th>
          <th>性别</th>
          <th>操作</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="patient in patients" :key="patient.id">
          <td>{{ patient.name }}</td>
          <td>{{ patient.id_card }}</td>
          <td>{{ patient.age }}</td>
          <td>{{ patient.gender }}</td>
          <td>
            <!-- 新增：管理病历按钮 -->
            <button class="manage-btn" @click="openRecordManager(patient)">管理病历</button>
            <button class="delete-btn" @click="deletePatient(patient.id)">删除</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增：病历管理模态框 -->
    <div v-if="showRecordModal" class="modal-overlay" @click.self="closeRecordModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeRecordModal">&times;</button>
        <h3>{{ selectedPatient?.name }} - 病历管理</h3>

        <!-- 新增病历表单 -->
        <div class="form-card record-form">
          <h4>新增病历</h4>
          <form @submit.prevent="addRecord">
            <textarea v-model="newRecord.diagnosis" placeholder="诊断信息" required></textarea>
            <textarea v-model="newRecord.treatment_plan" placeholder="治疗方案" required></textarea>
            <button type="submit">添加病历</button>
          </form>
        </div>

        <!-- 病历列表 -->
        <div class="list-card record-list">
          <h4>历史病历</h4>
          <div v-if="patientRecords.length === 0" class="no-records">暂无病历记录</div>
          <table v-else>
            <thead>
            <tr>
              <th>记录日期</th>
              <th>诊断信息</th>
              <th>治疗方案</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="record in patientRecords" :key="record.id">
              <td>{{ record.record_date }}</td>
              <td>{{ record.diagnosis }}</td>
              <td>{{ record.treatment_plan }}</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  gap: 2em; /* 模块间距 */
}

/* 卡片统一样式 */
.form-card, .list-card {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2em;
  box-shadow: var(--card-shadow);
  text-align: left;
}

h2 {
  margin-top: 0;
  margin-bottom: 1.5em;
  font-size: 1.4em;
  font-weight: 600;
  color: var(--text-color);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.6em;
}

/* 新增病人表单样式 */
.form-card form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); /* 响应式布局 */
  gap: 1.5em;
  align-items: center;
}

.form-card form button {
  grid-column: -1; /* 按钮始终在最后 */
  background-color: var(--success-color);
  color: white;
  border: none;
}
.form-card form button:hover {
  background-color: var(--success-hover-color);
}

/* 病人列表表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
}

th, td {
  padding: 1em;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

thead th {
  font-weight: 600;
  color: var(--text-secondary-color);
  font-size: 0.9em;
  text-transform: uppercase;
}

tbody tr:hover {
  background-color: var(--light-gray-color);
}

td:last-child {
  display: flex;
  gap: 0.8em; /* 按钮间距 */
}

/* 操作按钮样式 */
.manage-btn {
  background-color: var(--primary-color);
  color: white;
}
.manage-btn:hover {
  background-color: var(--primary-hover-color);
}
.delete-btn {
  background-color: var(--danger-color);
  color: white;
}
.delete-btn:hover {
  background-color: var(--danger-hover-color);
}


/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}
.modal-content {
  background-color: var(--light-gray-color);
  padding: 2.5em;
  border-radius: 12px;
  width: 90%;
  max-width: 750px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  color: var(--text-color);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 2em;
  background: none;
  border: none;
  color: var(--text-secondary-color);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
.modal-content h3, .modal-content h4 {
  margin-top: 0;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.6em;
  margin-bottom: 1em;
}
.record-form, .record-list {
  background-color: #fff;
  padding: 1.5em;
  border-radius: 8px;
  margin-top: 1.5em;
  border: 1px solid var(--border-color);
}
.record-form form {
  display: flex;
  flex-direction: column;
  gap: 1em;
}
.record-form button {
  align-self: flex-end; /* 按钮靠右 */
  background-color: var(--primary-color);
  color: white;
}
.record-form button:hover {
  background-color: var(--primary-hover-color);
}
textarea {
  min-height: 80px;
  resize: vertical;
}
.no-records {
  text-align: center;
  color: var(--text-secondary-color);
  padding: 2em;
}
</style>