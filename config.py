"""
Evolving Agent 配置文件
"""
import os

# 模型配置 - DeepSeek V4 Pro
MODEL_CONFIG = {
    "provider": "deepseek",
    "model": "deepseek-chat",  # DeepSeek V4 Pro
    "base_url": "https://api.deepseek.com/v1",
    "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
    "max_tokens": 4096,
    "temperature": 0.3,  # 编码用低温，更稳定
}

# 进化配置
EVOLUTION_CONFIG = {
    "interval_hours": 4,           # 每4小时迭代一次
    "max_iterations": 100,         # 最大迭代次数
    "max_code_length": 50000,      # 单个文件最大字符数
    "test_timeout": 30,            # 测试超时（秒）
    "max_retries_per_iteration": 3,# 每轮最大重试
}

# 目标项目目录
TARGET_DIR = os.path.join(os.path.dirname(__file__), "target")

# 记忆目录
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")

# 系统提示
SYSTEM_PROMPT = """你是一个自我进化的AI编程Agent。你的任务是根据给定目标，自主编写、改进代码。

核心原则：
1. 每次只做一个小改动（原子提交）
2. 写代码的同时写测试
3. 如果测试失败，立即回滚
4. 记录每次成功和失败的经验
5. 代码要简洁、可读、有注释
"""
