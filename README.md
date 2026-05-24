# 🧬 Evolving Agent - 自我进化智能体

一个给定目标后自主进化实现目标的 AI Agent。

## 当前目标
**写一个科学计算器**（支持基础运算、三角函数、对数、幂运算等）

## 进化机制
- 每 4 小时自动迭代一次
- 每轮：自省 → 规划 → 编码 → 验证 → 提交/回滚 → 记忆
- 使用 DeepSeek V4 Pro 作为核心模型

## 项目结构
```
evolving-agent/
├── agent/
│   ├── __init__.py
│   ├── core.py          # Agent 核心循环
│   ├── models.py        # 模型调用封装
│   ├── planner.py       # 目标分解与规划
│   ├── coder.py         # 代码读写执行
│   ├── verifier.py      # 测试验证
│   └── memory.py        # 经验记忆
├── target/              # 目标项目（科学计算器）
│   └── ...
├── memory/              # 进化记忆存储
├── config.py            # 配置
├── run.py               # 主入口
└── README.md
```

## 进化日志
- 实时记录每次迭代的结果、代码变更、测试结果

## 运行
```bash
python run.py --goal "写一个科学计算器"
```
