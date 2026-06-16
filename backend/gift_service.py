"""
Gift recommendation processing
"""
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from keyword_optimizer import KeywordOptimizer
import urllib.parse
from error_handlers import (
    DailyLimitExceededError, APIRateLimitError,
    RedditInsufficientDataError, get_analysis_error_from_exception
)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")

genai.configure(api_key=api_key)

class GiftService:
    def __init__(self):
        self.keyword_optimizer = KeywordOptimizer()
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.rate_limit_delay = float(os.getenv("GEMINI_RATE_LIMIT_DELAY", "3"))
        
        # API rate limit management
        self.last_request_time = None
        self.daily_request_count = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    async def generate_recommendations(self, posts: str, username: str, additional_info: Dict = None) -> Dict:
        """Generate gift recommendations"""
        await self._check_rate_limits()
        
        prompt = self._build_prompt(posts, username, additional_info)
        
        try:
            await asyncio.sleep(self.rate_limit_delay)
            
            self.last_request_time = datetime.now()
            self.daily_request_count += 1
            
            response = self.model.generate_content(prompt)
            
            if not response or not hasattr(response, 'text'):
                raise Exception("Invalid response from Gemini API")
            
            result = self._process_response(response.text.strip(), username)
            
            self._add_search_links(result)
            
            return result
            
        except Exception as e:
            # Retry on rate limit errors
            if "429" in str(e) or "quota" in str(e).lower():
                await asyncio.sleep(10)
                try:
                    response = self.model.generate_content(prompt)
                    result = self._process_response(response.text.strip(), username)
                    self._add_search_links(result)
                    return result
                except Exception as retry_error:
                    print(f"Retry attempt failed for user '{username}': {str(retry_error)}")
            
            raise get_analysis_error_from_exception(e, username)
    
    async def _check_rate_limits(self):
        """Check API rate limits"""
        now = datetime.now()
        
        if now >= self.daily_reset_time:
            self.daily_request_count = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Daily limit check (1200 requests per day)
        if self.daily_request_count >= 1200:
            raise DailyLimitExceededError()
        
        # Rate limit check (13 requests per minute)
        if self.last_request_time:
            time_since_last = (now - self.last_request_time).total_seconds()
            min_interval = 60 / 13  # ~4.6 second intervals
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                await asyncio.sleep(wait_time)
    
    def _build_prompt(self, posts: str, username: str, additional_info: Dict = None) -> str:
        """Build prompt"""
        additional_info_text = ""
        if additional_info:
            info_parts = []
            min_budget = additional_info.get("min_budget")
            max_budget = additional_info.get("max_budget")
            
            if min_budget is not None or max_budget is not None:
                if min_budget and max_budget:
                    info_parts.append(f"予算: {min_budget:,}円〜{max_budget:,}円")
                elif min_budget:
                    info_parts.append(f"予算: {min_budget:,}円以上")
                elif max_budget:
                    info_parts.append(f"予算: {max_budget:,}円以下")
            
            for key, label in [
                ("relationship", "関係性"),
                ("gender", "性別"),
                ("age", "年齢層"),
                ("occasion", "機会・シーン")
            ]:
                if additional_info.get(key):
                    info_parts.append(f"{label}: {additional_info[key]}")
            
            free_text_info = additional_info.get("additional_info")
            if free_text_info and free_text_info.strip():
                info_parts.append(f"その他の情報: {free_text_info.strip()}")
            
            if info_parts:
                additional_info_text = f"\n\n**Additional Info (for gift selection):**\n{', '.join(info_parts)}\n"
        
        # Determine if chat or Reddit analysis
        is_chat_analysis = isinstance(posts, list) and len(posts) > 0 and ("LINE Chat with" in posts[0].get("title", "") or "WhatsApp Chat with" in posts[0].get("title", ""))
        
        prompt_template = self._get_prompt_template(is_chat_analysis)
        
        return prompt_template.format(
            username=username,
            posts=posts,
            additional_info_text=additional_info_text
        )
    
    def _get_prompt_template(self, is_chat_analysis: bool = False) -> str:
        """Load prompt template from external file"""
        try:
            if is_chat_analysis:
                # LINEとWhatsApp両方に対応したチャット分析用プロンプトを使用
                prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "chat_analysis_prompt.txt")
            else:
                prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "gift_analysis_prompt.txt")
            
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            # フォールバック: 簡略版プロンプト
            return """
あなたは優秀なプレゼント選びの専門家です。以下のRedditユーザー「{username}」の投稿内容を分析し、
その人に最適なプレゼントを3つ提案してください。

Reddit投稿データ:
{posts}{additional_info_text}

以下のJSON形式で回答してください：
{{
"user_profile": {{
    "interests": ["興味1", "興味2", "興味3"],
    "personality_traits": ["性格1", "性格2", "性格3"],
    "values": ["価値観1", "価値観2"]
}},
"gift_recommendations": [
    {{
    "name": "プレゼント名1",
    "reason": "理由",
    "category": "カテゴリー",
    "amazon_keywords": "検索キーワード",
    "rakuten_keywords": "検索キーワード"
    }},
    {{
    "name": "プレゼント名2",
    "reason": "理由",
    "category": "カテゴリー",
    "amazon_keywords": "検索キーワード",
    "rakuten_keywords": "検索キーワード"
    }},
    {{
    "name": "プレゼント名3",
    "reason": "理由",
    "category": "カテゴリー",
    "amazon_keywords": "検索キーワード",
    "rakuten_keywords": "検索キーワード"
    }}
]
}}

データが不十分な場合は、"DATA_INSUFFICIENT_ERROR"を返してください。
"""
    
    def _process_response(self, response_text: str, username: str) -> Dict:
        """AIレスポンスを処理"""
        # データ不足エラーチェック
        if response_text == "DATA_INSUFFICIENT_ERROR":
            raise RedditInsufficientDataError(username)
        
        # JSONマークダウンを除去
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        return json.loads(response_text)
    
    def _add_search_links(self, result: Dict):
        """検索リンクを追加"""
        for gift in result.get("gift_recommendations", []):
            # AIが生成したキーワードを優先使用
            amazon_keywords = gift.get("amazon_keywords", gift["name"])
            rakuten_keywords = gift.get("rakuten_keywords", gift["name"])
            yahoo_keywords = gift.get("yahoo_keywords", amazon_keywords)
            category = gift.get("category", "")
            
            gift["amazon_link"] = self._generate_amazon_url(amazon_keywords, category)
            gift["rakuten_link"] = self._generate_rakuten_url(rakuten_keywords, category)
            gift["yahoo_link"] = self._generate_yahoo_url(yahoo_keywords, category)
    
    def _optimize_keywords(self, gift_name: str, category: str = "", platform: str = "amazon") -> str:
        """キーワードを最適化"""
        try:
            result = self.keyword_optimizer.optimize_keywords(gift_name, category)
            
            if platform == "rakuten":
                optimized = result["rakuten_keywords"]
            else:
                optimized = result["amazon_keywords"]
            
            return optimized if optimized.strip() else gift_name
        except Exception:
            return gift_name
    
    def _generate_amazon_url(self, gift_name: str, category: str = "") -> str:
        """Amazon検索URL生成"""
        optimized = self._optimize_keywords(gift_name, category, "amazon")
        encoded = urllib.parse.quote(optimized)
        return f"https://www.amazon.co.jp/s?k={encoded}&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&ref=nb_sb_noss"
    
    def _generate_rakuten_url(self, gift_name: str, category: str = "") -> str:
        """楽天検索URL生成"""
        optimized = self._optimize_keywords(gift_name, category, "rakuten")
        encoded = urllib.parse.quote(optimized)
        return f"https://search.rakuten.co.jp/search/mall/{encoded}/"
    
    def _generate_yahoo_url(self, gift_name: str, category: str = "") -> str:
        """Yahoo!ショッピング検索URL生成"""
        optimized = self._optimize_keywords(gift_name, category, "yahoo")
        encoded = urllib.parse.quote(optimized)
        return f"https://shopping.yahoo.co.jp/search?p={encoded}"