<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api/apiClient';

const templates = ref([]);
const editing = ref(null);
const newTpl = ref({ name:'', description:'', content:{ diagnosis:'', treatment_plan:'' }, is_shared:false });

const fetchTemplates = async () => {
  try {
    const res = await apiClient.get('/templates', { params: { mine: true }});
    templates.value = res.data;
  } catch(err){ templates.value = []; }
};

const createTpl = async () => {
  try {
    await apiClient.post('/templates', {
      name: newTpl.value.name,
      description: newTpl.value.description,
      content: newTpl.value.content,
      is_shared: newTpl.value.is_shared
    });
    newTpl.value = { name:'', description:'', content:{ diagnosis:'', treatment_plan:'' }, is_shared:false };
    await fetchTemplates();
    alert('创建成功');
  } catch(err){ alert('创建失败'); }
};

const deleteTpl = async (id) => {
  if(!confirm('确认删除模板？')) return;
  await apiClient.delete('/templates/' + id);
  await fetchTemplates();
};

onMounted(fetchTemplates);
</script>

<template>
  <div class="template-card">
    <h3>模板管理</h3>
    <div class="create-form">
      <input v-model="newTpl.name" placeholder="模板名称" />
      <input v-model="newTpl.description" placeholder="描述(可选)" />
      <label>诊断</label>
      <textarea v-model="newTpl.content.diagnosis" rows="2"></textarea>
      <label>治疗方案</label>
      <textarea v-model="newTpl.content.treatment_plan" rows="2"></textarea>
      <div>
        <label><input type="checkbox" v-model="newTpl.is_shared" /> 共享</label>
      </div>
      <button @click="createTpl">创建模板</button>
    </div>

    <hr />

    <ul>
      <li v-for="t in templates" :key="t.id">
        <div><strong>{{ t.name }}</strong> <small>{{ t.description }}</small></div>
        <div><pre style="white-space:pre-wrap">{{ typeof t.content === 'string' ? t.content : JSON.stringify(t.content, null, 2) }}</pre></div>
        <div>
          <button @click="deleteTpl(t.id)">删除</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.template-card { text-align:left; padding:1em; background:#fff; border-radius:8px; }
.create-form input, .create-form textarea { width:100%; margin-bottom:0.5em; }
</style>
