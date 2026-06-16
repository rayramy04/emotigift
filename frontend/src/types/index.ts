// 共通の型定義

export interface UserProfile {
  interests: readonly string[];
  personality_traits: readonly string[];
  values: readonly string[];
}

export interface GiftRecommendation {
  name: string;
  reason: string;
  category: string;
  amazon_link?: string;
  rakuten_link?: string;
  yahoo_link?: string;
  amazon_keywords?: string;
  rakuten_keywords?: string;
  yahoo_keywords?: string;
}

// より厳密な型定義のための型ユニオン
export type AnalysisType = 'reddit' | 'line' | 'whatsapp';
export type BudgetRange = 'プチギフト' | '一般ギフト' | '特別ギフト';
export type Relationship = '恋人・パートナー' | '親友' | '友人' | '家族' | '同僚・仕事仲間';
export type Gender = '男性' | '女性' | 'その他';
export type Age = '10代' | '20代' | '30代' | '40代' | '50代以上';
export type Occasion = '誕生日' | 'クリスマス' | '記念日' | 'お祝い' | '感謝・お礼';

export interface ChatPlatformOptions {
  platform: 'line' | 'whatsapp';
  options: readonly string[];
}

export interface ButtonStyleConfig {
  baseClasses: string;
  activeClasses: string;
  inactiveClasses: string;
}

export interface AnalysisResult {
  user_profile: UserProfile;
  gift_recommendations: GiftRecommendation[];
}

// フォーム関連の型定義
export interface FormData {
  redditId: string;
  budgetRange: string;
  minBudget: string;
  maxBudget: string;
  relationship: string;
  gender: string;
  age: string;
  occasion: string;
  additionalInfo: string;
}

// プログレス関連の型定義
export interface ProgressState {
  progress: number;
  currentStep: string;
  isLoading: boolean;
}

// API関連の型定義
export interface APIError {
  status?: number;
  detail?: string | object;
}

// バリデーション関連の型定義
export interface ValidationState {
  budgetError: string;
  isValid: boolean;
}

// アイコンコンポーネントの型定義
export interface IconProps {
  className?: string;
}