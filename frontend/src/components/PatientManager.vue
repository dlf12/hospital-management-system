<script setup>
import { ref, onMounted, watch } from 'vue';
import apiClient from '../api/apiClient'; // 导入 apiClient

// --- 响应式变量 ---
const patients = ref([]);
const newPatient = ref({ name: '', id_card: '', age: '', gender: '男', phone_number: '' });

// 病历管理相关
const selectedPatient = ref(null);
const patientRecords = ref([]);
const newRecord = ref({ 
  symptom: '',
  diagnosis: '', 
  treatment_plan: '',
  medical_history: '',
  allergy_history: ''
});
const showRecordModal = ref(false);

// 新增：病人编辑相关
const showEditPatientModal = ref(false);
const editingPatient = ref(null);

// 新增：搜索相关 & 分页
const searchQuery = ref('');
let searchTimeout = null;

const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const totalPages = ref(1);

// --- 模板相关 ---
const templates = ref([]);             // 模板列表
const selectedTemplateId = ref(null);  // 下拉选中的模板 id
const saveAsTemplateName = ref('');    // 保存为模板时的名称
const showTemplateManager = ref(false);

// --- API 调用函数 ---
// 1. 获取所有病人（支持搜索 & 分页）
const fetchPatients = async () => {
  try {
    const response = await apiClient.get('/patients', {
      params: {
        search: searchQuery.value,
        page: page.value,
        per_page: perPage.value
      }
    });
    patients.value = response.data.items || response.data;
    total.value = response.data.total || 0;
    page.value = response.data.page || 1;
    totalPages.value = response.data.pages || 1;
  } catch (error) {
    console.error("获取病人列表失败:", error);
    // 如果 401，可自动登出（apiClient 已处理）
  }
};

// 2. 监听搜索框的变化（防抖）
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    page.value = 1; // 新搜索回到第一页
    fetchPatients();
  }, 300);
});

// 3. 添加病人
const addPatient = async () => {
  try {
    await apiClient.post('/patients', newPatient.value);
    newPatient.value = { name: '', id_card: '', age: '', gender: '男', phone_number: '' }; // 重置表单
    await fetchPatients();
    alert('添加成功');
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
    const isLastItemOnPage = patients.value.length === 1 && page.value > 1;
    if (isLastItemOnPage) page.value--;
    await fetchPatients();
  } catch (error) {
    console.error("删除病人失败:", error);
    alert('删除失败！');
  }
};

// 5. 更新病人
const updatePatient = async () => {
  if (!editingPatient.value) return;
  try {
    await apiClient.put(`/patients/${editingPatient.value.id}`, editingPatient.value);
    showEditPatientModal.value = false;
    await fetchPatients();
    alert('更新成功');
  } catch (error) {
    console.error("更新病人信息失败:", error);
    alert('更新失败，请重试！');
  }
};

// --- 病历相关函数 ---
const fetchTemplates = async () => {
  try {
    const response = await apiClient.get('/templates', { params: { mine: true } });
    templates.value = response.data || [];
  } catch (error) {
    console.error('获取模板失败', error);
    templates.value = [];
  }
};

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
  // 同时加载模板
  await fetchTemplates();
};

const addRecord = async () => {
  if (!newRecord.value.symptom) {
    alert('症状不能为空！');
    return;
  }
  if (!newRecord.value.diagnosis || !newRecord.value.treatment_plan) {
    alert('诊断信息和治疗方案不能为空！');
    return;
  }
  try {
    await apiClient.post(`/patients/${selectedPatient.value.id}/records`, newRecord.value);
    newRecord.value = { 
      symptom: '',
      diagnosis: '', 
      treatment_plan: '',
      medical_history: '',
      allergy_history: ''
    };
    // 刷新病历列表
    const response = await apiClient.get(`/patients/${selectedPatient.value.id}/records`);
    patientRecords.value = response.data;
  } catch (error) {
    console.error("添加病历失败:", error);
    alert('添加病历失败');
  }
};

// --- 模板应用与保存 ---
// 当选择模板时，把模板内容填入 newRecord
const applySelectedTemplate = () => {
  if (!selectedTemplateId.value) return;
  const tpl = templates.value.find(t => t.id === selectedTemplateId.value);
  if (!tpl) return;
  let content = tpl.content;
  // content 可能为对象或字符串
  try {
    if (typeof content === 'string') content = JSON.parse(content || '{}');
  } catch (e) {
    // 解析失败则当作纯文本（不会填充）
    content = {};
  }
  newRecord.value.symptom = content.symptom || newRecord.value.symptom;
  newRecord.value.diagnosis = content.diagnosis || newRecord.value.diagnosis;
  newRecord.value.treatment_plan = content.treatment_plan || newRecord.value.treatment_plan;
  newRecord.value.medical_history = content.medical_history || newRecord.value.medical_history;
  newRecord.value.allergy_history = content.allergy_history || newRecord.value.allergy_history;
};

// 保存当前填写的 newRecord 为模板
const saveCurrentRecordAsTemplate = async () => {
  if (!newRecord.value.diagnosis || !newRecord.value.treatment_plan) {
    alert('要保存为模板，请先填写诊断和治疗方案。');
    return;
  }
  const name = saveAsTemplateName.value || `模板-${new Date().toISOString().slice(0,10)}`;
  const payload = {
    name,
    content: {
      symptom: newRecord.value.symptom,
      diagnosis: newRecord.value.diagnosis,
      treatment_plan: newRecord.value.treatment_plan,
      medical_history: newRecord.value.medical_history,
      allergy_history: newRecord.value.allergy_history
    }
  };
  try {
    await apiClient.post('/templates', payload);
    alert('已保存为模板');
    await fetchTemplates();
    saveAsTemplateName.value = '';
  } catch (error) {
    console.error('保存为模板失败', error);
    alert(error.response?.data?.message || '保存模板失败');
  }
};

// 将某条历史病历保存为模板（调用后端 save_as_template 接口）
const saveRecordAsTemplate = async (rec) => {
  const name = prompt('请输入模板名称（可留空使用默认）') || '';
  try {
    const res = await apiClient.post(`/patients/${selectedPatient.value.id}/records/${rec.id}/save_as_template`, { name });
    alert('历史病历已保存为模板');
    await fetchTemplates();
  } catch (error) {
    console.error('保存历史病历为模板失败', error);
    alert('保存失败');
  }
};

// --- 模态框控制函数 ---
const openEditPatientModal = (patient) => {
  editingPatient.value = { ...patient };
  showEditPatientModal.value = true;
};

const closeRecordModal = () => {
  showRecordModal.value = false;
  selectedPatient.value = null;
  patientRecords.value = [];
  // 清空模板选择
  selectedTemplateId.value = null;
  saveAsTemplateName.value = '';
};

const closeEditPatientModal = () => {
  showEditPatientModal.value = false;
  editingPatient.value = null;
};

// --- 分页控制 ---
const goToPage = (p) => {
  if (p < 1 || p > totalPages.value) return;
  page.value = p;
  fetchPatients();
};
const nextPage = () => {
  if (page.value < totalPages.value) {
    page.value++;
    fetchPatients();
  }
};
const prevPage = () => {
  if (page.value > 1) {
    page.value--;
    fetchPatients();
  }
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
        <div style="display:flex; gap:8px; align-items:center;">
          <input v-model.trim="searchQuery" class="search-input" placeholder="按姓名或身份证号搜索..." />
          <select v-model.number="perPage" @change="() => { page = 1; fetchPatients(); }">
            <option :value="5">5 / 页</option>
            <option :value="10">10 / 页</option>
            <option :value="20">20 / 页</option>
          </select>
        </div>
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

      <!-- 分页控件 -->
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1em;">
        <div>共 {{ total }} 条， 第 {{ page }} / {{ totalPages }} 页</div>
        <div style="display:flex; gap:8px; align-items:center;">
          <button @click="prevPage" :disabled="page <= 1">上一页</button>
          <button v-for="p in Math.min(5, totalPages)" :key="p" @click="goToPage(p)">
            {{ p }}
          </button>
          <button @click="nextPage" :disabled="page >= totalPages">下一页</button>
        </div>
      </div>
    </div>

    <!-- 病历管理模态框 -->
    <div v-if="showRecordModal" class="modal-overlay" @click.self="closeRecordModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeRecordModal">&times;</button>
        <h3>病历：{{ selectedPatient?.name }}</h3>

        <!-- 新增病历表单 -->
        <form @submit.prevent="addRecord" class="modal-form">
          <label>症状</label>
          <textarea v-model="newRecord.symptom" rows="3" placeholder="填写症状"></textarea>
          <label>诊断</label>
          <textarea v-model="newRecord.diagnosis" rows="3" placeholder="填写诊断"></textarea>
          <label>治疗方案</label>
          <textarea v-model="newRecord.treatment_plan" rows="3" placeholder="填写治疗方案"></textarea>
          <label>既往病史</label>
          <textarea v-model="newRecord.medical_history" rows="3" placeholder="填写既往病史（可选）"></textarea>
          <label>过敏史</label>
          <textarea v-model="newRecord.allergy_history" rows="3" placeholder="填写过敏史（可选）"></textarea>

          <!-- 模板控件 -->
          <div style="display:flex; gap:8px; align-items:center; margin-top:8px; flex-wrap:wrap;">
            <select v-model="selectedTemplateId" @change="applySelectedTemplate">
              <option :value="null">选择模板（可选）</option>
              <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>

            <input v-model="saveAsTemplateName" placeholder="保存为模板的名称 (可选)" style="max-width:320px;" />

            <button type="button" @click="saveCurrentRecordAsTemplate">保存当前为模板</button>

            <button type="button" @click="showTemplateManager = true">管理模板</button>
          </div>

          <button type="submit">添加病历</button>
        </form>

        <hr/>

        <!-- 病历列表 -->
        <div v-if="patientRecords.length">
          <h4>历史病历（最新在前）</h4>
          <ul>
            <li v-for="rec in patientRecords" :key="rec.id" style="text-align:left; margin-bottom:12px;">
              <div><strong>日期：</strong>{{ rec.record_date }}</div>
              <div><strong>诊断：</strong><pre style="white-space:pre-wrap">{{ rec.diagnosis }}</pre></div>
              <div><strong>治疗：</strong><pre style="white-space:pre-wrap">{{ rec.treatment_plan }}</pre></div>
              <div style="margin-top:6px;">
                <button @click="saveRecordAsTemplate(rec)">保存为模板</button>
              </div>
            </li>
          </ul>
        </div>
        <div v-else>
          <p>暂无病历记录。</p>
        </div>
      </div>
    </div>

    <!-- 编辑病人模态框 -->
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

    <!-- 模板管理模态 -->
    <div v-if="showTemplateManager" class="modal-overlay" @click.self="showTemplateManager=false">
      <div class="modal-content">
        <button class="close-btn" @click="showTemplateManager=false">&times;</button>
        <h3>模板管理</h3>
        <div style="text-align:left; margin-top:12px;">
          <ul>
            <li v-for="t in templates" :key="t.id" style="margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div><strong>{{ t.name }}</strong> <small style="color:var(--text-secondary-color)">{{ t.description }}</small></div>
                <div style="display:flex; gap:8px;">
                  <button @click="() => { selectedTemplateId = t.id; applySelectedTemplate(); showTemplateManager=false; }">使用模板</button>
                  <button @click="async () => { if(confirm('确定删除该模板？')) { try { await apiClient.delete('/templates/' + t.id); await fetchTemplates(); } catch(e){ alert('删除失败'); } } }">删除</button>
                </div>
              </div>
              <div style="white-space:pre-wrap; margin-top:6px; color:var(--text-secondary-color);">
                {{ typeof t.content === 'string' ? t.content : JSON.stringify(t.content, null, 2) }}
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* 保留你原先的样式（略） */
/* 这里可以保留或复制你已有的样式定义 */
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

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(5px); }
.modal-content { background-color: #fff; padding: 2.5em; border-radius: 12px; width: 90%; max-width: 700px; max-height: 90vh; overflow-y: auto; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.close-btn { position: absolute; top: 15px; right: 20px; font-size: 2em; background: none; border: none; color: var(--text-secondary-color); cursor: pointer; padding: 0; line-height: 1; }

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
