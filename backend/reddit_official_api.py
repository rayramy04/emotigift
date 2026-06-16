"""
Reddit公式API実装例
OAuth認証を使用してReddit APIにアクセス
"""
import os
import requests
import base64
import time
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class RedditOfficialAPI:
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "EmotiGift/1.0 by Live_Tone4502")
        self.access_token = None
        self.token_expires = 0
        
    def get_access_token(self) -> str:
        """OAuth認証でアクセストークンを取得"""
        if self.access_token and time.time() < self.token_expires:
            return self.access_token
            
        # Basic認証用のヘッダー
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth}',
            'User-Agent': self.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(
            'https://www.reddit.com/api/v1/access_token',
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            # トークンの有効期限を設定（通常1時間）
            self.token_expires = time.time() + token_data.get('expires_in', 3600) - 60
            return self.access_token
        else:
            raise Exception(f"Failed to get access token: {response.status_code}")
    
    def fetch_user_posts(self, username: str, limit: int = 25) -> List[Dict]:
        """ユーザーの投稿を取得"""
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': self.user_agent
        }
        
        url = f'https://oauth.reddit.com/user/{username}/submitted'
        params = {
            'limit': limit,
            'sort': 'new'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('children', [])
        elif response.status_code == 404:
            raise Exception(f"User {username} not found")
        else:
            raise Exception(f"API request failed: {response.status_code}")
    
    def fetch_user_comments(self, username: str, limit: int = 50) -> List[Dict]:
        """ユーザーのコメントを取得して深い洞察を得る"""
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': self.user_agent
        }
        
        url = f'https://oauth.reddit.com/user/{username}/comments'
        params = {
            'limit': limit,
            'sort': 'new'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('children', [])
        elif response.status_code == 404:
            raise Exception(f"User {username} not found")
        else:
            raise Exception(f"API request failed: {response.status_code}")
    
    def fetch_user_data_combined(self, username: str, post_limit: int = 25, comment_limit: int = 50) -> Dict:
        """投稿とコメントを組み合わせて取得"""
        posts = self.fetch_user_posts(username, post_limit)
        comments = self.fetch_user_comments(username, comment_limit)
        
        return {
            'posts': posts,
            'comments': comments
        }

# 使用例
async def fetch_reddit_posts_official(username: str) -> str:
    """公式APIを使用した投稿取得（既存関数の置き換え用）"""
    try:
        reddit_api = RedditOfficialAPI()
        posts = reddit_api.fetch_user_posts(username)
        
        if not posts:
            raise HTTPException(
                status_code=404, 
                detail=f"Reddit user '{username}' の投稿が見つかりませんでした。"
            )
        
        # 既存の形式に変換
        post_texts = []
        for post in posts:
            post_data = post.get('data', {})
            title = post_data.get('title', '')
            selftext = post_data.get('selftext', '')
            subreddit = post_data.get('subreddit', '')
            score = post_data.get('score', 0)
            num_comments = post_data.get('num_comments', 0)
            
            if title:
                post_text = f"Subreddit: r/{subreddit}\nTitle: {title}\nContent: {selftext}\nEngagement: {score}↑ {num_comments}💬\n---"
                post_texts.append(post_text)
        
        return "\n".join(post_texts)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit API error: {str(e)}")