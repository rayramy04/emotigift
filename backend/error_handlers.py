"""
エラーハンドリング関連のユーティリティ
"""
from fastapi import HTTPException

class RedditUserNotFoundError(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=404,
            detail=f"Reddit user '{username}' が見つかりません。ユーザー名を確認してください。"
        )

class RedditPostsNotFoundError(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=404,
            detail=f"Reddit user '{username}' の投稿が見つかりません。投稿がないか、削除されたアカウントの可能性があります。"
        )

class RedditInsufficientDataError(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=404,
            detail=f"Reddit user '{username}' の投稿データが不足しています。プレゼント提案にはある程度の投稿履歴が必要です。より活発に投稿しているアカウントをお試しください。"
        )

class RedditPrivateAccountError(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=403,
            detail=f"Reddit user '{username}' の投稿にアクセスできません。プライベートアカウントまたは削除されたアカウントの可能性があります。"
        )

class RedditAPITimeoutError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=504,
            detail="Reddit APIへの接続がタイムアウトしました。しばらく時間をおいてから再度お試しください。"
        )

class RedditAPIUnavailableError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=503,
            detail="Reddit APIに一時的にアクセスできません。しばらく時間をおいてから再度お試しください。"
        )

class APIRateLimitError(HTTPException):
    def __init__(self, service: str = "API"):
        super().__init__(
            status_code=429,
            detail=f"{service}制限に達しました。しばらく時間をおいてから再度お試しください。"
        )

class DailyLimitExceededError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail="本日のAPI利用制限に達しました。明日再度お試しください。"
        )

def get_reddit_error_from_response(response, username: str) -> HTTPException:
    """レスポンスコードから適切なエラーを返す"""
    status = response.status_code
    
    if status == 404:
        return RedditUserNotFoundError(username)
    elif status == 403:
        return RedditPrivateAccountError(username)
    elif status == 429:
        return APIRateLimitError("Reddit API")
    elif status == 504:
        return RedditAPITimeoutError()
    elif status == 503:
        return RedditAPIUnavailableError()
    else:
        return HTTPException(
            status_code=500,
            detail="Reddit データの取得中に予期しないエラーが発生しました。しばらく時間をおいてから再度お試しください。"
        )

def get_analysis_error_from_exception(e: Exception, username: str) -> HTTPException:
    """例外から適切なエラーメッセージを生成"""
    error_message = str(e).lower()
    
    if "429" in error_message or "quota" in error_message or "rate limit" in error_message:
        return APIRateLimitError("AI分析の")
    elif "insufficient" in error_message or "not enough" in error_message:
        return RedditInsufficientDataError(username)
    elif "json" in error_message and ("decode" in error_message or "parse" in error_message):
        return HTTPException(
            status_code=500,
            detail="AI分析結果の処理中にエラーが発生しました。システムの一時的な問題の可能性があります。しばらく時間をおいてから再度お試しください。"
        )
    elif "timeout" in error_message or "time out" in error_message:
        return HTTPException(
            status_code=504,
            detail="AI分析がタイムアウトしました。サーバーが混雑している可能性があります。しばらく時間をおいてから再度お試しください。"
        )
    elif "api key" in error_message or "authentication" in error_message:
        return HTTPException(
            status_code=500,
            detail="AIサービスの設定エラーです。管理者にお問い合わせください。"
        )
    else:
        return HTTPException(
            status_code=500,
            detail=f"プレゼント提案の生成中にエラーが発生しました。エラー詳細: {error_message[:100]}...しばらく時間をおいてから再度お試しください。"
        )