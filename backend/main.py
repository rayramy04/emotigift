"""
EmotiGift API - Main Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from datetime import datetime
import re

from reddit_unified import UnifiedRedditService
from gift_service import GiftService

load_dotenv()

class LineChatAnalysisRequest(BaseModel):
    chat_content: str
    min_budget: Optional[int] = None
    max_budget: Optional[int] = None
    relationship: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    occasion: Optional[str] = None
    additional_info: Optional[str] = None

class WhatsAppChatAnalysisRequest(BaseModel):
    chat_content: str
    min_budget: Optional[int] = None
    max_budget: Optional[int] = None
    relationship: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    occasion: Optional[str] = None
    additional_info: Optional[str] = None

app = FastAPI()

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

env_origins = os.getenv("CORS_ORIGINS")
if env_origins:
    allowed_origins.extend(env_origins.split(","))

if os.getenv("ENVIRONMENT") == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

reddit_service = UnifiedRedditService()
gift_service = GiftService()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "EmotiGift API is running", "cors_origins": allowed_origins}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/analyze")
async def analyze_reddit_user(
    reddit_id: str,
    min_budget: int = None,
    max_budget: int = None,
    relationship: str = None,
    gender: str = None,
    age: str = None,
    occasion: str = None,
    additional_info: str = None
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
    if not reddit_id:
        raise HTTPException(status_code=400, detail="Reddit ID is required")
    
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
        
        recommendations = await gift_service.generate_recommendations(
            reddit_posts, reddit_id, additional_info_dict
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error for user {reddit_id}: {e}")
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
    return await gift_service.generate_recommendations(
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
            r'^\d{4}/\d{2}/\d/d\s+\d{1,2}:\d{2}\t(.+?)\t(.+)$',  # 日付付き形式
            r'^(.+?)\s+\d{1,2}:\d{2}\s+(.+)$',  # 名前-時刻-メッセージ形式
            # Generic pattern removed to prevent misrecognition
            # r'^(.+?)[\t\s]+(.+)$'  # 汎用的な名前-メッセージ形式（最後の手段）
        ]
        
        message_found = False
        for i, pattern in enumerate(time_patterns):
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
    
    # Debug information output
    print(f"DEBUG: LINE speakers detected: {speakers}")
    print(f"DEBUG: Number of speakers: {len(speakers)}")
    print(f"DEBUG: Parsed messages count: {len(parsed_messages)}")
    if len(speakers) > 2:
        print(f"WARNING: Detected {len(speakers)} speakers: {list(speakers)}")
        print("DEBUG: First few parsed messages:")
        for i, msg in enumerate(parsed_messages[:10]):
            print(f"  {i+1}: {msg}")
        print("DEBUG: Original lines that were processed:")
        for i, line in enumerate(lines[:20]):
            print(f"  Line {i+1}: '{line.strip()}'")
    
    # Additional check for abnormally high number of speakers
    if len(speakers) > 5:
        print(f"ERROR: Too many speakers detected ({len(speakers)}). This suggests parsing errors.")
        print(f"Speakers: {list(speakers)}")
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
            r'^\[[\d/,:\s\u202f\u00a0APM]+\]\s*([^~]+?):\s*(.+)$',  # PC形式
            r'^[\d/,:\s\u202f\u00a0-]+\s*-\s*([^~]+?):\s*(.+)$',   # スマホ形式
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

@app.post("/analyze-line")
async def analyze_line_chat(request: LineChatAnalysisRequest):
    """
    Analyze LINE chat history and generate gift recommendations
    
    Args:
        request: LINE chat analysis request
    
    Returns:
        User profile analysis and gift recommendations
    """
    if not request.chat_content.strip():
        raise HTTPException(status_code=400, detail="チャット履歴が必要です")
    
    additional_info_dict = _build_additional_info_dict(request)
    
    try:
        target_person, parsed_chat = parse_line_chat(request.chat_content)
        
        if not parsed_chat.strip():
            raise HTTPException(
                status_code=400,
                detail="有効なチャット履歴を解析できませんでした。ファイル形式を確認してください。"
            )
        
        recommendations = await _process_chat_analysis(
            parsed_chat, target_person, additional_info_dict, "LINE"
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except ValueError as e:
        error_message = str(e)
        if "TARGET_SELECTION_REQUIRED:" in error_message:
            raise HTTPException(status_code=400, detail=error_message)
        elif "グループトーク" in error_message:
            raise HTTPException(status_code=400, detail="📄 " + error_message + "\n\n💡 ヒント:\n• 必ず一対一の個人トークファイルをアップロードしてください\n• グループトークには対応していません")
        elif "特定できませんでした" in error_message:
            raise HTTPException(status_code=400, detail="📄 " + error_message + "\n\n💡 チャット内容の確認:\n• 十分な会話内容があることを確認してください\n• 一対一のチャットファイルかどうか確認してください\n• ファイルが正しくアップロードされているか確認してください")
        else:
            raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        print(f"Unexpected error during LINE chat analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="チャット分析中に問題が発生しました。しばらく時間をおいてから再度お試しください。"
        )

@app.post("/analyze-whatsapp")
async def analyze_whatsapp_chat(request: WhatsAppChatAnalysisRequest):
    """
    Analyze WhatsApp chat history and generate gift recommendations
    
    Args:
        request: WhatsApp chat analysis request
    
    Returns:
        User profile analysis and gift recommendations
    """
    if not request.chat_content.strip():
        raise HTTPException(status_code=400, detail="チャット履歴が必要です")
    
    additional_info_dict = _build_additional_info_dict(request)
    
    try:
        # 1. WhatsAppチャット履歴を解析
        target_person, parsed_chat = parse_whatsapp_chat(request.chat_content)
        
        if not parsed_chat.strip():
            raise HTTPException(
                status_code=400,
                detail="有効なチャット履歴を解析できませんでした。ファイル形式を確認してください。"
            )
        
        recommendations = await _process_chat_analysis(
            parsed_chat, target_person, additional_info_dict, "WhatsApp"
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except ValueError as e:
        error_message = str(e)
        if "TARGET_SELECTION_REQUIRED:" in error_message:
            raise HTTPException(status_code=400, detail=error_message)
        elif "グループチャット" in error_message:
            raise HTTPException(status_code=400, detail="📄 " + error_message + "\n\n💡 ヒント:\n• 必ず一対一のプライベートチャットファイルをアップロードしてください\n• グループチャットには対応していません")
        elif "特定できませんでした" in error_message:
            raise HTTPException(status_code=400, detail="📄 " + error_message + "\n\n💡 チャット内容の確認:\n• 十分な会話内容があることを確認してください\n• 一対一のチャットファイルかどうか確認してください\n• ファイルが正しくアップロードされているか確認してください")
        else:
            raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        print(f"Unexpected error during WhatsApp chat analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="チャット分析中に問題が発生しました。しばらく時間をおいてから再度お試しください。"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)