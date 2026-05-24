"""
Evolving Agent - 主入口
用法：
  python run.py --goal "写一个科学计算器"          # 持续进化模式（每4小时一次）
  python run.py --goal "写一个科学计算器" --once    # 只跑一次迭代
  python run.py --goal "写一个科学计算器" --interval 1  # 每1小时迭代一次
"""
import argparse
import sys

from agent.core import EvolvingAgent


def main():
    parser = argparse.ArgumentParser(description="🧬 自我进化Agent")
    parser.add_argument("--goal", type=str, required=True, help="进化目标")
    parser.add_argument("--once", action="store_true", help="只运行一次迭代")
    parser.add_argument("--interval", type=int, default=4, help="迭代间隔（小时）")

    args = parser.parse_args()

    # 更新配置
    from config import EVOLUTION_CONFIG
    EVOLUTION_CONFIG["interval_hours"] = args.interval

    agent = EvolvingAgent(goal=args.goal)

    if args.once:
        print("🔄 单次迭代模式")
        result = agent.run_single()
        print(f"\n结果: {'✅ 成功' if result['success'] else '❌ 失败'}")
        print(f"详情: {result.get('output', '')[:500]}")
    else:
        print("🔄 持续进化模式")
        agent.run()


if __name__ == "__main__":
    main()
