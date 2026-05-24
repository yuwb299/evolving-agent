"""
模型调用封装 - DeepSeek V4 Pro
"""
import json
import requests
from config import MODEL_CONFIG, SYSTEM_PROMPT


class ModelClient:
    """统一的模型调用客户端"""

    def __init__(self):
        self.config = MODEL_CONFIG
        self.base_url = self.config["base_url"]
        self.api_key = self.config["api_key"]
        self.model = self.config["model"]

    def chat(self, messages: list, temperature: float = None) -> str:
        """调用模型进行对话"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.config["max_tokens"],
            "temperature": temperature or self.config["temperature"],
        }

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[模型调用失败: {e}]"

    def plan(self, context: str, goal: str) -> str:
        """规划下一步"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""## 当前上下文
{context}

## 目标
{goal}

## 任务
请分析当前代码状态，评估目标完成度（0-100%），然后规划下一步要做什么。
输出格式：
```
完成度: XX%
评估: （简要分析当前状态）
下一步: （具体要做的事情）
代码变更: （要写或改哪个文件，写什么内容）
```"""},
        ]
        return self.chat(messages, temperature=0.2)

    def code(self, instruction: str, existing_code: str = "") -> str:
        """根据指令生成代码"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n你只输出纯代码，不要用markdown代码块包裹。"},
            {"role": "user", "content": f"""## 现有代码
```
{existing_code}
```

## 指令
{instruction}

请输出完整的修改后的代码。"""},
        ]
        return self.chat(messages, temperature=0.1)

    def generate_test(self, source_code: str, filename: str) -> str:
        """为代码生成测试"""
        messages = [
            {"role": "system", "content": "你是一个测试工程师。输出纯Python测试代码，使用 pytest。"},
            {"role": "user", "content": f"""为以下代码生成测试用例：

文件: {filename}
```python
{source_code}
```

要求：
1. 使用 pytest 框架
2. 覆盖所有公开函数和主要功能
3. 包含正常情况和边界情况
4. 输出纯Python代码，不要markdown"""},
        ]
        return self.chat(messages, temperature=0.1)
