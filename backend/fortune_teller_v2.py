#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI 运势预测核心类 - 优化版
新增：重试、缓存、日志、错误处理、多模型支持
"""

import os
import time
import datetime
from typing import Dict, Optional, List

# 先尝试导入 LangChain，不可用也没关系
LANGCHAIN_AVAILABLE = False
ChatOpenAI = None
HumanMessage = None
SystemMessage = None

try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

from .config import MODEL_CONFIG, PROMPT_VERSIONS, SAFETY_CONFIG
from .logger import logger, request_logger
from .utils import (
    retry,
    timing,
    cached,
    APITimeoutException,
    APIKeyInvalidException,
    ContentSafetyException,
)


class FortuneTeller:
    """AI 运势预测核心类 - 生产级版本"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_profile: str = "default",
        prompt_version: str = "latest",
    ):
        """
        初始化运势预测器

        Args:
            api_key: API Key，如果不传会从环境变量读取
            model_profile: 模型配置名，参考 config.py 的 MODEL_CONFIG
            prompt_version: Prompt 版本，v1/v2/latest
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        self.model_profile = model_profile
        self.prompt_version = prompt_version
        self.config = MODEL_CONFIG[model_profile]

        # 加载 Prompt 模板
        self._load_prompts()

        # 初始化 LLM
        self.llm = self._init_llm()

        logger.info(
            f"✅ FortuneTeller 初始化完成 | "
            f"模型: {self.config['model']} | "
            f"Prompt: {prompt_version}"
        )

    def _load_prompts(self):
        """加载所有 Prompt 模板"""
        project_root = os.path.join(os.path.dirname(os.path.dirname(__file__)))

        self.prompts = {}

        for prompt_type, versions in PROMPT_VERSIONS.items():
            version_path = versions.get(self.prompt_version, versions["latest"])
            full_path = os.path.join(project_root, version_path)

            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    self.prompts[prompt_type] = f.read()
                logger.debug(f"📝 加载 Prompt: {prompt_type} -> {version_path}")
            else:
                logger.warning(f"⚠️  Prompt 文件不存在: {full_path}")

    def _init_llm(self) -> Optional:
        """初始化 LLM 客户端"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("⚠️  LangChain 未安装，只能用模拟模式")
            return None

        if not self.api_key:
            logger.warning("⚠️  没有设置 API Key，只能用模拟模式")
            return None

        try:
            return ChatOpenAI(
                model=self.config["model"],
                api_key=self.api_key,
                base_url=self.config["base_url"],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                timeout=self.config["timeout"],
            )
        except Exception as e:
            logger.error(f"❌ 初始化 LLM 失败: {e}")
            return None

    def _calculate_age(self, birth_date_str: str) -> int:
        """计算年龄"""
        try:
            birth = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d")
            now = datetime.datetime.now()
            return now.year - birth.year - ((now.month, now.day) < (birth.month, birth.day))
        except Exception:
            return 30  # 默认 30 岁

    def _check_content_safety(self, content: str) -> bool:
        """简单的内容安全检查"""
        if not SAFETY_CONFIG["enable_moderation"]:
            return True

        for keyword in SAFETY_CONFIG["blocked_keywords"]:
            if keyword in content:
                return False

        return True

    @retry(max_attempts=3, delay_seconds=1.0, backoff=2.0)
    @timing
    def _call_llm(self, prompt: str, request_type: str) -> str:
        """
        调用大模型（带重试和计时）

        Args:
            prompt: 完整的 Prompt
            request_type: 请求类型，用于日志

        Returns:
            模型返回的内容
        """
        start_time = time.time()
        success = False
        error_msg = None

        try:
            # 如果没有 LLM，返回模拟结果
            if self.llm is None:
                time.sleep(1)  # 模拟网络延迟
                result = self._get_mock_result(request_type)
                success = True
                return result

            # 真正调用 API
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            result = response.content

            # 内容安全检查
            if not self._check_content_safety(result):
                raise ContentSafetyException("输出内容包含敏感词，已拦截")

            success = True
            return result

        except Exception as e:
            error_msg = str(e)

            if "Invalid" in error_msg or "invalid" in error_msg or "401" in error_msg:
                raise APIKeyInvalidException("API Key 无效，请检查")
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                raise APITimeoutException("API 调用超时，请稍后重试")

            raise

        finally:
            latency_ms = (time.time() - start_time) * 1000
            request_logger.log_request(
                request_type=request_type,
                params={"model": self.config["model"]},
                model=self.config["model"],
                latency_ms=latency_ms,
                success=success,
                error=error_msg,
            )

    def _get_mock_result(self, request_type: str) -> str:
        """返回模拟结果，用于开发和测试"""
        mock_results = {
            "fortune": """
## 给你的第一印象

你是一个表面上看起来很冷静、很理性的人，但其实内心非常敏感，很在意别人的看法。
你不喜欢麻烦别人，什么事情都习惯自己扛着。

你给人的整体感觉是可靠、踏实，朋友遇到事情都愿意找你商量。
但是你有时候太追求完美了，对自己要求太高，反而容易累。

## 事业运详细解读

今年你的事业运整体是向上走的，特别是上半年，会有不错的机会出现。

### 整体趋势
这一年是「积累和准备」的一年，不要着急爆发。你现在做的每一件小事，未来都会成倍地回报你。
适合稳扎稳打，不适合冒进。如果有换工作或者创业的想法，建议下半年再考虑。

### 人际关系和贵人运
今年你的贵人运不错，特别是比你年长 5-10 岁的人，会给你很多有用的建议。
同事关系整体不错，但是要注意「少说多做」，不要参与办公室政治。
跟领导相处的时候，不要太拘谨，该表现的时候要勇敢表现。

### 需要注意的坑
1. 不要太相信「朋友介绍」的机会，特别是涉及到钱的时候，一定要自己调研清楚
2. 上半年不要轻易答应帮别人做担保，容易有口舌是非
3. 注意劳逸结合，不要为了工作把身体搞垮了

## 你需要特别注意的 3 件事

1. **健康方面** - 今年你的精力其实不如往年，不要硬撑。该休息就休息，该体检就体检。特别是颈椎和睡眠的问题，不要忽视。

2. **人际关系方面** - 今年你会遇到一些跟你三观不合的人，不要试图改变他们，也不要跟他们争论，保持距离就好。

3. **财务方面** - 今年有不错的财运，但是也有很多破财的机会。不要冲动消费，不要跟风投资。每个月强制存一点钱，年底你会感谢自己。

## 给你的专属建议

1. **心态上** - 不要太焦虑。20 多岁和 30 多岁本来就是用来试错的，走点弯路很正常。不要跟别人比，跟昨天的自己比就好。

2. **行动上** - 每周至少跟一个比你优秀的人聊聊天，可以是你的领导，可以是行业前辈。不要觉得不好意思，大部分人都很愿意分享。

3. **小习惯** - 每天花 10 分钟写日记，不用写很长，记录今天做了什么，有什么感悟。坚持半年，你会看到巨大的变化。

## 最后想对你说

我知道你最近有时候会觉得迷茫，会怀疑自己的选择是不是对的。
这很正常，每一个认真生活的人，都会有这样的时刻。

记住：
- 你不需要一开始就很厉害，但是你需要开始，才能变得很厉害。
- 不要怕走弯路，弯路也是路。
- 你已经做得很好了，继续往前走就好。

祝你好运 🍀
            """.strip(),

            "daily": """
## ✨ 今日运势：中吉

### 🔖 今日标签
适合思考 · 适合存钱 · 适合跟老朋友聊天 · 少说话多做事

### 🍀 幸运值
- **幸运色**：深蓝色
- **幸运数字**：7
- **幸运方位**：东北方
- **宜**：整理房间、学习新东西、给爸妈打电话
- **忌**：冲动消费、做重大决定、跟人吵架

### 💌 今日建议
今天的能量比较平和，适合做一些「积累型」的事情。
不用逼自己必须做出什么大成就，把手里的小事一件一件做好就很棒了。

如果今天遇到什么不开心的事，不要往心里去。
睡一觉，明天起来就都不是事了。

### 🎯 今日小目标
✅ 喝够 8 杯水
✅ 今天不熬夜，12 点前睡觉
✅ 夸奖一个人（可以是自己）
            """.strip(),

            "relation": """
## 关系整体能量

你们两个是「互补型」的关系，在一起的时候 1+1 > 2。
小明偏理性，做事情考虑周全，但是有时候太纠结；
小红偏感性，做事情凭直觉，但是有时候容易冲动。

刚好可以互相弥补对方的缺点。

整体匹配度：85 分，是很值得珍惜的一段关系。

## 你们的优势

1. **沟通顺畅** - 你们两个都是讲道理的人，有什么事说开了就好了，不会冷战。
2. **三观一致** - 在大是大非的问题上，你们的看法基本是一样的，这一点非常重要。
3. **互相欣赏** - 小明欣赏小红的活力和创造力，小红欣赏小明的稳重和靠谱。

## 需要注意的地方

1. **小明有时候太理性了**，遇到问题喜欢分析对错，但是女生有时候只是想要一个拥抱，想要被理解。下次遇到矛盾，先安抚情绪，再讲道理。

2. **小红有时候太冲动了**，生气的时候容易说狠话，说完自己又后悔。下次生气的时候，先深呼吸 10 秒，再说话。

3. **你们都太独立了**，什么事都习惯自己扛。其实两个人在一起，就是要互相麻烦的。偶尔示弱，偶尔依赖对方，感情会更好。

## 相处建议

给小明：
- 多夸夸她，女生是需要被肯定的
- 记住一些重要的日子，不是说要花多少钱，而是让她知道你在乎
- 有时候就算你觉得她错了，也不要当场指出来，回家再说

给小红：
- 他压力大的时候，不要逼他说话，安安静静陪着他就好
- 多看看他的付出，不要觉得都是理所当然
- 偶尔撒撒娇，比什么都管用

## 总结

你们是很合适的一对，遇到问题只要好好沟通，没有什么解决不了的。
好好珍惜彼此，祝你们越来越好 💕
            """.strip(),
        }

        return mock_results.get(request_type, "（模拟结果）")

    @cached
    def get_fortune(
        self,
        birth_date: str,
        gender: str,
        direction: str = "综合",
    ) -> str:
        """
        获取年度运势解读

        Args:
            birth_date: 出生日期，格式：YYYY-MM-DD
            gender: 性别："男" / "女"
            direction: 测算方向："综合" / "事业" / "感情" / "财运"

        Returns:
            运势解读结果
        """
        age = self._calculate_age(birth_date)

        logger.info(f"🔮 测算运势: {birth_date} ({age}岁) {gender} {direction}")

        prompt = self.prompts["fortune"].format(
            birth_date=birth_date,
            gender=gender,
            direction=direction,
            age=age,
        )

        return self._call_llm(prompt, request_type="fortune")

    @cached
    def get_daily_fortune(
        self,
        birth_date: str,
        today: Optional[str] = None,
    ) -> str:
        """获取今日运势"""
        if today is None:
            today = datetime.date.today().strftime("%Y-%m-%d")

        logger.info(f"📅 今日运势: {birth_date} @ {today}")

        prompt = self.prompts["daily"].format(
            birth_date=birth_date,
            today=today,
        )

        return self._call_llm(prompt, request_type="daily")

    @cached
    def get_relation_reading(
        self,
        person_a: str,
        birth_a: str,
        person_b: str,
        birth_b: str,
        relation_type: str = "情侣",
    ) -> str:
        """两人合盘分析"""
        logger.info(f"💑 合盘分析: {person_a} & {person_b} ({relation_type})")

        prompt = self.prompts["relation"].format(
            person_a=person_a,
            birth_a=birth_a,
            person_b=person_b,
            birth_b=birth_b,
            relation_type=relation_type,
        )

        return self._call_llm(prompt, request_type="relation")

    def get_stats(self) -> dict:
        """获取运行统计数据"""
        from .utils import cache
        return {
            "model_profile": self.model_profile,
            "model_config": self.config,
            "prompt_version": self.prompt_version,
            "requests": request_logger.get_stats(),
            "cache": cache.stats(),
        }

    def clear_cache(self):
        """清空缓存"""
        from .utils import cache
        cache.clear()
        logger.info("🗑️ 缓存已清空")


# 简单测试
if __name__ == "__main__":
    teller = FortuneTeller()

    print("\n" + "=" * 80)
    print("🧪 测试 - 模拟模式")
    print("=" * 80)

    print("\n📅 今日运势:")
    print("-" * 60)
    result = teller.get_daily_fortune("1995-03-15")
    print(result)

    print("\n\n🔮 年度运势:")
    print("-" * 60)
    result = teller.get_fortune("1995-03-15", "男", "事业")
    print(result)

    print("\n\n" + "=" * 80)
    print("📊 统计信息")
    print("=" * 80)
    import json
    print(json.dumps(teller.get_stats(), ensure_ascii=False, indent=2))
