#!/bin/bash
# 每4小时自动进化 + 推送GitHub
cd /home/yuwb/.openclaw/workspace/evolving-agent

# 运行一次进化
/usr/bin/python3 run.py --goal "写一个科学计算器" --once 2>&1

# 推送 target 变更到 GitHub
cd /home/yuwb/.openclaw/workspace/evolving-agent
git add -A
git diff --cached --quiet || git commit -m "🧬 自动进化 $(date '+%Y-%m-%d %H:%M')"
git push origin master 2>&1
