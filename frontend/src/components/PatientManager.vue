<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// 后端 API 的地址
const API_URL = 'http://127.0.0.1:5000/api/patients';

// 存储病人列表的响应式变量
const patients = ref([]);

// 存储新病人表单数据的响应式变量
const newPatient = ref({
  name: '',
  id_card: '',
  age: '',
  gender: '男',
});

// --- API 调用函数 ---

// 1. 获取所有病人
const fetchPatients = async () => {
  try {
    const response = await axios.get(API_URL);
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
    await axios.post(API_URL, newPatient.value);
    // 清空表单
    newPatient.value = { name: '', id_card: '', age: '', gender: '男' };
    // 重新获取列表以刷新界面
    await fetchPatients();
  } catch (error) {
    console.error("添加病人失败:", error);
    alert('添加失败，可能是身份证号重复！');
  }
};

// 3. 删除一个病人
const deletePatient = async (patientId) => {
  if (!confirm('确定要删除该病人吗？')) return;
  try {
    await axios.delete(`${API_URL}/${patientId}`);
    // 重新获取列表以刷新界面
    await fetchPatients();
  } catch (error) {
    console.error("删除病人失败:", error);
  }
};

// --- 生命周期钩子 ---
// 组件加载完成后，自动获取一次病人列表
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
            <button class="delete-btn" @click="deletePatient(patient.id)">删除</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.container {
  font-family: sans-serif;
}
.form-card, .list-card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1.5em;
  margin-bottom: 2em;
  text-align: left;
}
input, select, button {
  padding: 0.8em;
  margin-right: 1em;
  border-radius: 4px;
  border: 1px solid #ccc;
}
button {
  cursor: pointer;
  background-color: #42b883;
  color: white;
  border: none;
}
button.delete-btn {
  background-color: #e74c3c;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
}
th, td {
  border: 1px solid #ddd;
  padding: 0.8em;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
</style>