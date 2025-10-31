"""配置文件：集中管理环境变量和默认值"""

import os

# LLM 配置
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or "sk-otpswuzrwtijyrvfwyksxemjbpkiqnixcegbkldngmwlgaxr"
LLM_MODEL = os.environ.get("LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "deepseek-ai/DeepSeek-R1"

# 数据库配置
DATABASE_URI = os.environ.get("DATABASE_URI", "mysql+pymysql://root:123456@localhost:3306/hospital_db?charset=utf8mb4")

# JWT 配置
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")

