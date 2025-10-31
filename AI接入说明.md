# 医院病历系统 AI 接入说明

> 适用对象：对前后端开发只有部分了解的同学。

本文介绍为了实现“大模型根据症状给出诊断与治疗方案建议，同时智能推荐模板”这一目标，我们在项目里做了哪些改动、它们分别位于哪里、如何协同工作，并告诉你要想顺利使用这些能力，需要准备哪些信息。

---

## 1. 新增了哪些功能模块？

### 1.1 后端（Flask）

| 模块/文件 | 作用 | 代码入口 |
| --- | --- | --- |
| `backend/ai_service.py` | 封装大模型调用逻辑，提供两个函数：<br>• `generate_record_suggestion()`：根据症状生成诊断和治疗方案建议。<br>• `suggest_templates_by_symptom()`：根据症状筛选/推荐模板。 | 在 `backend/app.py` 中通过 `from ai_service import ...` 导入并调用 |
| `backend/app.py` | • 医疗记录模型新增 `symptom` 字段。<br>• 新增 AI 接口：`/api/ai/generate_record_suggestion` 与 `/api/ai/suggest_templates`。<br>• 原有病历相关接口同步支持 `symptom` 字段，并在保存模板时记录症状信息。 | `app.py` 中的路由函数 |
| 数据库迁移 | 新增 `symptom` 列（Alembic 迁移文件）。 | `backend/migrations/versions/f2b2d7d4a7c8_add_symptom_to_medical_records.py` |

### 1.2 前端（Vue 3）

| 文件 | 作用 |
| --- | --- |
| `frontend/src/components/DepartmentView.vue` | 科室病历管理界面：<br>• 新增“症状”输入框（位于诊断上方）。<br>• 在病历编辑窗口增加“AI 推荐模板”“AI 生成建议”按钮。<br>• 当调用成功时自动填充诊断和治疗方案、展示推荐模板按钮。 |
| `frontend/src/components/TemplateManager.vue` | 模板管理界面：模板内容现在包含 `symptom` 字段，表单和预览界面都支持症状信息。 |
| `frontend/src/components/PatientManager.vue` | 备用的病历管理界面，同步支持“症状/既往病史/过敏史”以及模板保存。 |
| 全局样式 `frontend/src/style.css` | 保证所有输入框都是浅色底、深色字，方便阅读。 |

这些模块之间的流程如下：

1. 用户在病历窗口先填写“症状”。
2. 点击“AI 生成建议”时，前端调用 `/api/ai/generate_record_suggestion`，后端转发给大模型，返回诊断与治疗方案文本，再自动填入表单。
3. 点击“AI 推荐模板”时，前端调用 `/api/ai/suggest_templates`，后端用症状在现有模板里做匹配，返回推荐列表，用户可一键套用。
4. 用户确认内容后，可保存病历、或将病历导出为模板（此时模板中也会记录症状）。

---

## 2. 我需要准备哪些信息？

要让大模型能力真正生效，需要准备 **API 访问凭据** 并配置在后端运行环境中。项目当前使用了与 OpenAI 兼容的 SDK，因此无论你使用硅基流动（DeepSeek R1）、OpenAI、Azure OpenAI 还是其他兼容厂商，只要按下列方式提供接口信息即可。

### 2.1 安装依赖

```bash
cd backend
pip install openai
```

### 2.2 配置环境变量

| 变量名 | 说明 | 示例（硅基流动 + DeepSeek R1） |
| --- | --- | --- |
| `LLM_BASE_URL` | 模型服务的 Base URL | `https://api.siliconflow.cn/v1` |
| `LLM_API_KEY` | API 密钥（必要） | `sk-xxxxxxxxxxxxxxxx` |
| `LLM_MODEL` | 模型标识 | `deepseek-ai/DeepSeek-R1` |

> 兼容性说明：如果你已经在其他场景使用过 `OPENAI_API_KEY` 或 `OPENAI_MODEL`，本项目也会自动读取它们作为默认值。

#### Windows PowerShell（当前窗口临时生效）

```powershell
$env:LLM_BASE_URL = "https://api.siliconflow.cn/v1"
$env:LLM_MODEL = "deepseek-ai/DeepSeek-R1"
$env:LLM_API_KEY = "sk-你的密钥"
```

#### Windows 持久化（对新开的 PowerShell 生效）

```powershell
setx LLM_BASE_URL "https://api.siliconflow.cn/v1"
setx LLM_MODEL "deepseek-ai/DeepSeek-R1"
setx LLM_API_KEY "sk-你的密钥"
```

#### macOS / Linux

```bash
export LLM_BASE_URL="https://api.siliconflow.cn/v1"
export LLM_MODEL="deepseek-ai/DeepSeek-R1"
export LLM_API_KEY="sk-你的密钥"
```

> **如果你使用其他厂商**：只需把上面的地址/模型/密钥替换为对应值即可，无需改动代码。若厂商不兼容 OpenAI 接口，可以在 `backend/ai_service.py` 内调整请求逻辑。

### 2.3 数据库迁移

新字段生效需要执行一次 Alembic 迁移：

```bash
cd backend
python -m flask db upgrade
```

执行完成后，`medical_records` 表会新增 `symptom` 列。如果你是第一次部署，还会保留既往迁移带来的 `medical_history`、`allergy_history` 列。

---

## 3. 如何使用新的 AI 功能？

1. 登录系统，进入任意科室。
2. 打开某个病人的“病历编辑”窗口，在表单顶部填写“症状”。
3. 点击：
   - **AI 生成建议**：等待按钮显示“生成中...”，完成后会自动填入诊断和治疗方案字段。
   - **AI 推荐模板**：若匹配到模板，会显示若干按钮，点击即可快速套用模板内容。
4. 根据需要再做人工调整，最后点击“添加病历”或“更新病历”。

如需将当前病历保存为模板，可继续使用右上角的“📤 导出为模板”。

---

## 4. 常见问题（FAQ）

**Q1：我没有配置 LLM_API_KEY/LLM_BASE_URL，会发生什么？**  
接口会返回错误提示（如“症状不能为空”或“未配置 LLM_API_KEY...”），前端会弹窗提醒，病历数据不会被修改。

**Q2：旧模板没有症状字段，还能用吗？**  
可以，但 AI 推荐模板可能匹配不到它们；如果希望兼容，建议重新编辑模板，补充症状信息并保存。

**Q3：需要上网吗？**  
大模型调用需要访问外部 API。如果在内网/无外网环境，可以改用部署在内网的大模型服务，或者在 `ai_service.py` 中切换到离线推理方案。

**Q4：能否扩展更复杂的检索算法？**  
可以。`suggest_templates_by_symptom()` 里目前是关键词匹配，你可以替换为向量检索（如接入 Embedding + Faiss），只需保持函数入参/出参结构一致，前端无需改动。

---

## 5. 小结

完成以上配置后，你就拥有了：

- 病历记录新增「症状」字段，与诊断、治疗方案并列管理；
- 通过大模型，一键生成诊断与治疗方案参考；
- 结合症状，智能推荐已有模板，提高录入效率；
- 模板体系同步支持症状等丰富信息，为未来的检索与分析奠定基础。

如果后续需要扩展更多 AI 能力（例如自动生成随访计划、药品用量校验等），可以在现有 `ai_service.py` 里继续新增函数，并在 `backend/app.py` 中暴露新的路由即可。前端也只需按照同样的方式添加按钮与处理逻辑。

祝使用愉快！


