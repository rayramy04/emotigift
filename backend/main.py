"""
EmotiGift API - Main Entry Point
"""
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from typing import Optional
import os
from dotenv import load_dotenv
from datetime import datetime
import re
import logging

from reddit_unified import UnifiedRedditService
from gift_service import GiftService

load_dotenv()

logger = logging.getLogger(__name__)

MAX_CHAT_CONTENT_CHARS = int(os.getenv("MAX_CHAT_CONTENT_CHARS", "1000000"))
# JSON overhead and multi-byte characters make the body larger than the text itself
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", str(MAX_CHAT_CONTENT_CHARS * 3 + 10_000)))
ANALYZE_RATE_LIMIT = os.getenv("ANALYZE_RATE_LIMIT", "5/minute;50/day")
MAX_BUDGET_YEN = 10_000_000
REDDIT_ID_PATTERN = r"^[A-Za-z0-9_-]{3,20}$"


class ChatAnalysisRequest(BaseModel):
    chat_content: str = Field(max_length=MAX_CHAT_CONTENT_CHARS)
    min_budget: Optional[int] = Field(default=None, ge=0, le=MAX_BUDGET_YEN)
    max_budget: Optional[int] = Field(default=None, ge=0, le=MAX_BUDGET_YEN)
    relationship: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=100)
    age: Optional[str] = Field(default=None, max_length=100)
    occasion: Optional[str] = Field(default=None, max_length=100)
    additional_info: Optional[str] = Field(default=None, max_length=1000)

LineChatAnalysisRequest = ChatAnalysisRequest
WhatsAppChatAnalysisRequest = ChatAnalysisRequest


def get_client_ip(request: Request) -> str:
    """
    Client IP used as the rate limit key.

    Behind a reverse proxy (Render) the socket address is the proxy, so read
    X-Forwarded-For. Entries are appended by each proxy, so only the ones
    added by our own proxies can be trusted: count TRUSTED_PROXY_HOPS from the right.
    """
    hops = int(os.getenv("TRUSTED_PROXY_HOPS", "1"))
    forwarded_for = request.headers.get("x-forwarded-for")
    if hops > 0 and forwarded_for:
        parts = [part.strip() for part in forwarded_for.split(",") if part.strip()]
        if parts:
            return parts[max(len(parts) - hops, 0)]
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=get_client_ip)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def limit_request_body_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_REQUEST_BODY_BYTES:
        return JSONResponse(
            status_code=413,
            content={"detail": "リクエストが大きすぎます。チャット履歴を短くして再度お試しください。"},
        )
    return await call_next(request)


environment = os.getenv("ENVIRONMENT", "").lower()
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
if environment != "production":
    allowed_origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])

allow_any_origin = environment == "development"
if allow_any_origin:
    allowed_origins = ["*"]

# Credentials are never needed (no cookies/auth) and must not be combined with "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

reddit_service = UnifiedRedditService()
gift_service = None

def get_gift_service() -> GiftService:
    global gift_service
    if gift_service is None:
        gift_service = GiftService()
    return gift_service

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "EmotiGift API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/analyze")
@limiter.limit(ANALYZE_RATE_LIMIT)
async def analyze_reddit_user(
    request: Request,
    reddit_id: str = Query(pattern=REDDIT_ID_PATTERN),
    min_budget: Optional[int] = Query(default=None, ge=0, le=MAX_BUDGET_YEN),
    max_budget: Optional[int] = Query(default=None, ge=0, le=MAX_BUDGET_YEN),
    relationship: Optional[str] = Query(default=None, max_length=100),
    gender: Optional[str] = Query(default=None, max_length=100),
    age: Optional[str] = Query(default=None, max_length=100),
    occasion: Optional[str] = Query(default=None, max_length=100),
    additional_info: Optional[str] = Query(default=None, max_length=1000),
):
    """
    Analyze Reddit user and generate gift recommendations
    
    Args:
        reddit_id: Reddit user ID
        min_budget: Minimum budget (yen)
        max_budget: Maximum budget (yen)
        relationship: Relationship type
        gender: Gender
        age: Age group
        occasion: Occasion type
        additional_info: Additional information
    
    Returns:
        User profile analysis and gift recommendations
    """
    additional_info_dict = {
        "min_budget": min_budget,
        "max_budget": max_budget,
        "relationship": relationship,
        "gender": gender,
        "age": age,
        "occasion": occasion,
        "additional_info": additional_info
    }
    
    try:
        reddit_posts = await reddit_service.fetch_user_data(reddit_id)
        
        if not reddit_posts:
            raise HTTPException(
                status_code=404,
                detail=f"Reddit user '{reddit_id}' の投稿データを取得できませんでした。ユーザー名を確認するか、別のアカウントをお試しください。"
            )
        
        recommendations = await get_gift_service().generate_recommendations(
            reddit_posts, reddit_id, additional_info_dict
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error for user %s", reddit_id)
        raise HTTPException(
            status_code=500,
            detail="プレゼント分析中に問題が発生しました。しばらく時間をおいてから再度お試しください。"
        )

async def _process_chat_analysis(parsed_chat: str, target_person: str, additional_info_dict: dict, platform: str):
    """
    Common processing to generate gift recommendations from chat analysis results
    
    Args:
        parsed_chat: Parsed chat text
        target_person: Target person name
        additional_info_dict: Additional information dictionary
        platform: "LINE" or "WhatsApp"
    
    Returns:
        Gift recommendation results
    """
    reddit_posts = [{"body": parsed_chat, "title": f"{platform} Chat with {target_person}"}]
    return await get_gift_service().generate_recommendations(
        reddit_posts, target_person, additional_info_dict
    )

def _build_additional_info_dict(request) -> dict:
    """
    Common function to build additional information dictionary from request
    
    Args:
        request: LINE or WhatsApp chat analysis request
    
    Returns:
        Additional information dictionary
    """
    return {
        "min_budget": request.min_budget,
        "max_budget": request.max_budget,
        "relationship": request.relationship,
        "gender": request.gender,
        "age": request.age,
        "occasion": request.occasion,
        "additional_info": request.additional_info
    }

def _handle_chat_error(error: ValueError, chat_type: str) -> HTTPException:
    """
    Function to handle chat analysis errors consistently
    
    Args:
        error: ValueError that occurred
        chat_type: "LINE" or "WhatsApp"
    
    Returns:
        HTTPException with appropriate message
    """
    error_message = str(error)
    
    if "TARGET_SELECTION_REQUIRED:" in error_message:
        return HTTPException(status_code=400, detail=error_message)
    
    elif "グループ" in error_message:
        if chat_type == "WhatsApp":
            hint_message = (
                "• 必ず一対一のプライベートチャットファイルをアップロードしてください\n"
                "• グループチャットには対応していません"
            )
        else:
            hint_message = (
                "• 必ず一対一の個人トークファイルをアップロードしてください\n"
                "• グループトークには対応していません"
            )
        return HTTPException(status_code=400, detail=f"📄 {error_message}\n\n💡 ヒント:\n{hint_message}")
    
    elif "特定できませんでした" in error_message:
        hint_message = (
            "• 十分な会話内容があることを確認してください\n"
            "• 一対一のチャットファイルかどうか確認してください\n"
            "• ファイルが正しくアップロードされているか確認してください"
        )
        return HTTPException(status_code=400, detail=f"📄 {error_message}\n\n💡 チャット内容の確認:\n{hint_message}")
    
    else:
        return HTTPException(status_code=400, detail=error_message)

def _extract_target_from_header(lines: list[str], chat_type: str) -> tuple[str | None, list[str]]:
    """
    Common function to extract analysis target from chat file header
    
    Args:
        lines: List of chat file lines
        chat_type: "line" or "whatsapp"
    
    Returns:
        tuple: (target person name, remaining lines)
    """
    target_person = None
    remaining_lines = lines.copy()
    
    for i, line in enumerate(lines[:10]):
        if line.startswith('分析対象: '):
            target_name = line.replace('分析対象: ', '').strip()
            if target_name and target_name != 'EXTRACT_FROM_CONTENT':
                target_person = target_name
                remaining_lines.pop(i)
                break
        elif chat_type == "line":
            if 'Chat history with' in line:
                match = re.search(r'Chat history with (.+)', line)
                if match:
                    target_person = match.group(1).strip()
                    break
            elif line.startswith('[LINE]') and line.endswith('.txt'):
                match = re.search(r'\[LINE\](.+)\.txt', line)
                if match:
                    target_person = match.group(1).strip()
                    break
    
    return target_person, remaining_lines

def _determine_target_person(target_person: str | None, speakers: set[str]) -> str:
    """
    Common logic to determine analysis target
    
    Args:
        target_person: Target person name extracted from header
        speakers: Set of chat participants
    
    Returns:
        Determined analysis target name
    
    Raises:
        ValueError: When group chat detected, selection required, or target not found
    """
    if not target_person:
        if len(speakers) > 2:
            raise ValueError("グループトークは対応していません。一対一の個人トークのみアップロードしてください。")
        
        if len(speakers) == 2:
            speakers_list = list(speakers)
            raise ValueError(f"TARGET_SELECTION_REQUIRED:{speakers_list[0]}|{speakers_list[1]}")
        elif len(speakers) == 1:
            target_person = list(speakers)[0]
        else:
            raise ValueError("チャット内容から分析対象者を特定できませんでした。チャット内容に十分な会話があることを確認してください。")
    else:
        # 明示的に指定された対象者の場合、speakersに含まれているかチェック
        if target_person != 'EXTRACT_FROM_CONTENT':
            if target_person in speakers:
                # 対象者が見つかった場合はそのまま返す（再選択を求めない）
                return target_person
            else:
                raise ValueError(f"指定された分析対象者 '{target_person}' がチャット内に見つかりませんでした。")
        else:
            # EXTRACT_FROM_CONTENTの場合のみ選択を求める
            if len(speakers) == 2:
                speakers_list = list(speakers)
                raise ValueError(f"TARGET_SELECTION_REQUIRED:{speakers_list[0]}|{speakers_list[1]}")
    
    return target_person or "分析対象者"

def _extract_target_messages(parsed_messages: list[str], target_person: str) -> str:
    """
    Common function to extract only target person's messages
    
    Args:
        parsed_messages: List of parsed messages
        target_person: Target person name
    
    Returns:
        Text for analysis
    """
    target_messages = []
    for msg in parsed_messages:
        if target_person and msg.startswith(f"{target_person}:"):
            content = msg[len(f"{target_person}:"):].strip()
            target_messages.append(content)
    
    return "\n".join(target_messages) if target_messages else "\n".join(parsed_messages)

def parse_line_chat(chat_content: str) -> tuple[str, str]:
    """
    Parse LINE chat history to identify analysis target and analysis text
    
    Args:
        chat_content: Raw text of LINE chat history
    
    Returns:
        tuple: (target person name, formatted text for analysis)
    """
    lines = chat_content.strip().split('\n')
    target_person, lines = _extract_target_from_header(lines, "line")
    
    parsed_messages = []
    speakers = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect time patterns (support for various formats)
        time_patterns = [
            r'^\d{1,2}:\d{2}\t(.+?)\t(.+)$',  # スマホ形式（タブ区切り）
            r'^\d{1,2}:\d{2}\s+(.+?)\s+(.+)$',  # PC形式（スペース区切り）
            r'^\d{4}/\d{2}/\d{2}\s+\d{1,2}:\d{2}\t(.+?)\t(.+)$',  # 日付付き形式
            r'^(.+?)\s+\d{1,2}:\d{2}\s+(.+)$',  # 名前-時刻-メッセージ形式
            # Generic pattern removed to prevent misrecognition
            # r'^(.+?)[\t\s]+(.+)$'  # 汎用的な名前-メッセージ形式（最後の手段）
        ]
        
        message_found = False
        for pattern in time_patterns:
            match = re.match(pattern, line)
            if match:
                sender = match.group(1).strip()
                content = match.group(2).strip()
                
                # Exclude system messages and invalid speakers
                system_messages = [
                    'Photos', 'Videos', 'Audio', 'Message', 'Missed call', 'Canceled',
                    'Saved on', 'Chat history with', 'LINE', 'WhatsApp',
                    'Stickers', 'Location'
                ]
                
                # Content-based system message detection
                system_content_patterns = [
                    'unsent a message',
                    r'^\d{2}:\d{2}$',  # 時刻のみ
                    r'^Photos?$',
                    r'^Videos?$', 
                    r'^Audio$',
                    r'^Stickers?$'
                ]
                
                # Basic sender name validation
                if (re.search(r'\d{1,2}:\d{2}', sender) or 
                    len(sender) < 2 or len(sender) > 50 or
                    sender.isdigit() or
                    re.match(r'^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}', sender) or
                    '参加しました' in sender or '退出しました' in sender or
                    'グループ名' in sender or 'アルバム' in sender):
                    continue
                
                # Check system messages for all patterns
                if sender in system_messages:
                    continue
                
                # Check content-based system messages
                is_system_content = False
                for pattern in system_content_patterns:
                    if re.search(pattern, content):
                        is_system_content = True
                        break
                if is_system_content:
                    continue
                
                # Exclude metadata lines and photo tags
                if (content.startswith('[') and content.endswith(']') or
                    content.lower().startswith('photo')):
                    continue
                    
                speakers.add(sender)
                parsed_messages.append(f"{sender}: {content}")
                message_found = True
                break
        
        # Patterns for lines to exclude
        if not message_found:
            if (re.match(r'^\d{4}\.\d{2}\.\d{2}', line) or
                'Saved on:' in line or 
                'Chat history with' in line or
                line.startswith('分析対象: ') or
                line.startswith('﻿')):
                continue
                
            # Process as continuation message
            if parsed_messages:
                parsed_messages[-1] += " " + line
    
    logger.debug("LINE speakers detected: %s", speakers)
    logger.debug("Number of speakers: %s", len(speakers))
    logger.debug("Parsed messages count: %s", len(parsed_messages))
    if len(speakers) > 2:
        logger.warning("Detected %s LINE speakers: %s", len(speakers), list(speakers))
        logger.debug("First parsed LINE message count: %s", min(len(parsed_messages), 10))
        logger.debug("Original LINE line sample count: %s", min(len(lines), 20))
    
    # Additional check for abnormally high number of speakers
    if len(speakers) > 5:
        logger.error("Too many LINE speakers detected (%s). Speakers: %s", len(speakers), list(speakers))
        # Tighten parser for obvious parsing errors
        speakers = {s for s in speakers if len(s) >= 2 and len(s) <= 20 and not s.isdigit()}
    
    target_person = _determine_target_person(target_person, speakers)
    analysis_text = _extract_target_messages(parsed_messages, target_person)
    
    return target_person, analysis_text

def parse_whatsapp_chat(chat_content: str) -> tuple[str, str]:
    """
    Parse WhatsApp chat history to identify analysis target and analysis text
    
    Args:
        chat_content: Raw text of WhatsApp chat history
    
    Returns:
        tuple: (target person name, formatted text for analysis)
    """
    lines = chat_content.strip().split('\n')
    target_person, lines = _extract_target_from_header(lines, "whatsapp")
    
    parsed_messages = []
    speakers = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect WhatsApp time patterns
        time_patterns = [
            r'^\[[\d/,:\s\u202f\u00a0APMapm]+\]\s*([^~]+?):\s*(.+)$',  # PC形式
            r'^[\d/,:\s\u202f\u00a0APMapm.-]+-\s*([^~]+?):\s*(.+)$',   # スマホ形式
        ]
        
        message_found = False
        for pattern in time_patterns:
            match = re.match(pattern, line)
            if match:
                sender = match.group(1).strip()
                content = match.group(2).strip()
                
                # Exclude system messages and invalid speakers
                system_messages = [
                    'Photos', 'Videos', 'Audio', 'Message', 'Missed call', 'Canceled',
                    'Saved on', 'Chat history with', 'LINE', 'WhatsApp',
                    'Stickers', 'Location'
                ]
                
                # Content-based system message detection
                system_content_patterns = [
                    'unsent a message',
                    r'^\d{2}:\d{2}$',  # 時刻のみ
                    r'^Photos?$',
                    r'^Videos?$', 
                    r'^Audio$',
                    r'^Stickers?$'
                ]
                
                # Check if speaker is system message
                if sender in system_messages:
                    continue
                
                # Check content-based system messages
                is_system_content = False
                for sys_pattern in system_content_patterns:
                    if re.search(sys_pattern, content):
                        is_system_content = True
                        break
                if is_system_content:
                    continue
                
                # Exclude WhatsApp-specific system messages and unnecessary messages
                if ('end-to-end encrypted' in content.lower() or 
                    content.startswith('\u200e') or
                    content.lower().startswith('<media omitted>') or
                    content.lower().startswith('messages and calls are end-to-end encrypted') or
                    'this message was deleted' in content.lower() or
                    content.strip() == ''):
                    continue
                    
                speakers.add(sender)
                parsed_messages.append(f"{sender}: {content}")
                message_found = True
                break
        
        # Patterns for lines to exclude
        if not message_found:
            if (line.startswith('分析対象: ') or
                'Messages and calls are end-to-end encrypted' in line):
                continue
                
            # Process as continuation message
            if parsed_messages:
                parsed_messages[-1] += " " + line
    
    target_person = _determine_target_person(target_person, speakers)
    analysis_text = _extract_target_messages(parsed_messages, target_person)
    
    return target_person, analysis_text

async def _analyze_chat(request: ChatAnalysisRequest, parser, platform: str):
    if not request.chat_content.strip():
        raise HTTPException(status_code=400, detail="チャット履歴が必要です")
    
    additional_info_dict = _build_additional_info_dict(request)
    
    try:
        target_person, parsed_chat = parser(request.chat_content)
        
        if not parsed_chat.strip():
            raise HTTPException(
                status_code=400,
                detail="有効なチャット履歴を解析できませんでした。ファイル形式を確認してください。"
            )
        
        recommendations = await _process_chat_analysis(
            parsed_chat, target_person, additional_info_dict, platform
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except ValueError as e:
        raise _handle_chat_error(e, platform)
    except Exception as e:
        logger.exception("Unexpected error during %s chat analysis", platform)
        raise HTTPException(
            status_code=500,
            detail="チャット分析中に問題が発生しました。しばらく時間をおいてから再度お試しください。"
        )

@app.post("/analyze-line")
@limiter.limit(ANALYZE_RATE_LIMIT)
async def analyze_line_chat(request: Request, body: LineChatAnalysisRequest):
    """
    Analyze LINE chat history and generate gift recommendations
    
    Args:
        request: Incoming HTTP request (used for rate limiting)
        body: LINE chat analysis request
    
    Returns:
        User profile analysis and gift recommendations
    """
    return await _analyze_chat(body, parse_line_chat, "LINE")

@app.post("/analyze-whatsapp")
@limiter.limit(ANALYZE_RATE_LIMIT)
async def analyze_whatsapp_chat(request: Request, body: WhatsAppChatAnalysisRequest):
    """
    Analyze WhatsApp chat history and generate gift recommendations
    
    Args:
        request: Incoming HTTP request (used for rate limiting)
        body: WhatsApp chat analysis request
    
    Returns:
        User profile analysis and gift recommendations
    """
    return await _analyze_chat(body, parse_whatsapp_chat, "WhatsApp")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
