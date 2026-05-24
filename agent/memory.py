"""
经验记忆模块 - 记录每次进化的成功/失败经验
"""
import json
import os
import time
from config import MEMORY_DIR


class Memory:
    """进化记忆系统"""

    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.log_file = os.path.join(MEMORY_DIR, "evolution_log.json")
        self.experiences = self._load()

    def _load(self) -> list:
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.log_file, "w") as f:
            json.dump(self.experiences, f, ensure_ascii=False, indent=2)

    def record(self, iteration: int, plan: str, action: str, result: str, success: bool, details: str = ""):
        """记录一次进化经验"""
        entry = {
            "iteration": iteration,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "plan": plan[:500],
            "action": action[:500],
            "result": result[:500],
            "success": success,
            "details": details[:1000],
        }
        self.experiences.append(entry)
        self._save()
        return entry

    def get_successes(self, limit: int = 10) -> list:
        """获取最近的成功经验"""
        return [e for e in self.experiences if e["success"]][-limit:]

    def get_failures(self, limit: int = 10) -> list:
        """获取最近的失败经验"""
        return [e for e in self.experiences if not e["success"]][-limit:]

    def get_summary(self) -> str:
        """生成记忆摘要供Agent参考"""
        if not self.experiences:
            return "（暂无进化经验）"

        total = len(self.experiences)
        successes = len([e for e in self.experiences if e["success"]])
        recent = self.experiences[-5:]

        summary = f"已进化 {total} 轮，成功 {successes} 次，失败 {total - successes} 次\n\n"
        summary += "最近5轮经验：\n"
        for e in recent:
            status = "✅" if e["success"] else "❌"
            summary += f"  {status} 迭代{e['iteration']}: {e['plan'][:100]} → {e['result'][:100]}\n"
        return summary

    @property
    def iteration_count(self) -> int:
        return len(self.experiences)
