## 1 目录结构

src/agentic_patterns/
├── reflection_pattern # 1 反射
│   └── reflection_agent.py
├── tool_pattern       # 2 工具调用
│   ├── tool.py     
│   └── tool_agent.py
├── planning_pattern   # 3 规划 （ReAct）
│   └── react_agent.py
├── multiagent_pattern # 4 多智能体
│   ├── agent.py
│   └── crew.py
└── utils
    ├── completions.py
    ├── extraction.py
    └── logging.py


## 2 问题

1 四个agent的概念
2 color使用
3 poetry的使用
4 切换成openai client