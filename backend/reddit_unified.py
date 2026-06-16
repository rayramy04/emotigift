"""
統合されたReddit API処理
OAuth/non-OAuthの重複を排除し、効率的な処理を実現
"""
import os
import requests
import asyncio
import random
from typing import List, Dict, Optional
from dotenv import load_dotenv
from reddit_official_api import RedditOfficialAPI
from error_handlers import (
    RedditUserNotFoundError, RedditPostsNotFoundError, 
    RedditInsufficientDataError
)

load_dotenv()

class UnifiedRedditService:
    def __init__(self):
        self.use_oauth = bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"))
        if self.use_oauth:
            self.reddit_api = RedditOfficialAPI()
        
        # 設定値
        self.fetch_limit = int(os.getenv("REDDIT_FETCH_LIMIT", "25"))
        self.max_posts = int(os.getenv("MAX_REDDIT_POSTS", "50"))
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", "15000"))
        
        # User-Agent設定
        self.user_agents = [
            'EmotiGift/1.0 (https://emotigift.vercel.app; contact@emotigift.com)',
            'Mozilla/5.0 (compatible; EmotiGift/1.0; +https://emotigift.vercel.app)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        ]
    
    async def fetch_user_data(self, username: str) -> str:
        """統合されたユーザーデータ取得"""
        try:
            if self.use_oauth:
                return await self._fetch_with_oauth(username)
            else:
                return await self._fetch_without_oauth(username)
        except Exception as e:
            # OAuth失敗時のフォールバック
            if self.use_oauth:
                print(f"OAuth failed for {username}: {e}, trying non-OAuth")
                return await self._fetch_without_oauth(username)
            raise
    
    async def _fetch_with_oauth(self, username: str) -> str:
        """OAuth方式でのデータ取得"""
        user_data = self.reddit_api.fetch_user_data_combined(username, 
                                                           post_limit=self.fetch_limit, 
                                                           comment_limit=30)
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        
        if not posts and not comments:
            raise RedditPostsNotFoundError(username)
        
        return self._process_combined_data(posts, comments, username)
    
    async def _fetch_without_oauth(self, username: str) -> str:
        """非OAuth方式でのデータ取得"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
            'Connection': 'keep-alive'
        }
        
        # 自然なリクエスト間隔
        await asyncio.sleep(random.uniform(2, 5))
        
        # 複数のURLを試行
        urls = [
            f"https://www.reddit.com/user/{username}/submitted.json?limit={self.fetch_limit}",
            f"https://old.reddit.com/user/{username}/submitted.json?limit={self.fetch_limit}",
        ]
        
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=12)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    if posts:
                        return self._process_posts_only(posts, username)
            except Exception as e:
                print(f"Failed to fetch from {url}: {e}")
                continue
        
        raise RedditUserNotFoundError(username)
    
    def _process_combined_data(self, posts: List[Dict], comments: List[Dict], username: str) -> str:
        """投稿とコメントを統合処理"""
        quality_content = []
        
        # 投稿処理
        for post in posts:
            post_data = post.get('data', {})
            content_item = self._extract_post_data(post_data)
            if content_item:
                quality_content.append(content_item)
        
        # コメント処理
        for comment in comments:
            comment_data = comment.get('data', {})
            content_item = self._extract_comment_data(comment_data)
            if content_item:
                quality_content.append(content_item)
        
        return self._finalize_content(quality_content, username)
    
    def _process_posts_only(self, posts: List[Dict], username: str) -> str:
        """投稿のみを処理"""
        quality_content = []
        
        for post in posts:
            post_data = post.get('data', {})
            content_item = self._extract_post_data(post_data)
            if content_item:
                quality_content.append(content_item)
        
        return self._finalize_content(quality_content, username)
    
    def _extract_post_data(self, post_data: Dict) -> Optional[Dict]:
        """投稿データを抽出・評価"""
        title = post_data.get('title', '')
        selftext = post_data.get('selftext', '')
        subreddit = post_data.get('subreddit', '')
        score = post_data.get('score', 0)
        num_comments = post_data.get('num_comments', 0)
        created_utc = post_data.get('created_utc', 0)
        
        if not title:
            return None
        
        # 品質スコア計算
        engagement_score = score * 2 + num_comments * 3
        text_quality = min(len(title + selftext) / 10, 80)
        quality_score = engagement_score + text_quality
        
        # 時系列重み
        import time
        post_age_days = (time.time() - created_utc) / 86400
        recency_weight = max(0.3, 1 - (post_age_days / 365))
        final_score = quality_score * recency_weight
        
        if final_score > 10:
            return {
                'text': f"Subreddit: r/{subreddit}\nTitle: {title}\nContent: {selftext}\nEngagement: {score}↑ {num_comments}💬\n---",
                'quality': final_score,
                'length': len(title) + len(selftext),
                'subreddit': subreddit,
                'type': 'post'
            }
        return None
    
    def _extract_comment_data(self, comment_data: Dict) -> Optional[Dict]:
        """コメントデータを抽出・評価"""
        body = comment_data.get('body', '')
        subreddit = comment_data.get('subreddit', '')
        score = comment_data.get('score', 0)
        created_utc = comment_data.get('created_utc', 0)
        
        if not body or len(body.strip()) < 20:
            return None
        
        # 品質スコア計算
        engagement_score = score * 1.5
        text_quality = min(len(body) / 5, 60)
        quality_score = engagement_score + text_quality
        
        # 時系列重み
        import time
        comment_age_days = (time.time() - created_utc) / 86400
        recency_weight = max(0.3, 1 - (comment_age_days / 365))
        final_score = quality_score * recency_weight
        
        if final_score > 15:
            return {
                'text': f"Comment in r/{subreddit}: {body[:200]}{'...' if len(body) > 200 else ''}\nScore: {score}↑\n---",
                'quality': final_score,
                'length': len(body),
                'subreddit': subreddit,
                'type': 'comment'
            }
        return None
    
    def _finalize_content(self, quality_content: List[Dict], username: str) -> str:
        """最終的なコンテンツ選択と整形"""
        if not quality_content:
            raise RedditInsufficientDataError(username)
        
        # 品質順でソート
        quality_content.sort(key=lambda x: x['quality'], reverse=True)
        
        # サブレディット分散を考慮した選択
        selected_content = []
        used_subreddits = {}
        total_length = 0
        
        # サブレディット頻度計算
        subreddit_counts = {}
        for content in quality_content:
            sub = content.get('subreddit', 'unknown')
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
        
        top_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)
        main_subreddits = [sub[0] for sub in top_subreddits[:3]]
        
        # バランス良く選択
        for content in quality_content:
            if len(selected_content) >= self.max_posts or total_length >= self.max_text_length:
                break
            
            subreddit = content.get('subreddit', 'unknown')
            max_from_sub = 12 if subreddit in main_subreddits else 3
            
            if used_subreddits.get(subreddit, 0) < max_from_sub:
                if total_length + content['length'] <= self.max_text_length:
                    selected_content.append(content)
                    used_subreddits[subreddit] = used_subreddits.get(subreddit, 0) + 1
                    total_length += content['length']
        
        if len(selected_content) < 1 or total_length < 100:
            raise RedditInsufficientDataError(username)
        
        return "\n".join([content['text'] for content in selected_content])