#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI 运势预测核心类 - v2.1 生产级版本
✅ 完整的类型提示
✅ 完善的错误处理
✅ 可观测性
✅ 内容安全
✅ 缓存
✅ 重试
"""

import os
import time
from typing import Optional, Dict, Any, Tuple

# 先尝试导入 LangChain
LANGCHAIN_AVAILABLE = False
ChatOpenAI = None
HumanMessage = None

try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

from .config import (
    MODEL_CONFIG,
    PROMPT_VERSIONS,
    SAFETY_CONFIG,
    TEXTS,
)
from .logger import logger, request_logger
from .utils import (
    retry,
    timing,
    cached,
    calculate_age,
    ContentModerator,
    APIKeyInvalidException,
    APITimeoutException,
    ContentSafetyException,
)


class FortuneTeller:
    """
    AI 运势预测核心类
    
    用法:
        >>> teller = FortuneTeller(api_key="your_key")
        >>> result = teller.get_fortune("1995-03-15", "男", "事业")
        >>> print(result)
    """
    
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
            model_profile: 模型配置名：default / gpt-3.5 / creative / conservative
            prompt_version: Prompt 版本：v1 / v2 / latest
        """
        # API Key 优先级：参数 > 环境变量
        self.api_key = (
            api_key
            or os.getenv("DEEPSEEK_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        
        self.model_profile = model_profile
        self.prompt_version = prompt_version
        self.config = MODEL_CONFIG[model_profile]
        
        # 初始化内容安全检查器
        self.moderator = ContentModerator(SAFETY_CONFIG["blocked_keywords"])
        
        # 加载 Prompt 模板
        self.prompts: Dict[str, str] = {}
        self._load_prompts()
        
        # 初始化 LLM 客户端
        self.llm = self._init_llm()
        
        # 模拟模式（没有 API Key 时使用）
        self.mock_mode = self.llm is None
        
        if self.mock_mode:
            logger.warning("⚠️  运行在模拟模式，使用内置的示例数据")
        else:
            logger.info(
                f"✅ FortuneTeller 初始化完成 | "
                f"模型: {self.config['model']} | "
                f"Prompt: {prompt_version}"
            )
    
    def _load_prompts(self):
        """加载所有 Prompt 模板"""
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        for prompt_type, versions in PROMPT_VERSIONS.items():
            prompt_path = versions.get(self.prompt_version, versions["latest"])
            full_path = os.path.join(project_root, prompt_path)
            
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        self.prompts[prompt_type] = f.read()
                    logger.debug(f"📝 加载 Prompt: {prompt_type} -> {prompt_path}")
                except Exception as e:
                    logger.error(f"❌ 加载 Prompt 失败 {prompt_path}: {e}")
            else:
                logger.warning(f"⚠️  Prompt 文件不存在: {full_path}")
    
    def _init_llm(self) -> Optional[Any]:
        """初始化 LLM 客户端"""
        if not LANGCHAIN_AVAILABLE:
            logger.debug("LangChain 未安装")
            return None
        
        if not self.api_key:
            logger.debug("没有设置 API Key")
            return None
        
        try:
            llm = ChatOpenAI(
                model=self.config["model"],
                api_key=self.api_key,
                base_url=self.config["base_url"],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                timeout=self.config["timeout"],
            )
            
            # 测试一下连接（可选）
            logger.debug(f"LLM 客户端初始化成功: {self.config['model']}")
            return llm
            
        except Exception as e:
            logger.error(f"❌ 初始化 LLM 失败: {e}")
            return None
    
    @retry(max_attempts=3, delay_seconds=1.0, backoff=2.0)
    @timing
    def _call_llm(self, prompt: str, request_type: str) -> str:
        """
        调用大模型（带重试和计时）
        
        Args:
            prompt: 完整的 Prompt
            request_type: 请求类型，用于日志和统计
        
        Returns:
            模型返回的内容
        
        Raises:
            APIKeyInvalidException: API Key 无效
            APITimeoutException: 调用超时
            ContentSafetyException: 输出包含敏感内容
        """
        start_time = time.perf_counter()
        success = False
        error_msg: Optional[str] = None
        result: Optional[str] = None
        
        try:
            # 模拟模式直接返回预设结果
            if self.mock_mode:
                time.sleep(1)  # 模拟网络延迟
                result = self._get_mock_result(request_type)
                success = True
                return result
            
            # 真正调用 API
            if self.llm is None:
                raise RuntimeError("LLM 未初始化")
            
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            result = response.content
            
            # 内容安全检查
            if SAFETY_CONFIG["enable_moderation"]:
                is_safe, reason = self.moderator.check_output(result)
                if not is_safe:
                    raise ContentSafetyException(f"输出内容不安全: {reason}")
            
            success = True
            return result
            
        except Exception as e:
            error_msg = str(e)
            
            # 判断异常类型，包装成我们的自定义异常
            error_str = str(e).lower()
            if "invalid" in error_str or "unauthorized" in error_str or "401" in error_str:
                raise APIKeyInvalidException("API Key 无效，请检查") from e
            elif "timeout" in error_str or "timed out" in error_str:
                raise APITimeoutException(f"API 调用超时 ({self.config['timeout']}s)") from e
            elif isinstance(e, ContentSafetyException):
                raise
            else:
                # 其他异常重新抛出
                raise
        
        finally:
            latency_ms = (time.perf_counter() - start_time) * 1000
            request_logger.log_request(
                request_type=request_type,
                params={"model": self.config["model"], "mock": self.mock_mode},
                model=self.config["model"],
                latency_ms=latency_ms,
                success=success,
                error=error_msg,
            )
    
    def _get_mock_result(self, request_type: str) -> str:
        """
        获取模拟结果（用于演示和测试）
        这些结果都是精心设计的，巴纳姆效应很强
        """
        mock_results = {
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
            
            "fortune": """
## 给你的第一印象

你表面上看起来很冷静、很理性，但其实内心非常敏感，很在意别人的看法。
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

1. **心态上** - 不要太焦虑。二十多岁和三十多岁本来就是用来试错的，走点弯路很正常。不要跟别人比，跟昨天的自己比就好。

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
            
            "relation": """
## 关系整体能量

你们两个是「互补型」的关系，在一起的时候 1+1 > 2。
他偏理性，做事情考虑周全，但是有时候太纠结；
你偏感性，做事情凭直觉，但是有时候容易冲动。

刚好可以互相弥补对方的缺点。

整体匹配度：85 分，是很值得珍惜的一段关系。

## 你们的优势

1. **沟通顺畅** - 你们两个都是讲道理的人，有什么事说开了就好了，不会冷战。
2. **三观一致** - 在大是大非的问题上，你们的看法基本是一样的，这一点非常重要。
3. **互相欣赏** - 他欣赏你的活力和创造力，你欣赏他的稳重和靠谱。

## 需要注意的地方

1. **他有时候太理性了**，遇到问题喜欢分析对错，但是女生有时候只是想要一个拥抱，想要被理解。下次遇到矛盾，先安抚情绪，再讲道理。

2. **你有时候太冲动了**，生气的时候容易说狠话，说完自己又后悔。下次生气的时候，先深呼吸 10 秒，再说话。

3. **你们都太独立了**，什么事都习惯自己扛。其实两个人在一起，就是要互相麻烦的。偶尔示弱，偶尔依赖对方，感情会更好。

## 相处建议

给男生：
- 多夸夸她，女生是需要被肯定的
- 记住一些重要的日子，不是说要花多少钱，而是让她知道你在乎
- 有时候就算你觉得她错了，也不要当场指出来，回家再说

给女生：
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
    def get_daily_fortune(
        self,
        birth_date: str,
        today: Optional[str] = None,
    ) -> str:
        """
        获取今日运势卡片
        
        Args:
            birth_date: 出生日期，格式：YYYY-MM-DD
            today: 今天日期，不传则使用当前日期
        
        Returns:
            今日运势的 Markdown 内容
        """
        from datetime import datetime
        if today is None:
            today = datetime.now().strftime("%Y-%m-%d")
        
        age = calculate_age(birth_date)
        logger.info(f"📅 今日运势: {birth_date} ({age}岁) @ {today}")
        
        prompt = self.prompts["daily"].format(
            birth_date=birth_date,
            today=today,
        )
        
        return self._call_llm(prompt, request_type="daily")
    
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
            direction: 测算方向："综合" / "事业" / "感情" / "财运" / "健康"
        
        Returns:
            运势解读的 Markdown 内容
        """
        age = calculate_age(birth_date)
        logger.info(f"🔮 测算运势: {birth_date} ({age}岁) {gender} {direction}")
        
        prompt = self.prompts["fortune"].format(
            birth_date=birth_date,
            gender=gender,
            direction=direction,
            age=age,
        )
        
        return self._call_llm(prompt, request_type="fortune")
    
    @cached
    def get_relation_reading(
        self,
        person_a: str,
        birth_a: str,
        person_b: str,
        birth_b: str,
        relation_type: str = "情侣",
    ) -> str:
        """
        两人合盘分析
        
        Args:
            person_a: 第一个人的称呼
            birth_a: 第一个人的出生日期
            person_b: 第二个人的称呼
            birth_b: 第二个人的出生日期
            relation_type: 关系类型："情侣" / "夫妻" / "合伙人" / "朋友"
        
        Returns:
            合盘分析的 Markdown 内容
        """
        logger.info(f"💑 合盘分析: {person_a} & {person_b} ({relation_type})")
        
        prompt = self.prompts["relation"].format(
            person_a=person_a,
            birth_a=birth_a,
            person_b=person_b,
            birth_b=birth_b,
            relation_type=relation_type,
        )
        
        return self._call_llm(prompt, request_type="relation")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取运行统计数据
        
        Returns:
            统计信息字典
        """
        from .utils import cache
        
        return {
            "version": "2.1.0",
            "model_profile": self.model_profile,
            "model_config": self.config,
            "prompt_version": self.prompt_version,
            "mock_mode": self.mock_mode,
            "requests": request_logger.get_stats(),
            "cache": cache.stats(),
        }
    
    def clear_cache(self):
        """清空缓存"""
        from .utils import cache
        cache.clear()
    
    def health_check(self) -> Tuple[bool, str]:
        """
        健康检查
        
        Returns:
            (是否健康, 状态信息)
        """
        if self.mock_mode:
            return True, "运行在模拟模式"
        
        if self.llm is None:
            return False, "LLM 客户端未初始化"
        
        # 可以加一个简单的 ping 测试
        return True, "健康"
