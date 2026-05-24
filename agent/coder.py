"""
代码读写执行模块
"""
import os
import subprocess
import glob
from config import TARGET_DIR


class Coder:
    """代码读写器"""

    def __init__(self):
        os.makedirs(TARGET_DIR, exist_ok=True)

    def read_all_files(self) -> dict:
        """读取目标目录下所有代码文件"""
        files = {}
        for ext in ("*.py", "*.js", "*.html", "*.css", "*.json", "*.md"):
            for path in glob.glob(os.path.join(TARGET_DIR, "**", ext), recursive=True):
                rel = os.path.relpath(path, TARGET_DIR)
                with open(path, "r") as f:
                    files[rel] = f.read()
        return files

    def get_code_context(self) -> str:
        """生成代码上下文摘要"""
        files = self.read_all_files()
        if not files:
            return "（目标目录为空，还没有任何代码）"

        context = f"当前有 {len(files)} 个文件：\n\n"
        for name, content in files.items():
            lines = content.count("\n") + 1
            context += f"### {name} ({lines}行)\n```python\n{content}\n```\n\n"
        return context[:8000]  # 限制长度

    def write_file(self, filename: str, content: str) -> bool:
        """写文件到目标目录"""
        # 从模型输出中提取纯代码
        content = self._extract_code(content)

        filepath = os.path.join(TARGET_DIR, filename)
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else TARGET_DIR, exist_ok=True)

        with open(filepath, "w") as f:
            f.write(content)
        return True

    def run_tests(self) -> tuple[bool, str]:
        """运行测试，返回 (成功?, 输出)"""
        test_dir = TARGET_DIR
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", test_dir, "-v", "--tb=short", "-x"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output[-2000:]  # 限制输出长度
        except subprocess.TimeoutExpired:
            return False, "测试超时（30秒）"
        except Exception as e:
            return False, f"运行测试失败: {e}"

    def run_file(self, filename: str) -> tuple[bool, str]:
        """运行单个Python文件"""
        filepath = os.path.join(TARGET_DIR, filename)
        if not os.path.exists(filepath):
            return False, f"文件不存在: {filename}"

        try:
            result = subprocess.run(
                ["python3", filepath],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output[-1000:]
        except subprocess.TimeoutExpired:
            return False, "运行超时"
        except Exception as e:
            return False, str(e)

    def _extract_code(self, text: str) -> str:
        """从模型输出中提取纯代码（去掉markdown包裹）"""
        # 如果被 ```包裹，提取内容
        if "```" in text:
            lines = text.split("\n")
            in_block = False
            code_lines = []
            for line in lines:
                if line.strip().startswith("```"):
                    in_block = not in_block
                    continue
                if in_block:
                    code_lines.append(line)
            if code_lines:
                return "\n".join(code_lines)
        return text
