<div align="center">

# 🔮 AI 运势预测

**温暖、有趣、有智慧 — 基于大模型的个性化运势解读，不仅仅是算命。**<br/>
今日运势卡片 · 年度详细解读 · 两人合盘分析 · 精美分享图片

<p>
<a href="https://github.com/luckysun001/ai-fortune-teller/actions/workflows/ci.yml"><img src="https://github.com/luckysun001/ai-fortune-teller/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
<a href="#"><img src="https://img.shields.io/badge/Status-Beta-F97316?style=for-the-badge" alt="Status"></a>
<a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
<a href="#"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"></a>
</p>

<p>
<a href="#-功能特性"><kbd> &nbsp; ✨ 功能特性 &nbsp; </kbd></a>
<a href="#-技术架构"><kbd> &nbsp; 🏗️ 技术架构 &nbsp; </kbd></a>
<a href="#-快速开始"><kbd> &nbsp; 🚀 快速开始 &nbsp; </kbd></a>
</p>

</div>

---

## ✨ 功能特性

### 📅 三种运势解读

- **今日运势卡片** — 每天一句暖心提醒，幸运色、幸运数字、今日小目标
- **年度运势解读** — 1000 字详细分析，覆盖事业、感情、财运、健康四大维度
- **两人合盘分析** — 情侣、夫妻、合伙人、朋友关系深度匹配分析

### 🎨 用户体验

- **精美 Web 界面** — Streamlit 打造，现代化设计，好看又好用
- **流式输出** — 边生成边显示，不用长时间等待
- **分享图片生成** — 一键生成精美卡片，直接发朋友圈
- **命令行版本** — 高手可以直接在终端调用

### 🛡️ 生产级保障

- **智能缓存** — LRU 缓存，相同输入不重复调用 API，省费用又快
- **自动重试** — 指数退避算法，网络不稳定也不怕
- **内容安全** — 敏感词自动过滤，确保输出合规
- **Mock 模式** — 无 API Key 时自动使用模拟数据，方便开发测试

---

## 🏗️ 技术架构

### 核心技术栈

| 层级 | 技术选型 | 职责 |
|---|---|---|
| **前端界面** | Streamlit | Web UI、交互、渲染、图片生成 |
| **编排层** | Python | 流程控制、Prompt 管理、结果解析 |
| **LLM 适配层** | LangChain + LangChain-OpenAI | 大模型调用、统一接口 |
| **缓存层** | LRU Cache（内置） | 响应缓存、减少 API 调用 |
| **配置层** | Python-dotenv | 环境变量管理 |
| **图片层** | Pillow | 分享卡片图片生成 |

### 工作原理

```text
用户输入
    │
    ├─► 配置加载 + 参数校验
    │
    ├─► 查询缓存 ──► 命中? ──► 直接返回结果
    │                   │
    │               未命中
    │                   │
    └───────────────────┘
                        │
                        ▼
                加载对应 Prompt 模板
                        │
                        ▼
                注入用户数据 + 系统提示
                        │
                        ▼
                LLM API 调用（带重试）
                        │
                        ▼
                解析结构化输出
                        │
                        ▼
                写入缓存
                        │
                        ▼
                格式化 + 生成分享图
                        │
                        ▼
                    返回给用户
```

---

## 📁 项目结构

```text
ai-fortune-teller/
├── app.py                      # Web 主界面（流式输出 + 分享图）
├── cli.py                      # 命令行版本
├── requirements.txt            # 依赖清单
├── .env.example                # 环境变量示例
├── .gitignore
├── Makefile                    # 常用命令封装
├── Dockerfile                  # Docker 容器配置
├── README.md
├── LICENSE
│
├── prompts/                    # Prompt 模板
│   ├── fortune_reading.md      # 年度运势（基础版）
│   ├── fortune_reading_v2.md   # 年度运势（优化版）
│   ├── daily_fortune.md        # 今日运势卡片
│   └── relation_reading.md     # 两人合盘分析
│
├── backend/                    # 后端核心模块
│   ├── __init__.py
│   ├── config.py               # 配置管理（环境变量 + 默认值）
│   ├── fortune_teller.py       # 核心业务逻辑（v1）
│   ├── fortune_teller_v2.py    # 核心业务逻辑（v2，含缓存/重试/限流/审核）
│   ├── share_image.py          # 分享图片生成器（v1）
│   ├── share_image_v2.py       # 分享图片生成器（v2）
│   ├── logger.py               # 日志工具
│   ├── utils.py                # 通用工具函数
│   └── test_tools.py           # 工具测试脚本
│
├── docs/
│   └── DEVELOPMENT.md          # 开发文档
│
└── tests/                      # 单元测试
    ├── __init__.py
    ├── test_core.py            # 核心逻辑测试
    ├── test_fortune_v2.py      # v2 业务逻辑测试
    └── test_share_image.py     # 分享图生成测试
```

> **注意**：README 之前版本声称的 `backend/cache.py`、`backend/retry.py`、`backend/exceptions.py`、`frontend/`、`examples/`、`assets/` 目录均不存在。缓存、重试、异常处理逻辑已内置于 `fortune_teller_v2.py` 中。

---

## 🚀 快速开始

### 前置要求

- Python 3.11+
- OpenAI API Key（或其他兼容的大模型 API）

### 安装运行

```bash
# 1. 进入项目目录
cd 04-production-apps/ai-fortune-teller

# 2. 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

### 启动 Web 界面

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

### 命令行使用

```bash
# 今日运势（模拟模式，不用 API Key）
python cli.py --daily --birth 1995-03-15

# 年度运势（真实调用）
python cli.py --fortune --birth 1995-03-15 --gender 男 --direction 事业

# 两人合盘分析
python cli.py --relation \
    --name-a 小明 --birth-a 1995-03-15 \
    --name-b 小红 --birth-b 1996-08-20 \
    --relation 情侣
```

### Python 代码调用

```python
from backend.fortune_teller_v2 import FortuneTeller

# 初始化
teller = FortuneTeller(api_key="YOUR_API_KEY")

# 今日运势
result = teller.get_daily_fortune("1995-03-15")

# 年度运势
result = teller.get_fortune("1995-03-15", "男", "事业")

# 两人合盘
result = teller.get_relation_reading(
    "小明", "1995-03-15",
    "小红", "1996-08-20",
    "情侣"
)

print(result)
```

---

## 🎯 设计理念

### 温暖，不是迷信

- 拒绝危言耸听的"克夫"、"破财"等封建话术
- 强调积极心理暗示，给人力量和希望
- 把传统命理智慧转化为现代心理引导

### 个性化，不是模板

- 根据生日、性别、关注方向动态调整
- 每个人的解读都是独一无二的
- 语言风格接地气，不说空话套话

### 有用，不仅仅是好玩

- 给出具体可行的建议
- 帮助用户反思和成长
- 成为更好的自己的工具

---

## 🧪 运行测试

```bash
# 单元测试
pytest tests/ -v

# 覆盖率
pytest tests/ --cov=backend
```

---

## 🔗 相关项目

本仓库是一个「**可直接跑起来的 LLM 应用样板**」——Prompt 工程、缓存、重试、内容安全一应俱全。

如果你更关心「**Agent 与 RAG 这类工程架构**」，推荐作者的另外两个开源项目：

> ### 🤖 [银行审计多智能体平台（bank-audit-agents）](https://github.com/luckysun001/bank-audit-agents)
> 多 Agent 分工协作 + 编排器 + 审计流水线。
>
> ### 🔍 [银行审计 RAG 系统（audit-rag）](https://github.com/luckysun001/audit-rag)
> 向量检索 + 生成，把知识库接进大模型。

---

## 📝 开发计划

- [ ] 补充更多测试用例（share_image_v2、app.py 界面逻辑）
- [ ] 支持更多模型（Claude、Gemini、通义千问、豆包）
- [ ] 历史记录保存
- [ ] 用户偏好学习
- [ ] API 服务（FastAPI）
- [ ] 拆分 `fortune_teller_v2.py` 为独立模块（cache.py / retry.py / exceptions.py）

---

## 📄 许可证

MIT License - 随便用，可以商用，可以卖钱。
