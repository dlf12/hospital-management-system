"""AI 服务封装：统一处理大模型调用与模板推荐逻辑。"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - openai 非必装
    OpenAI = None  # type: ignore

# 从配置文件导入
from config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL


def _get_llm_client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError("未安装 openai 库，请执行 `pip install openai`.")

    if not LLM_API_KEY or not LLM_API_KEY.strip():
        raise RuntimeError(
            f"未配置 LLM_API_KEY 或 OPENAI_API_KEY，无法调用大模型。\n"
            f"当前值: '{LLM_API_KEY}'"
        )
    if not LLM_BASE_URL or not LLM_BASE_URL.strip():
        raise RuntimeError(f"未配置 LLM_BASE_URL，无法调用大模型。当前值: '{LLM_BASE_URL}'")
    if not LLM_MODEL or not LLM_MODEL.strip():
        raise RuntimeError(f"未配置 LLM_MODEL 或 OPENAI_MODEL，无法调用大模型。当前值: '{LLM_MODEL}'")

    return OpenAI(api_key=LLM_API_KEY.strip(), base_url=LLM_BASE_URL.strip())


def generate_record_suggestion(
    symptom: str,
    medical_history: Optional[str] = None,
    allergy_history: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
) -> Dict[str, str]:
    """根据症状生成诊断与治疗方案建议。"""

    if not symptom:
        return {
            "diagnosis": "",
            "treatment_plan": "",
            "message": "症状信息为空，无法生成建议"
        }

    try:
        client = _get_llm_client()
    except RuntimeError as exc:  # 未配置或未安装
        return {
            "diagnosis": "",
            "treatment_plan": "",
            "message": str(exc)
        }

    prompt = f"""
你是一名资深临床医生助手，请基于以下信息给出诊断与治疗方案建议。

输出要求：
1. 使用简体中文。
2. 返回 JSON 格式，字段包含 diagnosis（诊断建议）与 treatment_plan（治疗方案建议），不要额外字段。
3. 内容需专业、清晰，可落地执行。

患者信息：
- 症状：{symptom}
- 既往病史：{medical_history or '未提供'}
- 过敏史：{allergy_history or '未提供'}
- 年龄：{age if age is not None else '未提供'}
- 性别：{gender or '未提供'}
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是专业且谨慎的临床医生助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=800,
        )
    except Exception as exc:  # pragma: no cover - 网络/鉴权错误
        return {
            "diagnosis": "",
            "treatment_plan": "",
            "message": f"大模型调用失败：{exc}"
        }

    content = response.choices[0].message.content.strip() if response.choices else ""

    try:
        data = json.loads(content)
        diagnosis = data.get("diagnosis", "").strip()
        plan = data.get("treatment_plan", "").strip()
    except json.JSONDecodeError:
        # 如果模型未返回合法 JSON，直接将原始文本塞入治疗方案，诊断留空
        diagnosis = ""
        plan = content

    return {
        "diagnosis": diagnosis,
        "treatment_plan": plan,
        "message": ""
    }


def suggest_templates_by_symptom(symptom: str, templates: List[Dict]) -> List[Dict]:
    """基于症状使用AI进行智能模板推荐。"""
    if not symptom:
        return []

    # 如果没有可用模板，直接返回空列表
    if not templates:
        return []

    try:
        client = _get_llm_client()
    except RuntimeError:
        # 如果无法获取AI客户端，降级为关键词匹配（保留原逻辑作为fallback）
        return _fallback_keyword_match(symptom, templates)

    # 构建模板列表供AI分析
    template_summaries = []
    for idx, tpl in enumerate(templates):
        content = tpl.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                content = {}

        summary = {
            "index": idx,
            "id": tpl.get("id"),
            "name": tpl.get("name", "未命名模板"),
            "symptom": content.get("symptom", "")[:100],  # 限制长度
            "diagnosis": content.get("diagnosis", "")[:100],
            "treatment_plan": content.get("treatment_plan", "")[:100],
        }
        template_summaries.append(summary)

    # 构建AI prompt
    templates_text = "\n".join([
        f"{i+1}. 模板ID={t['id']}, 名称={t['name']}, 症状={t['symptom']}, 诊断={t['diagnosis']}"
        for i, t in enumerate(template_summaries)
    ])

    prompt = f"""
你是一名经验丰富的临床医生助手。请根据患者症状，从以下可用的病历模板中选择最相关的一个。

患者症状：
{symptom}

可用模板列表：
{templates_text}

要求：
1. 必须从上述模板中选择一个最相关的模板
2. 即使症状不完全匹配，也要选择相关度最高的那个
3. 返回JSON格式：{{"selected_template_id": 模板ID, "reason": "选择理由"}}
4. 不要返回其他内容，只返回JSON
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是专业的医疗助手，擅长分析症状并匹配最合适的病历模板。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=300,
        )
    except Exception:
        # AI调用失败，降级为关键词匹配
        return _fallback_keyword_match(symptom, templates)

    content = response.choices[0].message.content.strip() if response.choices else ""

    try:
        result = json.loads(content)
        selected_id = result.get("selected_template_id")
        reason = result.get("reason", "")

        # 找到选中的模板并返回
        for tpl in templates:
            if tpl.get("id") == selected_id:
                return [{
                    "id": tpl.get("id"),
                    "name": tpl.get("name"),
                    "reason": reason
                }]

        # 如果没找到，返回第一个模板作为兜底
        if templates:
            return [{
                "id": templates[0].get("id"),
                "name": templates[0].get("name"),
                "reason": "AI推荐"
            }]

    except json.JSONDecodeError:
        # JSON解析失败，降级为关键词匹配
        return _fallback_keyword_match(symptom, templates)

    return []


def _fallback_keyword_match(symptom: str, templates: List[Dict]) -> List[Dict]:
    """关键词匹配（作为AI调用失败时的降级方案）。"""
    if not symptom or not templates:
        return []

    symptom_lower = symptom.lower()
    suggestions: List[Dict] = []

    for tpl in templates:
        content = tpl.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                content = {"symptom": content}

        text_parts = [
            tpl.get("name", ""),
            content.get("symptom", ""),
            content.get("diagnosis", ""),
            content.get("treatment_plan", ""),
        ]
        merged_text = "\n".join(text_parts).lower()

        if not merged_text.strip():
            continue

        score = merged_text.count(symptom_lower)
        for token in symptom_lower.split():
            if token and token in merged_text:
                score += 1

        if score > 0:
            suggestions.append({
                "id": tpl.get("id"),
                "name": tpl.get("name"),
                "score": score,
            })

    suggestions.sort(key=lambda item: item["score"], reverse=True)
    return suggestions[:1] if suggestions else []


