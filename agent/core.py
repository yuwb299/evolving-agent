"""
Agent 核心进化循环
"""
import json
import os
import subprocess
import time
from agent.models import ModelClient
from agent.coder import Coder
from agent.memory import Memory
from config import EVOLUTION_CONFIG, TARGET_DIR


class EvolvingAgent:
    """自我进化Agent"""

    def __init__(self, goal: str):
        self.goal = goal
        self.model = ModelClient()
        self.coder = Coder()
        self.memory = Memory()
        self.iteration = self.memory.iteration_count
        self.config = EVOLUTION_CONFIG

    def evolve_once(self) -> dict:
        """执行一次进化迭代"""
        self.iteration += 1
        print(f"\n{'='*60}")
        print(f"🧬 迭代 #{self.iteration} | {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # Step 1: 收集上下文
        print("📖 [1/6] 读取当前代码状态...")
        code_context = self.coder.get_code_context()
        memory_summary = self.memory.get_summary()

        # Step 2: 规划
        print("🎯 [2/6] 规划下一步...")
        plan = self.model.plan(
            context=f"## 经验记忆\n{memory_summary}\n\n## 当前代码\n{code_context}",
            goal=self.goal,
        )
        print(f"   规划结果:\n{plan[:300]}...\n")

        # Step 3: 解析规划，确定要写的文件
        print("🔧 [3/6] 生成代码...")
        files_to_write = self._parse_plan_to_files(plan, code_context)

        if not files_to_write:
            print("   ⚠️ 无法解析出代码变更，重试...")
            self.memory.record(self.iteration, plan, "解析失败", "无法提取代码", False)
            return {"success": False, "reason": "无法解析代码变更"}

        # Step 4: 写代码
        for filename, content in files_to_write.items():
            print(f"   ✏️ 写入: {filename}")
            self.coder.write_file(filename, content)

        # Step 5: 生成测试并验证
        print("✅ [4/6] 生成测试并验证...")
        for filename in files_to_write:
            if filename.endswith(".py") and not filename.startswith("test_"):
                existing = self.coder.read_all_files().get(filename, "")
                test_code = self.model.generate_test(existing, filename)
                test_filename = f"test_{filename}"
                self.coder.write_file(test_filename, test_code)
                print(f"   📝 生成测试: {test_filename}")

        # Step 6: 运行测试
        print("🧪 [5/6] 运行测试...")
        success, output = self.coder.run_tests()
        print(f"   {'✅ 测试通过！' if success else '❌ 测试失败'}")
        if not success:
            print(f"   输出: {output[:300]}")

        # Step 7: 记录结果
        print(f"🧠 [6/6] 记录经验...")
        self.memory.record(
            iteration=self.iteration,
            plan=plan[:500],
            action=json.dumps(list(files_to_write.keys())),
            result="测试通过" if success else f"测试失败: {output[:300]}",
            success=success,
            details=output[:1000],
        )

        if success:
            # Git 提交
            self._git_commit(f"迭代#{self.iteration}: {plan[:100]}")
            print(f"   📦 Git 已提交")
        else:
            # 回滚代码变更
            self._git_rollback()
            print(f"   🔄 已回滚代码变更")

        return {
            "iteration": self.iteration,
            "success": success,
            "plan": plan[:300],
            "output": output[:500],
        }

    def run(self):
        """运行进化循环直到目标达成或达到最大迭代"""
        print(f"🧬 启动自我进化Agent")
        print(f"📋 目标: {self.goal}")
        print(f"🔄 最大迭代: {self.config['max_iterations']}次")
        print(f"⏰ 迭代间隔: {self.config['interval_hours']}小时")
        print()

        while self.iteration < self.config["max_iterations"]:
            result = self.evolve_once()

            # 检查是否完成
            if result.get("success"):
                completion = self._check_completion()
                if completion >= 1.0:
                    print(f"\n🎉 目标达成！共迭代 {self.iteration} 次")
                    self._git_commit(f"🎉 目标达成！迭代#{self.iteration}")
                    return True

            # 等待下一次迭代
            wait_seconds = self.config["interval_hours"] * 3600
            next_time = time.strftime("%H:%M:%S", time.gmtime(wait_seconds))
            print(f"\n⏳ 等待 {self.config['interval_hours']}小时 后进行下一次迭代（{next_time}）...")
            time.sleep(wait_seconds)

        print(f"\n⚠️ 达到最大迭代次数 ({self.config['max_iterations']})，停止进化")
        return False

    def run_single(self):
        """只运行一次迭代（用于测试）"""
        return self.evolve_once()

    def _parse_plan_to_files(self, plan: str, context: str) -> dict:
        """从规划中提取要写的文件"""
        # 让模型直接生成代码
        code_response = self.model.code(
            instruction=f"根据规划实现下一步:\n{plan}\n\n目标: {self.goal}",
            existing_code=context if context and "为空" not in context else "# 空项目，从零开始",
        )

        # 尝试解析出文件名和代码
        # 简单策略：如果是第一个文件，命名为 calculator.py
        files = {}
        if self.iteration <= 1 or "为空" in context:
            files["calculator.py"] = code_response
        else:
            # 后续迭代，让模型决定写哪个文件
            files["calculator.py"] = code_response

        return files

    def _check_completion(self) -> float:
        """检查目标完成度"""
        prompt = f"""评估以下科学计算器代码的完成度。

目标功能：
- 基础运算（加减乘除）
- 三角函数（sin, cos, tan）
- 对数运算（log, ln）
- 幂运算和开方
- 括号支持
- 错误处理

当前代码：
{self.coder.get_code_context()}

请只输出一个0到1之间的小数表示完成度。"""
        result = self.model.chat([
            {"role": "system", "content": "你只输出一个小数，不要其他内容。"},
            {"role": "user", "content": prompt},
        ])
        try:
            return float(result.strip())
        except:
            return 0.0

    def _git_commit(self, message: str):
        """Git 提交"""
        try:
            subprocess.run(["git", "add", "-A"], cwd=TARGET_DIR, capture_output=True)
            subprocess.run(["git", "commit", "-m", message], cwd=TARGET_DIR, capture_output=True)
        except:
            pass

    def _git_rollback(self):
        """Git 回滚"""
        try:
            subprocess.run(["git", "checkout", "--", "."], cwd=TARGET_DIR, capture_output=True)
        except:
            pass
