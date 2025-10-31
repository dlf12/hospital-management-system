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
    """基于症状进行简单模板推荐（关键词匹配）。"""
    if not symptom:
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
        # 附加基于分词的粗略评分
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
    return suggestions[:5]


