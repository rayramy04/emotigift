/**
 * アプリケーション全体で使用される定数
 */

// API設定
export const API_CONFIG = {
  // 開発/本番環境のベースURL
  BASE_URL: {
    DEVELOPMENT: 'http://localhost:8000',
    PRODUCTION: process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000'
  },
  
  // HTTPステータスコード
  STATUS_CODES: {
    NOT_FOUND: 404,
    FORBIDDEN: 403,
    TOO_MANY_REQUESTS: 429,
    GATEWAY_TIMEOUT: 504,
    SERVICE_UNAVAILABLE: 503
  }
} as const;

// 予算設定
export const BUDGET_CONFIG = {
  // デフォルト予算範囲
  DEFAULT: {
    MIN: '1000',
    MAX: '30000'
  },
  
  // プリセット予算範囲
  PRESETS: {
    PETIT_GIFT: {
      MIN: '1000',
      MAX: '5000',
      LABEL: 'プチギフト',
      DESCRIPTION: '1,000円〜5,000円'
    },
    GENERAL_GIFT: {
      MIN: '5000',
      MAX: '15000', 
      LABEL: '一般的なギフト',
      DESCRIPTION: '5,000円〜15,000円'
    },
    SPECIAL_GIFT: {
      MIN: '15000',
      MAX: '50000',
      LABEL: '特別なギフト', 
      DESCRIPTION: '15,000円〜50,000円'
    }
  }
} as const;

// UI設定
export const UI_CONFIG = {
  // タイムアウト設定（ミリ秒）
  TIMEOUTS: {
    BUDGET_VALIDATION_DELAY: 100,
    PROGRESS_ANIMATION_DELAY: 300,
    STEP_ANIMATION_DELAY: 1500,
    COMPLETION_DELAY: 3000,
    FINAL_STEP_DELAY: 6000
  },
  
  // 進行状況の設定
  PROGRESS: {
    MAX_VALUE: 100,
    ANIMATION_STEPS: [
      { delay: 1500, value: 20 },
      { delay: 1500, value: 40 }, 
      { delay: 1500, value: 60 },
      { delay: 3000, value: 80 },
      { delay: 4500, value: 95 },
      { delay: 6000, value: 100 }
    ]
  },
  
  // テキスト制限
  TEXT_LIMITS: {
    ADDITIONAL_INFO_MAX_LENGTH: 500,
    CHAT_CONTENT_PREVIEW_LENGTH: 100
  },
  
  // レスポンシブブレークポイント（Tailwind基準）
  BREAKPOINTS: {
    SM: '640px',
    MD: '768px', 
    LG: '1024px',
    XL: '1280px'
  }
} as const;

// アニメーション設定
export const ANIMATION_CONFIG = {
  // CSS transition durations（ミリ秒）
  DURATIONS: {
    FAST: 200,
    NORMAL: 300,
    SLOW: 500
  },
  
  // CSS transform scales
  SCALES: {
    HOVER: 1.02,
    ACTIVE: 0.98,
    BUTTON_ACTIVE: 1.05
  }
} as const;

// メッセージ定数
export const MESSAGES = {
  LOADING: {
    ANALYZING: '🤖 分析中...',
    DEFAULT: '✨ AIプレゼント分析を開始'
  },
  
  ERRORS: {
    BUDGET_MIN_MAX: '最大額は最小額より大きい値を入力してください',
    BUDGET_NEGATIVE: '予算は0円以上で入力してください',
    USER_NOT_FOUND: 'ユーザーが見つかりませんでした',
    ACCESS_DENIED: 'アクセスが拒否されました',
    RATE_LIMITED: 'リクエストが多すぎます。しばらくお待ちください',
    TIMEOUT: 'タイムアウトしました。再度お試しください',
    SERVER_ERROR: 'サーバーエラーが発生しました'
  },

  VALIDATION: {
    REDDIT_USERNAME_REQUIRED: 'Reddit ユーザー名を入力してください',
    LINE_FILE_REQUIRED: 'LINEチャットファイルをアップロードしてください',
    WHATSAPP_FILE_REQUIRED: 'WhatsAppチャットファイルをアップロードしてください',
    BUDGET_VALIDATION: '予算の設定を確認してください',
    BUDGET_INPUT_REQUIRED: '予算を入力してください',
    REDDIT_USERNAME_REQUIRED_FORM: 'Reddit ユーザー名を入力してください。',
    LINE_FILE_REQUIRED_FORM: 'LINEチャットファイルをアップロードしてください。',
    WHATSAPP_FILE_REQUIRED_FORM: 'WhatsAppチャットファイルをアップロードしてください。'
  },

  ANALYSIS: {
    CANCELLED: '分析を中止しました',
    COMPLETED: '✅ 分析完了！',
    ERROR: '分析中にエラーが発生しました。'
  },

  STEPS: {
    REDDIT_SEARCH: '🔍 Redditアカウント検索中...',
    POSTS_ANALYSIS: '📊 投稿・コメント分析中...',
    LINE_ANALYSIS: '💬 LINEチャット分析中...',
    WHATSAPP_ANALYSIS: '💬 WhatsAppチャット分析中...',
    CONTENT_ANALYSIS: '📊 会話内容分析中...',
    AI_ANALYSIS: '🧠 AI分析実行中...',
    GIFT_SELECTION: '🎁 プレゼント選定中...',
    FINAL_ADJUSTMENT: '✨ 最終調整中...'
  }
} as const;