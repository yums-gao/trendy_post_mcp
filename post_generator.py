"""
Post generator module for creating trending Xiaohongshu-style posts.
"""
import os
import json
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import random
import logging

from dotenv import load_dotenv
from zai import ZhipuAiClient

# Load environment variables
load_dotenv()

# Initialize OpenAI client
LLM_API_KEY = os.getenv("ZHIPU_API_KEY")

# Initialize logger
logger = logging.getLogger(__name__)

class PostGenerator:
    """
    Generates trending Xiaohongshu-style posts based on image analysis and extracted text.
    """
    
    def __init__(self):
        """Initialize the post generator."""
        self.xiaohongshu_styles = [
            "lifestyle",
            "fashion",
            "beauty",
            "food",
            "travel",
            "fitness",
            "home decor",
            "snowboarding",
            "bouldering",
            "archery",
            "AI",
            "news",
            "tech",
            "exhibitions",
            "concerts",
            "plays",
            "films",
            "series"
        ]
        
        self.emoji_sets = {
            "lifestyle": ["✨", "💫", "🌈", "💖", "🥰", "🌟", "🌱"],
            "fashion": ["👗", "👠", "👜", "💅", "👒", "✨", "💎"],
            "beauty": ["💄", "💋", "✨", "💆‍♀️", "💅", "🧴", "💫"],
            "food": ["🍜", "🍣", "🍰", "☕", "🍷", "🥂", "😋"],
            "travel": ["✈️", "🌍", "🏝️", "🗺️", "🧳", "📸", "🌅"],
            "fitness": ["💪", "🏃‍♀️", "🧘‍♀️", "🥗", "🥤", "🌱", "✨"],
            "home decor": ["🏠", "🪴", "🛋️", "✨", "🕯️", "🖼️", "💫"],
            "snowboarding": ["🏂", "❄️", "🏔️", "🌨️", "🎿", "🥶", "🔥"],
            "bouldering": ["🧗‍♀️", "🧗‍♂️", "💪", "🪨", "🧠", "🤸‍♀️", "✨"],
            "archery": ["🏹", "🎯", "🔄", "💯", "🧘‍♀️", "🏆", "✨"],
            "AI": ["🤖", "💻", "🧠", "✨", "🔮", "📊", "🚀"],
            "news": ["🌍", "🤝", "📜", "🏛️", "🔄", "📰", "🌐"],
            "exhibitions": ["🖼️", "🏛️", "🎨", "✨", "📸", "🖌️", "👁️"],
            "concerts": ["🎵", "🎤", "🎸", "🥁", "🎧", "✨", "🔥"],
            "plays": ["🎭", "🎬", "👥", "🎪", "🎟️", "✨", "👏"],
            "films": ["🎬", "🍿", "🎞️", "🎭", "🎥", "🎦", "✨"],
            "series": ["📺", "🍿", "🎬", "📱", "🎭", "🎞️", "✨"]
        }

    def _call_llm(self, prompt: str, system_prompt: str = "You are a helpful assistant.", max_tokens: int = 4096) -> str:
        """
        Call the LLM to generate text.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """

        client = ZhipuAiClient(api_key=LLM_API_KEY)  # 请填写您自己的 API Key

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        print(messages)

        response = client.chat.completions.create(
            model="glm-4.5",
            messages=messages,
            thinking={
                "type": "enabled",    # 启用深度思考模式
            },
            max_tokens=max_tokens,          # 最大输出tokens
            temperature=0.7           # 控制输出的随机性
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
        
    
    def generate_post(self, image_data: Dict[str, Any], user_query: str = "") -> Dict[str, Any]:
        """
        Generate a trending Xiaohongshu post based on image analysis.
        
        Args:
            image_data: Image analysis data
            user_query: Optional user query to guide post generation
            
        Returns:
            Generated post data
        """
        # Extract relevant information from image data
        extracted_text = image_data.get("text", "")
        text_blocks = image_data.get("text_blocks", [])
        image_analysis = image_data.get("analysis", {})
        
        # Determine the most appropriate style based on image content and user query
        style = self._determine_style(extracted_text, user_query)
        
        # Generate the post content
        content = self._generate_content(extracted_text, text_blocks, image_analysis, style, user_query)
        
        # Generate title based on content
        title = self.generate_title(content, style, user_query)
        
        # Generate hashtags
        hashtags = self._generate_hashtags(content, style, user_query)
        
        return {
            "title": title,
            "content": content,
            "hashtags": hashtags,
            "style": style
        }
    
    def _determine_style(self, text: str, user_query: str = "") -> str:
        """
        Determine the most appropriate Xiaohongshu style based on image content using LLM.
        
        Args:
            text: Extracted text from the image
            image_analysis: Image analysis data
            user_query: Optional user query to guide style determination
            
        Returns:
            Style category string
        """
        # Use LLM to determine the style based on the extracted text and image analysis
        prompt = f"""Based on the following information, determine the most appropriate style category for a Xiaohongshu post:
Extracted text from image: {text}

User query: {user_query}

Please analyze this content and determine which of the following Xiaohongshu post styles would be most appropriate:
{', '.join(self.xiaohongshu_styles)}

Return only the style name, nothing else.
"""
        
        try:
            # Call LLM to determine style
            response = self._call_llm(prompt)
            
            # Clean and validate the response
            suggested_style = response.strip().lower()
            
            # # Check if the suggested style is in our list of styles
            # if suggested_style in self.xiaohongshu_styles:
            #     return suggested_style
            
            # # If not an exact match, try to find the closest match
            # for style in self.xiaohongshu_styles:
            #     if style in suggested_style:
            #         return style
            
            # Default to a random style if no match
            # return random.choice(self.xiaohongshu_styles)
            return suggested_style
            
        except Exception as e:
            logger.error(f"Error determining style with LLM: {str(e)}")
            # Fall back to random style if LLM fails
            return "lifestyle"

    def _generate_hashtags(self, content: str, style: str, user_query: str = "") -> List[str]:
        """
        Generate hashtags for the post using LLM.
        
        Args:
            content: Generated post content
            style: Post style
            user_query: Optional user query to guide hashtag generation
            
        Returns:
            List of hashtags
        """
        # prompt = f"""
        # Generate 5-8 trending Xiaohongshu hashtags for a post with the following:
        
        # Post content: {content[:300]}  # Truncate to avoid token limits
        
        # Post style: {style}
        
        # User query: {user_query}
        
        # The hashtags should be relevant, trendy, and in the style of Xiaohongshu (小红书).
        # Return only the hashtags as a comma-separated list, without the # symbol.
        # """

        prompt = f"""# Role: 小红书标签优化专家  
## 任务  
基于用户提供的爆款文章正文，生成高转化率的小红书标签组合（Tags），需同时满足**搜索流量提升**和**算法推荐**双目标。  

### 标签生成策略（三层矩阵）  
1. **流量池钥匙（占30%）**  
   - 选择2-3个百万级泛流量词，覆盖基础用户池  
   - 要求：从当前平台热门标签中匹配（参考实时热搜词）  
   - 示例：`#程序员` `#AI工具` `#效率提升`  

2. **精准狙击器（占50%）**  
   - 生成3-4个垂直领域标签，锁定细分人群需求  
   - 要求：结合正文关键词+行业高转化词（如技术类用`#独立开发者`，美妆类用`#黄黑皮天菜`）  
   - 示例：`#初创公司技术栈` `#全栈开发` `#低成本创业`  

3. **长尾钩子（占20%）**  
   - 创建1-2个蓝海长尾词，避开头部竞争  
   - 要求：  
     ▪️ 包含「解决方案+人群/场景」结构（例：`#学生党平价开发工具`）  
     ▪️ 搜索量/内容量比值＞5（通过工具检测）  

### 核心规则  
⚠️ **强制条款**  
- 标签总数：**严格控制在5-8个**（超出触发限流）  
- 排序逻辑：按「泛流量→垂类词→长尾词」顺序排列（前3位必须含大热词）  
- 敏感词规避：用「零克查词」检测，替换灰色词（如`#免费`→`#同价位更狠`）  

🚫 **绝对禁忌**  
× 禁用重复标签（如同时用`#技术栈`和`#开发工具`）  
× 禁用失效标签（参考平台每月公示的「过时标签库」）  
× 禁用纯英文标签（中文标签曝光率高42%）  

### 高阶技巧  
1. **热点截流**  
   - 若正文含热点关键词（如`AI`），添加带🔥图标的标签（例：`#AIGC工具🔥`）  
2. **跨屏引流**  
   - 同步抖音/微博热搜词（如`#多巴胺编程`），在标签和正文各出现3次  
3. **养号策略**  
   - 新账号前5篇笔记固定使用相同核心标签（例：技术类必带`#技术栈`+`#效率翻倍`）  

### 输出格式
- 请直接返回你生成的标签，多个标签之间用英文逗号分隔，不要添加任何其他内容。

接下来，请你使用以下文本内容、风格、和用户对话内容，生成一个符合小红书风格的标签组合：

文本内容：{content[:300]}

风格：{style}

用户对话内容：{user_query}
        """
        
        try:
            # Call LLM to generate hashtags
            response = self._call_llm(prompt)
            
            # Process the response
            hashtags = [tag.strip() for tag in response.split(',')]
            
            # Filter out empty tags and limit to 8 max
            hashtags = [tag for tag in hashtags if tag][:8]
            
            return hashtags
            
        except Exception as e:
            logger.error(f"Error generating hashtags with LLM: {str(e)}")
            # Return some generic hashtags if LLM fails
            return ["小红书", "分享", "推荐", style]
    
    def generate_title(self, content: str, style: str, user_query: str = "") -> str:
        """
        Generate a catchy title for the post using LLM.
        
        Args:
            content: Post content
            style: Post style
            user_query: Optional user query to guide title generation
            
        Returns:
            Generated title
        """
        # prompt = f"""
        # Generate a catchy, attention-grabbing Xiaohongshu (小红书) post title based on:
        
        # Post content: {content[:300]} 
        
        # Post style: {style}
        
        # User query: {user_query}
        
        # The title should be concise (under 30 characters), engaging, and in the style of popular Xiaohongshu posts.
        # Return only the title, nothing else.
        # """

        prompt = f"""**标题公式**：
- 采用「人群+痛点/利益点+解决方案」结构
- 融合数字/悬念词/感叹词（如：程序员必看！3天提效200%的AI工具链💥）
- 参考句式：
    * 震惊体："我竟然用XX天实现了XX！"
    * 数字体："XX个技巧让XX效率翻倍"
    * 反差体："别再XX了！这个方法YYY更有效"

请你根据以下文本内容、风格、和用户对话内容，生成一个符合小红书风格的标题：

文本内容：{content}

风格：{style}

用户对话内容：{user_query}

请直接返回你生成的标题，不要添加任何其他内容。
        """
        
        try:
            # Call LLM to generate title
            response = self._call_llm(prompt)
            
            # Clean the response
            title = response.strip()
            
            # # Ensure it's not too long
            # if len(title) > 50:  # Allow some flexibility but still keep it concise
            #     title = title[:47] + "..."
                
            return title
            
        except Exception as e:
            logger.error(f"Error generating title with LLM: {str(e)}")
            # Generate a simple title if LLM fails
            return f"我的{style}分享"  # "My {style} sharing"
    
    
    def _generate_content(
        self, 
        extracted_text: str, 
        text_blocks: List[Dict[str, Any]],
        image_analysis: Dict[str, Any],
        post_style: str,
        user_query: str = ""
    ) -> str:
        """
        Generate post content using LLM.
        
        Args:
            extracted_text: Text extracted from the image
            text_blocks: Structured text blocks from OCR
            image_analysis: Image analysis data
            post_style: Determined post style
            
        Returns:
            Generated post content
        """
        try:
            # Prepare the prompt
            prompt = self._create_prompt(extracted_text, text_blocks, image_analysis, post_style, user_query)
            
            role_prompt = """# 角色设定  
你是一名小红书爆款内容创作专家，擅长将普通话题转化为具有病毒式传播力的完整文章。你的核心能力包括：  
1. 情绪钩子设计：运用“夸张情绪词+反常识观点”引爆好奇心（如“太可怕了”“谁懂啊”“绝绝子”）  
2. 二极管结构法：通过“痛点刺激-解决方案-逆天效果”三段式框架制造爽感  
3. 平台化表达：口语化行文+高频emoji+20字内短段落适配移动端阅读  

# 爆款文章生成公式  
▶ 标题公式（保留原规则升级版）  
`[情绪词] + [反常识结果] + [人群标签] + [emoji]`  
✅ 示例：  
> “太可怕了！用ChatGPT写文案月入5w+，打工人逆袭指南💥”  

▶ 正文结构公式  
1. 段落小标题（简洁明了）
2. 情绪冲击开头（引发共鸣）  
   - 痛点场景故事（50字内）+ 夸张情绪词  
   > *例：“谁懂啊！熬夜写的文案0点赞，同事用AI 3秒收割10w流量！！”*
3. 颠覆认知转折（制造反差）  
   - “直到我发现...” + 反常识方法（突出简单/速成）  
4. 干货步骤拆解（实用价值）  
   - 分步骤+emoji图标 + 具体案例（如“实测7天涨粉5千”）  
5. 高潮金句点题（刺激传播）  
   - 用“记住：...”句式+争议性观点（例：“不会用AI的文案人，终将被淘汰！”）  
6. 互动钩子结尾（引导行动）  
   - “评论区扣【666】领指令库” / “戳合集看100个变现案例”  

# 创作规则  
1. 内容长度：正文300-500字，分3-5段，并配上段落小标题，每段≤3行  
2. 关键词植入：从用户提供的关键词库选3个自然融入（如“吐血整理”“手残党必备”）  
3. 平台特性：  
   - 每段尽量有段落小标题，并在段落标题和正文中插入1-2个🔥⭐💡类高亮emoji
   - 关键信息用“！”标点强化情绪
4. 禁忌：
   × 避免长段落（每段≤3行）  
   × 禁止直接出现"小红书"、"粉丝"等平台词  
   × 禁用复杂标签（后续单独处理） 
            """

            response = self._call_llm(prompt, system_prompt=role_prompt, max_tokens=8192)
            # print(response)

            return response
            
        except Exception as e:
            # Fallback content in case of API error
            print(f"Error generating content: {e}")
            return self._generate_fallback_content(extracted_text, post_style)
    
    def _create_prompt(
        self, 
        extracted_text: str, 
        text_blocks: List[Dict[str, Any]],
        image_analysis: Dict[str, Any],
        post_style: str,
        user_query: str = ""
    ) -> str:
        """
        Create a prompt for the LLM to generate post content.
        
        Args:
            extracted_text: Text extracted from the image
            text_blocks: Structured text blocks from OCR
            image_analysis: Image analysis data
            post_style: Determined post style
            
        Returns:
            Prompt string
        """
        # Extract relevant image information
        dimensions = image_analysis.get("dimensions", {})
        color_info = image_analysis.get("color_info", {})

        # Image details:
        # - Dimensions: {dimensions.get('width', 'unknown')}x{dimensions.get('height', 'unknown')}
        # - Brightness: {'Bright' if color_info.get('is_bright', False) else 'Dark'}
        
        
        prompt = f"""请你根据以下文本内容、风格、和用户对话内容，生成一个小红书爆款文章风格的推文：

文本内容：{extracted_text}

风格：{post_style}

用户对话内容：{user_query}

请注意：善用情绪钩子、平台化表达。多分段落，并添加emoji。请你直接返回你生成的推文，不要添加任何其他内容。
        """
        
        return prompt
    
    def _generate_fallback_content(self, extracted_text: str, post_style: str) -> str:
        """
        Generate fallback content when API call fails.
        
        Args:
            extracted_text: Text extracted from the image
            post_style: Determined post style
            
        Returns:
            Fallback content
        """
        # Extract a few words from the text to personalize the fallback
        words = extracted_text.split()
        sample_text = " ".join(words[:10]) if len(words) > 10 else extracted_text
        
        templates = [
            f"今天发现了一个超棒的{post_style}好物！{sample_text}... 真的很推荐大家尝试一下～",
            f"分享一下我最近超爱的{post_style}心得！{sample_text}... 希望对你也有帮助～",
            f"偶然间发现的{post_style}宝藏！{sample_text}... 真的是相见恨晚！"
        ]
        
        return random.choice(templates)
    
    def _get_emojis(self, post_style: str, count: int = 5) -> List[str]:
        """
        Get relevant emojis for the post.
        
        Args:
            post_style: Post style category
            count: Maximum number of emojis to include
            
        Returns:
            List of emoji strings
        """
        style_emojis = self.emoji_sets.get(post_style, ["✨", "💫", "🌈", "💖", "🥰", "🌟", "🌱"])
        
        # Select random emojis from the style category
        if style_emojis:
            # Ensure we don't try to select more emojis than available
            available_count = min(count, len(style_emojis))
            selected_emojis = random.sample(style_emojis, available_count)
        else:
            selected_emojis = ["✨", "💫"]
        
        return selected_emojis
    
    def _format_post(self, content: str, hashtags: List[str], emojis: List[str]) -> str:
        """
        Format the final post with content, hashtags, and emojis.
        
        Args:
            content: Generated post content
            hashtags: Selected hashtags
            emojis: Selected emojis
            
        Returns:
            Formatted post string
        """
        # Add random emojis throughout the content
        paragraphs = content.split("\n\n")
        formatted_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # Add an emoji at the beginning or end of some paragraphs
                if random.random() > 0.5 and emojis:
                    emoji = random.choice(emojis)
                    if random.random() > 0.5:
                        paragraph = f"{emoji} {paragraph}"
                    else:
                        paragraph = f"{paragraph} {emoji}"
                formatted_paragraphs.append(paragraph)
        
        # Join paragraphs
        formatted_content = "\n\n".join(formatted_paragraphs)
        
        # Add hashtags at the end
        hashtag_section = " ".join(hashtags)
        
        # Final post
        final_post = f"{formatted_content}\n\n{hashtag_section}"
        
        return final_post


# Example usage
if __name__ == "__main__":
    generator = PostGenerator()
    
    # Sample image data
    sample_data = {
        "text": "今天去了新开的咖啡店，环境超级好，咖啡也很香浓",
        "text_blocks": [],
        "language": "zh",
        "analysis": {
            "dimensions": {"width": 1080, "height": 1920, "aspect_ratio": 0.5625},
            "color_info": {"is_bright": True, "dominant_colors": [[240, 240, 240], [200, 180, 160]]}
        }
    }
    
    post = generator.generate_post(sample_data)
    print(json.dumps(post, ensure_ascii=False, indent=2))
