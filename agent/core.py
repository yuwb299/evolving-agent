"""
Agent 核心进化循环 v2
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

        # Step 2: 规划 - 让模型直接输出要写的代码
        print("🎯 [2/6] 规划并生成代码...")
        full_prompt = f"""## 目标
{self.goal}

## 经验记忆
{memory_summary}

## 当前代码
{code_context}

## 任务
请直接输出一个完整的 calculator.py 文件，实现科学计算器的功能。
要求：
1. 使用 import math
2. 实现 ScientificCalculator 类
3. 包含：加减乘除、三角函数(sin/cos/tan)、对数(log/ln)、幂运算、开方、阶乘
4. 支持链式调用（记录上次结果）
5. 支持内存功能（store/recall/clear）
6. 完善的错误处理（除零、负数开方等）
7. 所有方法返回 float
8. 只输出纯Python代码，不要任何解释文字"""

        source_code = self.model.chat([
            {"role": "system", "content": "你是一个Python程序员。只输出纯代码，不要markdown包裹，不要解释。"},
            {"role": "user", "content": full_prompt},
        ], temperature=0.1)

        # Step 3: 写入源码
        print("🔧 [3/6] 写入 calculator.py ...")
        self.coder.write_file("calculator.py", source_code)

        # 验证代码能被 import
        success, output = self.coder.run_file("calculator.py")
        if not success and "SyntaxError" in output:
            print(f"   ❌ 语法错误，尝试修复...")
            # 让模型修复
            fix_prompt = f"以下代码有语法错误，请修复并输出完整代码：\n{output}\n\n原始代码：\n{source_code}"
            fixed = self.model.chat([
                {"role": "system", "content": "只输出修复后的纯Python代码"},
                {"role": "user", "content": fix_prompt},
            ], temperature=0.1)
            self.coder.write_file("calculator.py", fixed)

        # Step 4: 生成测试
        print("✅ [4/6] 生成测试...")
        current_code = self.coder.read_all_files().get("calculator.py", "")
        test_code = self.model.generate_test(current_code, "calculator.py")
        self.coder.write_file("test_calculator.py", test_code)

        # Step 5: 运行测试
        print("🧪 [5/6] 运行测试...")
        success, output = self.coder.run_tests()
        print(f"   {'✅ 测试通过！' if success else '❌ 测试失败'}")
        if not success:
            print(f"   {output[:400]}")

        # Step 6: 记录经验
        print(f"🧠 [6/6] 记录经验...")
        self.memory.record(
            iteration=self.iteration,
            plan="生成科学计算器代码+测试",
            action="calculator.py + test_calculator.py",
            result="测试通过" if success else f"测试失败: {output[:300]}",
            success=success,
            details=output[:1000],
        )

        if success:
            self._git_commit(f"迭代#{self.iteration}: {'测试通过' if success else '测试失败'}")
            print(f"   📦 Git 已提交")
        else:
            self._git_rollback()
            print(f"   🔄 已回滚")

        return {
            "iteration": self.iteration,
            "success": success,
            "output": output[:500],
        }

    def run(self):
        """运行进化循环"""
        print(f"🧬 启动自我进化Agent")
        print(f"📋 目标: {self.goal}")
        print(f"🔄 最大迭代: {self.config['max_iterations']}次")
        print(f"⏰ 迭代间隔: {self.config['interval_hours']}小时\n")

        while self.iteration < self.config["max_iterations"]:
            result = self.evolve_once()

            if result.get("success"):
                completion = self._check_completion()
                if completion >= 0.9:
                    print(f"\n🎉 目标达成！共迭代 {self.iteration} 次")
                    self._git_commit(f"🎉 目标达成！迭代#{self.iteration}")
                    return True

            wait_seconds = self.config["interval_hours"] * 3600
            print(f"\n⏳ 等待 {self.config['interval_hours']}小时后下一次迭代...")
            time.sleep(wait_seconds)

        print(f"\n⚠️ 达到最大迭代次数 ({self.config['max_iterations']})")
        return False

    def run_single(self):
        """只运行一次迭代"""
        return self.evolve_once()

    def _check_completion(self) -> float:
        """检查目标完成度"""
        code_context = self.coder.get_code_context()
        result = self.model.chat([
            {"role": "system", "content": "只输出0-1之间的小数。"},
            {"role": "user", "content": f"评估科学计算器完成度(0-1)：\n{code_context}"},
        ], temperature=0.0)
        try:
            return float(result.strip())
        except:
            return 0.0

    def _git_commit(self, message: str):
        try:
            subprocess.run(["git", "add", "-A"], cwd=TARGET_DIR, capture_output=True)
            subprocess.run(["git", "commit", "-m", message], cwd=TARGET_DIR, capture_output=True)
        except:
            pass

    def _git_rollback(self):
        try:
            subprocess.run(["git", "checkout", "--", "."], cwd=TARGET_DIR, capture_output=True)
        except:
            pass
