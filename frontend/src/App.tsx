import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { HeartProgress } from './HeartProgress';
import { UserForm } from './components/UserForm';
import { ResultDisplay } from './components/ResultDisplay';
import { AnalysisResult } from './types';
import { BUDGET_CONFIG, UI_CONFIG, API_CONFIG, MESSAGES } from './constants/app';

type AnalysisType = 'reddit' | 'line' | 'whatsapp';
interface ChatRequestData {
  chat_content: string;
  min_budget: number;
  max_budget: number;
  relationship: string | null;
  gender: string | null;
  age: string | null;
  occasion: string | null;
  additional_info: string | null;
}

type SafeChatRequestLog = Omit<ChatRequestData, 'chat_content'> & {
  chat_content_length: number;
};

interface ProgressTimers {
  progressInterval: NodeJS.Timeout;
  stepTimers: NodeJS.Timeout[];
}

const getApiUrl = () => (
  process.env.NODE_ENV === 'production'
    ? process.env.REACT_APP_API_URL || 'https://emotigift-backend.onrender.com'
    : API_CONFIG.BASE_URL.DEVELOPMENT
);

const normalizeErrorDetail = (detail: unknown): string => {
  if (!detail) return '';

  if (typeof detail === 'object') {
    if (Array.isArray(detail)) {
      return detail.map(item =>
        typeof item === 'object' && item !== null
          ? (item as { msg?: string }).msg || JSON.stringify(item)
          : String(item)
      ).join('\n');
    }

    return (
      (detail as { msg?: string; message?: string }).msg ||
      (detail as { msg?: string; message?: string }).message ||
      JSON.stringify(detail)
    );
  }

  return String(detail);
};

const toSafeChatRequestLog = (requestData: ChatRequestData): SafeChatRequestLog => {
  const { chat_content, ...safeRequestData } = requestData;
  return {
    ...safeRequestData,
    chat_content_length: chat_content.length
  };
};

export default function App() {
  // State management
  const [analysisType, setAnalysisType] = useState<AnalysisType>('reddit');
  const [redditId, setRedditId] = useState('');
  const [lineChatContent, setLineChatContent] = useState('');
  const [lineChatFileName, setLineChatFileName] = useState('');
  const [whatsappChatContent, setWhatsappChatContent] = useState('');
  const [whatsappChatFileName, setWhatsappChatFileName] = useState('');
  const [targetPersonOptions, setTargetPersonOptions] = useState<{platform: 'line' | 'whatsapp', options: string[]} | null>(null);
  const [isAutoSubmitting, setIsAutoSubmitting] = useState(false);
  const [budgetRange, setBudgetRange] = useState('');
  const [minBudget, setMinBudget] = useState<string>(BUDGET_CONFIG.DEFAULT.MIN);
  const [maxBudget, setMaxBudget] = useState<string>(BUDGET_CONFIG.DEFAULT.MAX);
  const [relationship, setRelationship] = useState('');
  const [gender, setGender] = useState('');
  const [age, setAge] = useState('');
  const [occasion, setOccasion] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState('');
  const [budgetError, setBudgetError] = useState('');
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  
  // 分析中止用のAbortController
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // チャットコンテンツの最新値を同期的に追跡するためのRef
  const lineChatContentRef = useRef('');
  const whatsappChatContentRef = useRef('');

  const buildChatRequestData = useCallback((chatContent: string): ChatRequestData => ({
    chat_content: chatContent,
    min_budget: parseInt(minBudget) || 0,
    max_budget: parseInt(maxBudget) || 0,
    relationship: relationship || null,
    gender: gender || null,
    age: age || null,
    occasion: occasion || null,
    additional_info: additionalInfo.trim() || null
  }), [minBudget, maxBudget, relationship, gender, age, occasion, additionalInfo]);

  const appendOptionalAnalysisParams = useCallback((params: URLSearchParams) => {
    const minBudgetNum = parseInt(minBudget) || 0;
    const maxBudgetNum = parseInt(maxBudget) || 0;

    if (minBudgetNum > 0) {
      params.append('min_budget', minBudgetNum.toString());
    }

    if (maxBudgetNum > 0) {
      params.append('max_budget', maxBudgetNum.toString());
    }

    if (relationship) params.append('relationship', relationship);
    if (gender) params.append('gender', gender);
    if (age) params.append('age', age);
    if (occasion) params.append('occasion', occasion);
    if (additionalInfo.trim()) params.append('additional_info', additionalInfo.trim());
  }, [minBudget, maxBudget, relationship, gender, age, occasion, additionalInfo]);

  const startProgressTimers = useCallback((type: AnalysisType): ProgressTimers => {
    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + 5, 90));
    }, UI_CONFIG.TIMEOUTS.PROGRESS_ANIMATION_DELAY);

    const stepTimers: NodeJS.Timeout[] = [];

    if (type === 'reddit') {
      setCurrentStep(MESSAGES.STEPS.REDDIT_SEARCH);
      stepTimers.push(setTimeout(() => {
        setCurrentStep(MESSAGES.STEPS.POSTS_ANALYSIS);
      }, UI_CONFIG.TIMEOUTS.STEP_ANIMATION_DELAY));
    } else if (type === 'line') {
      setCurrentStep(MESSAGES.STEPS.LINE_ANALYSIS);
      stepTimers.push(setTimeout(() => {
        setCurrentStep(MESSAGES.STEPS.CONTENT_ANALYSIS);
      }, UI_CONFIG.TIMEOUTS.STEP_ANIMATION_DELAY));
    } else {
      setCurrentStep(MESSAGES.STEPS.WHATSAPP_ANALYSIS);
      stepTimers.push(setTimeout(() => {
        setCurrentStep(MESSAGES.STEPS.CONTENT_ANALYSIS);
      }, UI_CONFIG.TIMEOUTS.STEP_ANIMATION_DELAY));
    }

    stepTimers.push(
      setTimeout(() => {
        setCurrentStep(MESSAGES.STEPS.AI_ANALYSIS);
      }, 3000),
      setTimeout(() => {
        setCurrentStep(MESSAGES.STEPS.GIFT_SELECTION);
      }, 4500),
      setTimeout(() => {
        setCurrentStep(MESSAGES.STEPS.FINAL_ADJUSTMENT);
      }, UI_CONFIG.TIMEOUTS.FINAL_STEP_DELAY)
    );

    return { progressInterval, stepTimers };
  }, []);

  const clearProgressTimers = useCallback((timers: ProgressTimers) => {
    clearInterval(timers.progressInterval);
    timers.stepTimers.forEach(timer => clearTimeout(timer));
  }, []);

  // 予算のバリデーション
  const validateBudget = useCallback((min: string, max: string) => {
    const minNum = parseInt(min) || 0;
    const maxNum = parseInt(max) || 0;
    
    if (minNum > maxNum && maxNum > 0) {
      setBudgetError(MESSAGES.ERRORS.BUDGET_MIN_MAX);
      return false;
    } else if (minNum < 0 || maxNum < 0) {
      setBudgetError(MESSAGES.ERRORS.BUDGET_NEGATIVE);
      return false;
    } else {
      setBudgetError('');
      return true;
    }
  }, []);

  // 予算入力フィールド変更時の処理
  const handleMinBudgetChange = useCallback((value: string) => {
    setMinBudget(value);
    setBudgetRange(''); // カスタム入力時はタブ選択を解除
    setTimeout(() => validateBudget(value, maxBudget), UI_CONFIG.TIMEOUTS.BUDGET_VALIDATION_DELAY);
  }, [maxBudget, validateBudget]);

  const handleMaxBudgetChange = useCallback((value: string) => {
    setMaxBudget(value);
    setBudgetRange(''); // カスタム入力時はタブ選択を解除
    setTimeout(() => validateBudget(minBudget, value), UI_CONFIG.TIMEOUTS.BUDGET_VALIDATION_DELAY);
  }, [minBudget, validateBudget]);

  // 予算範囲選択時の処理
  const handleBudgetRangeSelect = useCallback((range: string) => {
    setBudgetRange(range);
    switch (range) {
      case BUDGET_CONFIG.PRESETS.PETIT_GIFT.LABEL:
        setMinBudget(BUDGET_CONFIG.PRESETS.PETIT_GIFT.MIN);
        setMaxBudget(BUDGET_CONFIG.PRESETS.PETIT_GIFT.MAX);
        break;
      case BUDGET_CONFIG.PRESETS.GENERAL_GIFT.LABEL:
        setMinBudget(BUDGET_CONFIG.PRESETS.GENERAL_GIFT.MIN);
        setMaxBudget(BUDGET_CONFIG.PRESETS.GENERAL_GIFT.MAX);
        break;
      case BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.LABEL:
        setMinBudget(BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.MIN);
        setMaxBudget(BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.MAX);
        break;
    }
    // 予算範囲選択時は予算バリデーションを即座に実行
    setTimeout(() => {
      const newMin = range === BUDGET_CONFIG.PRESETS.PETIT_GIFT.LABEL ? BUDGET_CONFIG.PRESETS.PETIT_GIFT.MIN : 
                     range === BUDGET_CONFIG.PRESETS.GENERAL_GIFT.LABEL ? BUDGET_CONFIG.PRESETS.GENERAL_GIFT.MIN : 
                     BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.MIN;
      const newMax = range === BUDGET_CONFIG.PRESETS.PETIT_GIFT.LABEL ? BUDGET_CONFIG.PRESETS.PETIT_GIFT.MAX : 
                     range === BUDGET_CONFIG.PRESETS.GENERAL_GIFT.LABEL ? BUDGET_CONFIG.PRESETS.GENERAL_GIFT.MAX : 
                     BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.MAX;
      validateBudget(newMin, newMax);
    }, 50);
  }, [validateBudget]);

  // 初期化時に予算バリデーションを実行
  useEffect(() => {
    validateBudget(minBudget, maxBudget);
  }, [minBudget, maxBudget, validateBudget]);

  // チャットコンテンツのrefを状態と同期
  useEffect(() => {
    lineChatContentRef.current = lineChatContent;
  }, [lineChatContent]);

  useEffect(() => {
    whatsappChatContentRef.current = whatsappChatContent;
  }, [whatsappChatContent]);


  // 分析中止ハンドラー
  const handleCancelAnalysis = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    // 状態をリセット
    setLoading(false);
    setProgress(0);
    setCurrentStep('');
    setError(MESSAGES.ANALYSIS.CANCELLED);
    // targetPersonOptions は中止時にリセットしない（再分析時に必要）
    setIsAutoSubmitting(false); // 自動実行フラグもリセット
  }, []);

  // ボタンが無効な理由を取得する関数
  const getButtonDisabledReason = useCallback(() => {
    if (loading) return null; // 分析中は理由を表示しない
    if (analysisType === 'reddit' && !redditId.trim()) return MESSAGES.VALIDATION.REDDIT_USERNAME_REQUIRED;
    if (analysisType === 'line' && !lineChatContent.trim()) return MESSAGES.VALIDATION.LINE_FILE_REQUIRED;
    if (analysisType === 'whatsapp' && !whatsappChatContent.trim()) return MESSAGES.VALIDATION.WHATSAPP_FILE_REQUIRED;
    if (budgetError) return MESSAGES.VALIDATION.BUDGET_VALIDATION;
    if (parseInt(minBudget) === 0 && parseInt(maxBudget) === 0) return MESSAGES.VALIDATION.BUDGET_INPUT_REQUIRED;
    return null;
  }, [loading, analysisType, redditId, lineChatContent, whatsappChatContent, budgetError, minBudget, maxBudget]);

  const requestAnalysis = useCallback(async (type: AnalysisType, chatContentOverride?: string): Promise<AnalysisResult> => {
    if (type === 'reddit') {
      const params = new URLSearchParams();
      params.append('reddit_id', redditId);
      appendOptionalAnalysisParams(params);

      const response = await axios.get(`${getApiUrl()}/analyze?${params.toString()}`, {
        signal: abortControllerRef.current?.signal
      });
      return response.data;
    }

    const chatContent = chatContentOverride ?? (type === 'line' ? lineChatContent : whatsappChatContent);
    const requestData = buildChatRequestData(chatContent);
    const endpoint = type === 'line' ? '/analyze-line' : '/analyze-whatsapp';

    if (type === 'line') {
      console.log('LINE Request Data:', JSON.stringify(toSafeChatRequestLog(requestData), null, 2));
    } else {
      console.log('WhatsApp Request Data:', JSON.stringify(toSafeChatRequestLog(requestData), null, 2));
    }

    const response = await axios.post(`${getApiUrl()}${endpoint}`, requestData, {
      signal: abortControllerRef.current?.signal
    });
    return response.data;
  }, [redditId, appendOptionalAnalysisParams, buildChatRequestData, lineChatContent, whatsappChatContent]);

  const handleAnalysisError = useCallback((err: any, type: AnalysisType, suppressTargetSelection = false) => {
    console.error('Error details:', err?.message || err);
    console.error('Error response:', JSON.stringify(err?.response?.data, null, 2));
    console.error('Error status:', err?.response?.status);
    console.error('Full error object:', err);

    if (err.name === 'AbortError' || err.code === 'ERR_CANCELED') {
      return;
    }

    const status = err.response?.status;
    const detail = normalizeErrorDetail(err.response?.data?.detail);

    if (status === 404) {
      setError(`🔍 ${detail}\n\n確認事項：\n• ユーザー名のスペルミスがないか\n• そのユーザーが実際に存在するか\n• 投稿履歴があるアクティブなアカウントか`);
    } else if (status === 403) {
      setError(`🔒 ${detail}\n\n対処法：\n• 別の公開アカウントを試してみてください\n• プライベート設定のアカウントは分析できません`);
    } else if (status === 429) {
      setError('⏰ API制限に達しました。\n\nしばらく時間をおいてから再度お試しください。');
    } else if (status === 504) {
      setError(`⏱️ ${detail}\n\n対処法：\n• ネットワーク接続を確認してください\n• 少し時間をおいてから再試行してください`);
    } else if (status === 503) {
      setError(`🔧 ${detail}\n\n対処法：\n• サービス側の一時的な問題です\n• 数分後に再度お試しください`);
    } else if (detail && detail.startsWith('TARGET_SELECTION_REQUIRED:')) {
      if (!targetPersonOptions && !suppressTargetSelection) {
        const options = detail.replace('TARGET_SELECTION_REQUIRED:', '').split('|');
        const platform = type === 'line' ? 'line' : 'whatsapp';
        setTargetPersonOptions({ platform, options });
        setError('');
      } else if (suppressTargetSelection) {
        setError('分析対象を特定できませんでした。チャット内容を確認してから再度お試しください。');
      }
    } else {
      setError(detail || 'エラーが発生しました。しばらく時間をおいてから再度お試しください。');
    }
  }, [targetPersonOptions]);

  const runAnalysis = useCallback(async (type: AnalysisType, chatContentOverride?: string, suppressTargetSelection = false) => {
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setError('');
    setResult(null);
    setProgress(0);
    setCurrentStep('');

    const progressTimers = startProgressTimers(type);
    let completed = false;

    try {
      const data = await requestAnalysis(type, chatContentOverride);

      clearProgressTimers(progressTimers);
      completed = true;

      setProgress(UI_CONFIG.PROGRESS.MAX_VALUE);
      setCurrentStep(MESSAGES.ANALYSIS.COMPLETED);

      setTimeout(() => {
        setResult(data);
      }, UI_CONFIG.TIMEOUTS.PROGRESS_ANIMATION_DELAY);
    } catch (err: any) {
      clearProgressTimers(progressTimers);
      handleAnalysisError(err, type, suppressTargetSelection);
    } finally {
      setLoading(false);
      setIsAutoSubmitting(false);
      abortControllerRef.current = null;

      if (!completed) {
        setProgress(0);
        setCurrentStep('');
      }
    }
  }, [requestAnalysis, startProgressTimers, clearProgressTimers, handleAnalysisError]);

  // Handle target person selection
  const handlePersonSelection = useCallback(async (person: string) => {
    if (!targetPersonOptions) return;
    
    // Store platform to avoid closure issues
    const platform = targetPersonOptions.platform;
    
    // Get latest content from ref synchronously
    const currentContent = platform === 'line' ? lineChatContentRef.current : whatsappChatContentRef.current;
    
    // Replace existing target line or add to beginning
    let updatedContent: string;
    if (currentContent.includes('分析対象: ')) {
      updatedContent = currentContent.replace(/^分析対象: .+$/m, `分析対象: ${person}`);
    } else {
      updatedContent = `分析対象: ${person}
${currentContent}`;
    }
    
    // 状態とrefを両方更新
    if (platform === 'line') {
      setLineChatContent(updatedContent);
      lineChatContentRef.current = updatedContent;
    } else {
      setWhatsappChatContent(updatedContent);
      whatsappChatContentRef.current = updatedContent;
    }
    
    setTargetPersonOptions(null);
    setIsAutoSubmitting(true);

    if (!loading) {
      runAnalysis(platform, updatedContent, true);
    }
  }, [targetPersonOptions, loading, runAnalysis]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 重複送信防止
    if (loading) {
      console.log('Analysis already in progress, ignoring duplicate request');
      return;
    }
    
    // 自動実行中の無限ループ防止
    if (isAutoSubmitting) {
      console.log('Auto-submit already in progress, ignoring duplicate request');
      return;
    }
    
    // バリデーション
    if (analysisType === 'reddit' && !redditId.trim()) {
      setError(MESSAGES.VALIDATION.REDDIT_USERNAME_REQUIRED_FORM);
      return;
    }

    if (analysisType === 'line' && !lineChatContent.trim()) {
      setError(MESSAGES.VALIDATION.LINE_FILE_REQUIRED_FORM);
      return;
    }

    if (analysisType === 'whatsapp' && !whatsappChatContent.trim()) {
      setError(MESSAGES.VALIDATION.WHATSAPP_FILE_REQUIRED_FORM);
      return;
    }

    if (!validateBudget(minBudget, maxBudget)) {
      return;
    }

    await runAnalysis(analysisType);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-rose-50 to-pink-100">
      <div className="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <header className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <img 
              src="/emotigift-logo.jpg" 
              alt="EmotiGift Logo" 
              className="w-24 h-24 md:w-28 md:h-28 lg:w-32 lg:h-32 rounded-2xl shadow-lg mr-6"
            />
            <h1 className="text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-bold bg-gradient-to-r from-rose-500 to-orange-500 bg-clip-text text-transparent">
              EmotiGift
            </h1>
          </div>
          <p className="text-xl md:text-2xl lg:text-3xl text-rose-800 font-medium mb-4">
            AIが読み解く、心に響くプレゼント
          </p>
          <p className="text-lg md:text-xl lg:text-2xl text-rose-700 mb-8">
            SNS・チャットから興味・価値観を分析し、あらゆるギフトシーンに対応したプレゼントを提案
          </p>
          <div className="flex flex-wrap justify-center gap-3 md:gap-4 text-sm md:text-base max-w-4xl mx-auto">
            <span className="bg-rose-50 text-rose-800 px-4 py-3 rounded-full border-2 border-rose-200 font-semibold shadow-sm hover:shadow-md transition-shadow">
              🔒 個人情報を保存しません
            </span>
            <span className="bg-rose-50 text-rose-800 px-4 py-3 rounded-full border-2 border-rose-200 font-semibold shadow-sm hover:shadow-md transition-shadow">
              🎯 他人向けギフト推薦に特化
            </span>
            <span className="bg-rose-50 text-rose-800 px-4 py-3 rounded-full border-2 border-rose-200 font-semibold shadow-sm hover:shadow-md transition-shadow">
              🛡️ プライバシー重視設計
            </span>
          </div>
        </header>

        <div className="max-w-4xl mx-auto">
          <UserForm
            analysisType={analysisType}
            setAnalysisType={setAnalysisType}
            redditId={redditId}
            setRedditId={setRedditId}
            lineChatContent={lineChatContent}
            setLineChatContent={setLineChatContent}
            lineChatFileName={lineChatFileName}
            setLineChatFileName={setLineChatFileName}
            whatsappChatContent={whatsappChatContent}
            setWhatsappChatContent={setWhatsappChatContent}
            whatsappChatFileName={whatsappChatFileName}
            setWhatsappChatFileName={setWhatsappChatFileName}
            budgetRange={budgetRange}
            setBudgetRange={setBudgetRange}
            minBudget={minBudget}
            setMinBudget={handleMinBudgetChange}
            maxBudget={maxBudget}
            setMaxBudget={handleMaxBudgetChange}
            handleBudgetRangeSelect={handleBudgetRangeSelect}
            relationship={relationship}
            setRelationship={setRelationship}
            gender={gender}
            setGender={setGender}
            age={age}
            setAge={setAge}
            occasion={occasion}
            setOccasion={setOccasion}
            additionalInfo={additionalInfo}
            setAdditionalInfo={setAdditionalInfo}
            budgetError={budgetError}
            loading={loading}
            onSubmit={handleSubmit}
            getButtonDisabledReason={getButtonDisabledReason}
            targetPersonOptions={targetPersonOptions}
          />

          {loading && (
            <div className="mt-6 bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-rose-100 p-4 max-w-md mx-auto">
              <HeartProgress
                progress={progress}
                currentStep={currentStep}
                isLoading={loading}
              />
              <div className="mt-4 text-center">
                <button
                  onClick={handleCancelAnalysis}
                  className="px-4 py-2 text-sm text-rose-600 hover:text-rose-800 hover:bg-rose-50 rounded-lg transition-colors border border-rose-200 hover:border-rose-300"
                >
                  ⏹️ 分析を中止
                </button>
              </div>
            </div>
          )}

          {targetPersonOptions && (
            <div className="mt-8 bg-rose-50 border-2 border-rose-200 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-rose-800 mb-4">
                🎯 分析対象者を選択してください
              </h3>
              <p className="text-rose-700 mb-4">
                チャット内容から2人の参加者が検出されました。プレゼントを贈りたい相手を選択してください：
              </p>
              <div className="flex flex-col gap-3">
                {targetPersonOptions.options.map((person, index) => (
                  <button
                    key={index}
                    className="px-6 py-3 bg-white text-rose-700 border-2 border-rose-300 rounded-xl hover:bg-rose-100 hover:border-rose-400 transition-colors font-medium text-left"
                    onClick={() => handlePersonSelection(person)}
                  >
                    <span className="text-xl mr-2">👤</span>
                    {person}
                  </button>
                ))}
              </div>
              <button
                className="mt-4 px-4 py-2 text-sm text-rose-600 hover:text-rose-800 underline"
                onClick={() => setTargetPersonOptions(null)}
              >
                キャンセル
              </button>
            </div>
          )}

          {error && (
            <div className="mt-8 bg-red-50 border-2 border-red-200 rounded-2xl p-6">
              <p className="text-red-700 whitespace-pre-line">{error}</p>
            </div>
          )}

          {result && <ResultDisplay result={result} />}
        </div>

        <footer className="mt-16 text-center text-rose-700">
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4 text-rose-800">EmotiGiftの特徴</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-rose-100 hover:border-rose-200 transition-colors">
                <div className="text-3xl mb-3">🔍</div>
                <h4 className="font-semibold mb-2 text-rose-800">深い理解</h4>
                <p className="text-sm text-rose-700">SNS・チャットから本当の興味や価値観を読み取ります</p>
              </div>
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-rose-100 hover:border-rose-200 transition-colors">
                <div className="text-3xl mb-3">🛡️</div>
                <h4 className="font-semibold mb-2 text-rose-800">プライバシー保護</h4>
                <p className="text-sm text-rose-700">個人情報を一切保存しない安心設計。分析後は即座に削除されます</p>
              </div>
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-rose-100 hover:border-rose-200 transition-colors">
                <div className="text-3xl mb-3">🎁</div>
                <h4 className="font-semibold mb-2 text-rose-800">他人向け特化</h4>
                <p className="text-sm text-rose-700">既存サービスと違い、他人の好みを推測してギフトを提案する専門AI</p>
              </div>
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-rose-100 hover:border-rose-200 transition-colors">
                <div className="text-3xl mb-3">💝</div>
                <h4 className="font-semibold mb-2 text-rose-800">感動体験</h4>
                <p className="text-sm text-rose-700">相手の心に響く、思い出に残るプレゼント選び</p>
              </div>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4 text-rose-800">よくある質問</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto text-left">
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-rose-100">
                <h4 className="font-semibold mb-2 text-rose-800">Q: どんなアカウント・チャット履歴が分析できますか？</h4>
                <p className="text-sm text-rose-700">A: Reddit（公開設定で投稿履歴があるアカウント）、LINE・WhatsApp（エクスポートしたチャット履歴ファイル）に対応しています。誕生日、クリスマス、記念日などあらゆるギフトシーンに対応できます。</p>
              </div>
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-rose-100">
                <h4 className="font-semibold mb-2 text-rose-800">Q: 分析にどのくらい時間がかかりますか？</h4>
                <p className="text-sm text-rose-700">A: 通常20〜30秒程度で完了します。投稿数が多い場合は、もう少し時間がかかることがあります。</p>
              </div>
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-rose-100">
                <h4 className="font-semibold mb-2 text-rose-800">Q: プライバシー・セキュリティは大丈夫？</h4>
                <p className="text-sm text-rose-700">A: <strong>完全にプライバシー重視設計</strong>です。個人情報は一切保存せず、分析後は即座にデータを削除。既存のレコメンドサービスと違い、あなたの購買履歴に影響されない純粋な他人向けギフト提案を実現しています。</p>
              </div>
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-rose-100">
                <h4 className="font-semibold mb-2 text-rose-800">Q: 提案されたギフトが合わない場合は？</h4>
                <p className="text-sm text-rose-700">A: 追加情報（関係性、年齢、シーンなど）を詳しく入力して再分析することで、より精度の高い提案が得られます。</p>
              </div>
            </div>
          </div>

          <div className="text-sm text-rose-600">
            <p className="mb-2">© 2024 EmotiGift - AIが導く、心に響くギフト選び</p>
            <p>Made with ❤️ for thoughtful gift giving</p>
          </div>
        </footer>
      </div>
    </div>
  );
}
