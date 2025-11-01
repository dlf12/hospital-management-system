# AI智能助手对话功能 - 需求文档

**版本：** v1.0  
**日期：** 2025-11-01  
**项目：** 医院病历管理系统

---

## 一、功能概述

将现有的 AI 功能（智能推荐模板、智能诊断）从顶部按钮式交互，升级为侧边对话框交互模式，提供更友好、更具科技感的用户体验。

---

## 二、核心需求

### 2.1 界面布局

#### 2.1.1 AI启动按钮

- **位置**：病历编辑区域顶部操作栏
- **样式**：
  - 带渐变背景（紫蓝色渐变）
  - 图标：✨ 或 🤖
  - 文字：AI 助手
  - 悬停效果：提升 + 阴影

#### 2.1.2 AI对话框

- **触发**：点击"AI 助手"按钮
- **展现方式**：从右侧滑入
- **尺寸**：
  - 宽度：400px
  - 高度：与病历编辑区域同高
- **布局**：
```
┌─────────────────────┐
│  🤖 AI医疗助手        │  ← 标题栏
├─────────────────────┤
│                     │
│  [消息列表]          │  ← 滚动区域
│  - AI消息            │
│  - 用户选项按钮      │
│                     │
├─────────────────────┤
│  [操作按钮组]        │  ← 底部操作
└─────────────────────┘
```

#### 2.1.3 病历编辑框激活状态

- **触发**：AI对话框打开时
- **效果**：
  - 渐变边框（紫-蓝-粉渐变）
  - 呼吸动画效果（3秒循环）
  - 编辑框自适应收窄，为对话框留出空间

### 2.2 交互流程

#### 流程图

```
用户点击"AI 助手"
    ↓
对话框滑入 + 病历框显示渐变边框
    ↓
AI 发送欢迎消息：
  "您好！我是医疗AI助手，已成功接入。
   我可以为您提供：
   1️⃣ 智能推荐模板 - 基于症状匹配相似病历
   2️⃣ 智能诊断建议 - 生成诊断和治疗方案
   请选择您需要的功能："
   [智能推荐模板] [智能诊断建议]
    ↓
用户点击选项按钮
    ↓
┌─────────────────┬─────────────────┐
│ 智能推荐模板     │ 智能诊断建议     │
└─────────────────┴─────────────────┘
    ↓                   ↓
检查症状栏是否填写      检查症状栏是否填写
    ↓                   ↓
❌ 未填写           ❌ 未填写
AI提示：            AI提示：
"请先在左侧填写    "请先在左侧填写
症状信息"          症状信息，以便
                   生成准确的诊断建议"
    ↓                   ↓
✅ 已填写           ✅ 已填写
调用 API:           调用 API:
/ai/suggest_        /ai/generate_
templates           record_suggestion
    ↓                   ↓
显示加载动画         显示加载动画
"正在分析..."       "AI思考中..."
    ↓                   ↓
返回推荐结果         返回诊断结果
AI："基于症状       AI："根据症状分析，
'...'，为您推荐     建议诊断为：...
以下模板：          治疗方案：...

【模板名称】        是否将以上内容
模板内容预览...     应用到病历？"

是否应用此模板？"   [应用到病历] [重新生成]
[应用] [查看其他]
    ↓                   ↓
用户点击[应用]      用户点击[应用到病历]
    ↓                   ↓
自动填充到编辑框    自动填充到编辑框
AI："已成功应用"    AI："已成功应用"
```

### 2.3 前置条件判断

#### 2.3.1 智能推荐模板

- **前置条件**：症状 字段非空
- **判断时机**：用户点击"智能推荐模板"按钮时
- **未满足时**：
  - 不调用 API
  - AI 直接回复："请先在左侧病历编辑框填写症状信息，以便为您推荐合适的模板。"
  - 提供按钮：[知道了]（点击返回初始菜单）

#### 2.3.2 智能诊断建议

- **前置条件**：症状 字段非空
- **判断时机**：用户点击"智能诊断建议"按钮时
- **未满足时**：
  - 不调用 API
  - AI 直接回复："请先在左侧病历编辑框填写症状信息，以便生成准确的诊断建议。"
  - 提供按钮：[知道了]

### 2.4 对话方式设计

#### 2.4.1 消息类型

1. **AI 消息**：
   - 左对齐
   - 头像：🤖 图标
   - 背景：浅灰色气泡
   - 可包含文本 + 按钮组

2. **用户操作反馈**（非输入框）：
   - 右对齐
   - 背景：蓝色气泡
   - 显示用户点击的按钮文本

#### 2.4.2 按钮样式

- **选项按钮**：白底、蓝色边框、悬停变色
- **确认按钮**：渐变背景（与主题一致）
- **取消/返回按钮**：灰色边框

### 2.5 数据填充逻辑

#### 2.5.1 智能推荐模板

**API 返回：**
```json
{
  "template_id": 123,
  "template_name": "感冒诊疗模板",
  "content": {
    "diagnosis": "上呼吸道感染",
    "treatment_plan": "...",
    "medical_history": "...",
    "allergy_history": "..."
  }
}
```

**填充规则：**
- 将 content 中的字段填入对应的病历编辑框
- 保留用户已填写的 症状 字段（不覆盖）
- 其他字段直接覆盖

#### 2.5.2 智能诊断建议

**API 返回：**
```json
{
  "diagnosis": "...",
  "treatment_plan": "..."
}
```

**填充规则：**
- 仅填充 诊断 和 治疗方案 字段
- 保留用户已填写的 症状、既往病史、过敏史 字段

---

## 三、技术实现路径

### 3.1 技术栈

- **前端**：Vue 3 Composition API
- **样式**：CSS3（渐变、动画、过渡）
- **后端**：Flask + 现有 AI Service
- **API**：复用现有 /api/ai/* 接口

### 3.2 开发步骤

#### 第一步：创建 AI 对话组件 AiChatPanel.vue

**文件位置**：`frontend/src/components/AiChatPanel.vue`

**核心功能**：
- **Props**：
  - `show`：控制显隐
  - `patientInfo`：患者信息
  - `recordForm`：病历表单（用于前置条件判断）
- **Emits**：
  - `close`：关闭对话框
  - `apply-data`：应用数据到病历表单
- **状态管理**：
  - `messages`：消息列表 `[{type: 'ai'|'user', content, buttons}]`
  - `loading`：加载状态
  - `currentStep`：当前对话步骤

**UI 结构**：
```vue
<div class="ai-chat-panel">
  <header>
    <h3>🤖 AI医疗助手</h3>
    <button @click="$emit('close')">✕</button>
  </header>
  <div class="messages-container">
    <div v-for="msg in messages" :class="msg.type">
      {{ msg.content }}
      <div v-if="msg.buttons">
        <button v-for="btn in msg.buttons">...</button>
      </div>
    </div>
  </div>
</div>
```

#### 第二步：修改 DepartmentView.vue

**改动点**：
1. **移除顶部 AI 按钮**：
   - 删除 `@click="aiGenerateSuggestions"` 按钮
   - 删除 `@click="aiSuggestTemplates"` 按钮

2. **添加新的 AI 助手按钮**：
```vue
<button @click="openAiChat" class="btn-ai-assistant">
  ✨ AI 助手
</button>
```

3. **集成 AiChatPanel 组件**：
```vue
<AiChatPanel
  :show="showAiChat"
  :patient-info="selectedPatient"
  :record-form="recordForm"
  @close="showAiChat = false"
  @apply-data="handleApplyAiData"
/>
```

4. **添加激活状态类**：
```vue
<div class="record-edit-section" :class="{ 'ai-active': showAiChat }">
```

#### 第三步：实现对话逻辑

**核心方法**（在 AiChatPanel.vue 中）：

```javascript
// 初始化欢迎消息
const initWelcomeMessage = () => {
  messages.value = [{
    type: 'ai',
    content: '您好！我是医疗AI助手，已成功接入。\n我可以为您提供：\n1️⃣ 智能推荐模板\n2️⃣ 智能诊断建议\n\n请选择您需要的功能：',
    buttons: [
      { label: '智能推荐模板', action: 'recommend' },
      { label: '智能诊断建议', action: 'diagnose' }
    ]
  }];
};

// 处理用户选择
const handleUserChoice = async (action) => {
  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: action === 'recommend' ? '智能推荐模板' : '智能诊断建议'
  });

  // 前置条件检查
  if (!props.recordForm.symptom) {
    messages.value.push({
      type: 'ai',
      content: '请先在左侧病历编辑框填写症状信息...',
      buttons: [{ label: '知道了', action: 'reset' }]
    });
    return;
  }

  // 调用 API
  loading.value = true;
  if (action === 'recommend') {
    await handleRecommendTemplate();
  } else {
    await handleGenerateDiagnosis();
  }
  loading.value = false;
};

// 智能推荐模板
const handleRecommendTemplate = async () => {
  try {
    const { data } = await apiClient.post('/ai/suggest_templates', {
      symptom: props.recordForm.symptom
    });

    if (data.items?.length > 0) {
      const template = data.items[0]; // 取第一个推荐
      messages.value.push({
        type: 'ai',
        content: `基于症状"${props.recordForm.symptom}"，为您推荐以下模板：\n\n【${template.name}】\n${getTemplatePreview(template)}`,
        buttons: [
          { label: '应用此模板', action: 'apply-template', data: template.id },
          { label: '返回', action: 'reset' }
        ]
      });
    } else {
      messages.value.push({
        type: 'ai',
        content: '抱歉，暂未找到匹配的模板。',
        buttons: [{ label: '返回', action: 'reset' }]
      });
    }
  } catch (error) {
    messages.value.push({
      type: 'ai',
      content: '推荐失败，请稍后重试。',
      buttons: [{ label: '返回', action: 'reset' }]
    });
  }
};

// 智能诊断建议
const handleGenerateDiagnosis = async () => {
  try {
    const { data } = await apiClient.post('/ai/generate_record_suggestion', {
      symptom: props.recordForm.symptom,
      medical_history: props.recordForm.medical_history,
      allergy_history: props.recordForm.allergy_history,
      age: props.patientInfo?.age,
      gender: props.patientInfo?.gender
    });

    messages.value.push({
      type: 'ai',
      content: `根据症状分析，生成以下建议：\n\n【诊断】\n${data.diagnosis}\n\n【治疗方案】\n${data.treatment_plan}\n\n是否将以上内容应用到病历？`,
      buttons: [
        { label: '应用到病历', action: 'apply-diagnosis', data },
        { label: '重新生成', action: 'diagnose' },
        { label: '返回', action: 'reset' }
      ]
    });
  } catch (error) {
    messages.value.push({
      type: 'ai',
      content: 'AI生成失败，请稍后重试。',
      buttons: [{ label: '返回', action: 'reset' }]
    });
  }
};

// 应用数据
const applyData = (action, data) => {
  emit('apply-data', { action, data });
  messages.value.push({
    type: 'ai',
    content: '✅ 已成功应用到病历！',
    buttons: [
      { label: '继续使用AI助手', action: 'reset' },
      { label: '关闭', action: 'close' }
    ]
  });
};
```

#### 第四步：实现 CSS 样式

**1. AI 助手按钮样式**
```css
.btn-ai-assistant {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-ai-assistant:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
}
```

**2. 渐变边框激活状态**
```css
.record-edit-section.ai-active {
  position: relative;
  border: 3px solid transparent;
  background:
    linear-gradient(white, white) padding-box,
    linear-gradient(135deg, #667eea, #764ba2, #f093fb, #667eea) border-box;
  background-size: 300% 300%;
  animation: borderGradient 3s ease infinite;
  border-radius: 12px;
}

@keyframes borderGradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

**3. 对话框样式**
```css
.ai-chat-panel {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px;
  height: 100%;
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.message-ai {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.message-ai .bubble {
  background: #f7fafc;
  padding: 1rem;
  border-radius: 12px;
  max-width: 85%;
}

.message-user {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.message-user .bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  max-width: 85%;
}
```

#### 第五步：API 连接与测试

- **复用现有 API**：
  - `/api/ai/suggest_templates`
  - `/api/ai/generate_record_suggestion`
- **测试场景**：
  - a. 症状为空时的提示
  - b. 推荐模板成功/失败
  - c. 智能诊断成功/失败
  - d. 数据应用到病历表单

---

## 四、验收标准

### 4.1 功能验收

- ✅ 点击"AI 助手"按钮，对话框从右侧滑入
- ✅ 病历编辑框显示渐变边框动画
- ✅ AI 发送欢迎消息，显示两个选项按钮
- ✅ 症状为空时，AI 提示先填写症状
- ✅ 智能推荐模板：返回推荐结果，显示模板名称和预览
- ✅ 智能诊断建议：返回诊断和治疗方案
- ✅ 点击"应用"后，数据正确填入病历编辑框
- ✅ 关闭对话框，渐变边框消失

### 4.2 UI/UX 验收

- ✅ 对话框宽度 400px，高度自适应
- ✅ 消息滚动流畅，最新消息自动滚动到底部
- ✅ 按钮悬停效果明显
- ✅ 加载状态显示动画（旋转图标或骨架屏）
- ✅ 渐变边框动画流畅，3秒循环

### 4.3 性能验收

- ✅ API 调用失败时有错误提示
- ✅ 按钮防抖，避免重复点击
- ✅ 对话框打开/关闭动画流畅（60fps）

---

## 五、后续优化方向（V2.0）

1. **多轮对话**：支持连续追问和修改
2. **模板对比**：推荐多个模板，让用户选择
3. **历史记录**：保存对话历史
4. **语音输入**：支持语音描述症状
5. **AI 解释**：AI 解释诊断依据

---

## 六、风险与注意事项

1. **API 调用失败**：需要友好的错误提示
2. **症状为空判断**：前端做双重校验（按钮点击前 + 发送请求前）
3. **数据覆盖**：确保不会丢失用户已填写的数据
4. **性能**：对话框频繁开关不影响性能
5. **移动端适配**：400px 宽度在小屏幕上需要适配

---

**文档结束**

