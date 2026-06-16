import React, { memo, useCallback } from 'react';
import { ChatUpload } from './ChatUpload';
import { createButtonClassGenerator, BUTTON_STYLES } from '../utils/buttonStyles';
import { BUDGET_CONFIG, UI_CONFIG } from '../constants/app';

interface UserFormProps {
  analysisType: 'reddit' | 'line' | 'whatsapp';
  setAnalysisType: (value: 'reddit' | 'line' | 'whatsapp') => void;
  redditId: string;
  setRedditId: (value: string) => void;
  lineChatContent: string;
  setLineChatContent: (value: string) => void;
  lineChatFileName: string;
  setLineChatFileName: (value: string) => void;
  whatsappChatContent: string;
  setWhatsappChatContent: (value: string) => void;
  whatsappChatFileName: string;
  setWhatsappChatFileName: (value: string) => void;
  budgetRange: string;
  setBudgetRange: (value: string) => void;
  minBudget: string;
  setMinBudget: (value: string) => void;
  maxBudget: string;
  setMaxBudget: (value: string) => void;
  handleBudgetRangeSelect: (range: string) => void;
  relationship: string;
  setRelationship: (value: string) => void;
  gender: string;
  setGender: (value: string) => void;
  age: string;
  setAge: (value: string) => void;
  occasion: string;
  setOccasion: (value: string) => void;
  additionalInfo: string;
  setAdditionalInfo: (value: string) => void;
  budgetError: string;
  loading: boolean;
  onSubmit: (e: React.FormEvent) => void;
  getButtonDisabledReason: () => string | null;
  targetPersonOptions: {platform: 'line' | 'whatsapp', options: string[]} | null;
}

const UserFormComponent: React.FC<UserFormProps> = ({
  analysisType,
  setAnalysisType,
  redditId,
  setRedditId,
  lineChatContent,
  setLineChatContent,
  lineChatFileName,
  setLineChatFileName,
  whatsappChatContent,
  setWhatsappChatContent,
  whatsappChatFileName,
  setWhatsappChatFileName,
  budgetRange,
  setBudgetRange,
  minBudget,
  setMinBudget,
  maxBudget,
  setMaxBudget,
  handleBudgetRangeSelect,
  relationship,
  setRelationship,
  gender,
  setGender,
  age,
  setAge,
  occasion,
  setOccasion,
  additionalInfo,
  setAdditionalInfo,
  budgetError,
  loading,
  onSubmit,
  getButtonDisabledReason,
  targetPersonOptions,
}) => {
  const getBudgetButtonClass = useCallback(
    (range: string) => createButtonClassGenerator(BUTTON_STYLES.BUDGET, budgetRange)(range),
    [budgetRange]
  );

  const getAnalysisTypeButtonClass = useCallback(
    (type: string) => createButtonClassGenerator(BUTTON_STYLES.ANALYSIS_TYPE, analysisType)(type),
    [analysisType]
  );

  return (
    <form onSubmit={onSubmit} className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-xl border border-rose-100 p-6 md:p-8 lg:p-10">
      {/* 分析タイプ選択 */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-2">🔍</span>
          <h3 className="text-xl font-semibold text-gray-700">分析タイプを選択</h3>
        </div>
        <p className="text-sm text-gray-600 mb-6">
          分析したいプラットフォームを選択してください
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            type="button"
            className={getAnalysisTypeButtonClass('reddit')}
            onClick={() => setAnalysisType('reddit')}
            disabled={loading}
          >
            <div className="flex items-center justify-center">
              <span className="text-2xl mr-2">📱</span>
              <div>
                <div>SNS分析</div>
                <div className="text-sm opacity-80">ユーザー名で投稿を分析</div>
              </div>
            </div>
          </button>
          <button
            type="button"
            className={getAnalysisTypeButtonClass('line')}
            onClick={() => setAnalysisType('line')}
            disabled={loading}
          >
            <div className="flex items-center justify-center">
              <span className="text-2xl mr-2">💬</span>
              <div>
                <div>LINE分析</div>
                <div className="text-sm opacity-80">チャット履歴を分析</div>
              </div>
            </div>
          </button>
          <button
            type="button"
            className={getAnalysisTypeButtonClass('whatsapp')}
            onClick={() => setAnalysisType('whatsapp')}
            disabled={loading}
          >
            <div className="flex items-center justify-center">
              <span className="text-2xl mr-2">💬</span>
              <div>
                <div>WhatsApp分析</div>
                <div className="text-sm opacity-80">チャット履歴を分析</div>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Reddit入力フィールド */}
      {analysisType === 'reddit' && (
        <div className="mb-8">
          <label htmlFor="reddit-id" className="block text-lg font-semibold text-gray-700 mb-2">
            SNS ユーザー名を入力（現在はRedditのみ対応）
          </label>
          <input
            type="text"
            id="reddit-id"
            value={redditId}
            onChange={(e) => setRedditId(e.target.value)}
            placeholder="例: spez"
            className="w-full px-4 py-3 text-lg border-2 border-rose-200 rounded-xl focus:border-rose-400 focus:outline-none transition-colors disabled:bg-rose-50 disabled:text-rose-400"
            disabled={loading}
          />
        </div>
      )}

      {/* LINEファイルアップロード */}
      {analysisType === 'line' && (
        <ChatUpload
          platform="line"
          chatContent={lineChatContent}
          setChatContent={setLineChatContent}
          fileName={lineChatFileName}
          setFileName={setLineChatFileName}
          loading={loading}
        />
      )}

      {/* WhatsAppファイルアップロード */}
      {analysisType === 'whatsapp' && (
        <ChatUpload
          platform="whatsapp"
          chatContent={whatsappChatContent}
          setChatContent={setWhatsappChatContent}
          fileName={whatsappChatFileName}
          setFileName={setWhatsappChatFileName}
          loading={loading}
        />
      )}

      <div className="mb-8">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-2">💰</span>
          <h3 className="text-xl font-semibold text-rose-800">予算範囲</h3>
        </div>
        <p className="text-sm text-rose-700 mb-4">
          プリセットボタンをクリックするか、下の入力欄で金額を直接指定してください。
          <br />
          <small>※ 直接入力するとプリセット選択は解除されます</small>
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <button
            type="button"
            className={getBudgetButtonClass(BUDGET_CONFIG.PRESETS.PETIT_GIFT.LABEL)}
            onClick={() => handleBudgetRangeSelect(BUDGET_CONFIG.PRESETS.PETIT_GIFT.LABEL)}
            disabled={loading}
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center">
                <span className="text-lg mr-2">🎁</span>
                <div className="text-left">
                  <div>{BUDGET_CONFIG.PRESETS.PETIT_GIFT.LABEL}</div>
                  <div className="text-xs opacity-80">{BUDGET_CONFIG.PRESETS.PETIT_GIFT.DESCRIPTION}</div>
                </div>
              </div>
              {budgetRange === BUDGET_CONFIG.PRESETS.PETIT_GIFT.LABEL && (
                <span className="text-lg ml-2">✓</span>
              )}
            </div>
          </button>
          <button
            type="button"
            className={getBudgetButtonClass(BUDGET_CONFIG.PRESETS.GENERAL_GIFT.LABEL)}
            onClick={() => handleBudgetRangeSelect(BUDGET_CONFIG.PRESETS.GENERAL_GIFT.LABEL)}
            disabled={loading}
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center">
                <span className="text-lg mr-2">💝</span>
                <div className="text-left">
                  <div>{BUDGET_CONFIG.PRESETS.GENERAL_GIFT.LABEL}</div>
                  <div className="text-xs opacity-80">{BUDGET_CONFIG.PRESETS.GENERAL_GIFT.DESCRIPTION}</div>
                </div>
              </div>
              {budgetRange === BUDGET_CONFIG.PRESETS.GENERAL_GIFT.LABEL && (
                <span className="text-lg ml-2">✓</span>
              )}
            </div>
          </button>
          <button
            type="button"
            className={getBudgetButtonClass(BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.LABEL)}
            onClick={() => handleBudgetRangeSelect(BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.LABEL)}
            disabled={loading}
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center">
                <span className="text-lg mr-2">💎</span>
                <div className="text-left">
                  <div>{BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.LABEL}</div>
                  <div className="text-xs opacity-80">{BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.DESCRIPTION}</div>
                </div>
              </div>
              {budgetRange === BUDGET_CONFIG.PRESETS.SPECIAL_GIFT.LABEL && (
                <span className="text-lg ml-2">✓</span>
              )}
            </div>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-rose-700 mb-1">
              最小額（円）
            </label>
            <input
              type="number"
              value={minBudget}
              onChange={(e) => setMinBudget(e.target.value)}
              className="w-full px-4 py-3 border-2 border-rose-200 rounded-xl focus:border-rose-400 focus:outline-none transition-colors disabled:bg-rose-50"
              placeholder={BUDGET_CONFIG.DEFAULT.MIN}
              min="0"
              disabled={loading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-rose-700 mb-1">
              最大額（円）
            </label>
            <input
              type="number"
              value={maxBudget}
              onChange={(e) => setMaxBudget(e.target.value)}
              className="w-full px-4 py-3 border-2 border-rose-200 rounded-xl focus:border-rose-400 focus:outline-none transition-colors disabled:bg-rose-50"
              placeholder={BUDGET_CONFIG.DEFAULT.MAX}
              min="0"
              disabled={loading}
            />
          </div>
        </div>
        {budgetError && (
          <p className="mt-2 text-sm text-red-600 flex items-center">
            <span className="mr-1">⚠️</span> {budgetError}
          </p>
        )}
      </div>

      <div className="mb-8">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-2">🎯</span>
          <h3 className="text-xl font-semibold text-gray-700">その他の情報（任意）</h3>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          より精度の高い提案のために、追加情報を入力できます。
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-rose-700 mb-1">
              関係性
            </label>
            <select
              value={relationship}
              onChange={(e) => setRelationship(e.target.value)}
              className="w-full px-4 py-3 border-2 border-rose-200 rounded-xl focus:border-rose-400 focus:outline-none transition-colors disabled:bg-rose-50"
              disabled={loading}
            >
              <option value="">選択してください</option>
              <option value="恋人・パートナー">恋人・パートナー</option>
              <option value="親友">親友</option>
              <option value="友人">友人</option>
              <option value="家族">家族</option>
              <option value="同僚・仕事仲間">同僚・仕事仲間</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-rose-700 mb-1">
              性別
            </label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="w-full px-4 py-3 border-2 border-rose-200 rounded-xl focus:border-rose-400 focus:outline-none transition-colors disabled:bg-rose-50"
              disabled={loading}
            >
              <option value="">選択してください</option>
              <option value="男性">男性</option>
              <option value="女性">女性</option>
              <option value="その他">その他</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-rose-700 mb-1">
              年代
            </label>
            <select
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="w-full px-4 py-3 border-2 border-rose-200 rounded-xl focus:border-rose-400 focus:outline-none transition-colors disabled:bg-rose-50"
              disabled={loading}
            >
              <option value="">選択してください</option>
              <option value="10代">10代</option>
              <option value="20代">20代</option>
              <option value="30代">30代</option>
              <option value="40代">40代</option>
              <option value="50代以上">50代以上</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-rose-700 mb-1">
              シーン
            </label>
            <select
              value={occasion}
              onChange={(e) => setOccasion(e.target.value)}
              className="w-full px-4 py-3 border-2 border-rose-200 rounded-xl focus:border-rose-400 focus:outline-none transition-colors disabled:bg-rose-50"
              disabled={loading}
            >
              <option value="">選択してください</option>
              <option value="誕生日">誕生日</option>
              <option value="クリスマス">クリスマス</option>
              <option value="記念日">記念日</option>
              <option value="お祝い">お祝い</option>
              <option value="感謝・お礼">感謝・お礼</option>
            </select>
          </div>
        </div>
      </div>

      <div className="mb-8">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-2">📝</span>
          <h3 className="text-xl font-semibold text-gray-700">その人に関する追加情報（任意）</h3>
        </div>
        <p className="text-sm text-rose-700 mb-4">
          💡 その人の趣味、最近の出来事、好きなもの、ライフスタイルなど、プレゼント選びに役立つ情報があれば自由に入力してください
          <br />
          <small className="text-rose-600">※ 詳しく入力するほど精度が向上します（最大{UI_CONFIG.TEXT_LIMITS.ADDITIONAL_INFO_MAX_LENGTH}文字）</small>
        </p>
        
        
        <textarea
          value={additionalInfo}
          onChange={(e) => setAdditionalInfo(e.target.value)}
          className="w-full px-4 py-3 border-2 border-rose-200 rounded-xl focus:border-rose-400 focus:outline-none transition-colors disabled:bg-rose-50 resize-y min-h-[120px]"
          placeholder="例: 12月のクリスマスプレゼント、最近転職して在宅ワークになった、猫を2匹飼っている、コーヒーにこだわりがあり手動ドリップをしている、実用的なものより癒しグッズが好み、など..."
          disabled={loading}
          maxLength={UI_CONFIG.TEXT_LIMITS.ADDITIONAL_INFO_MAX_LENGTH}
        />
        
        <div className="flex justify-end mt-2">
          <span className="text-xs text-rose-500">
            {additionalInfo.length}/{UI_CONFIG.TEXT_LIMITS.ADDITIONAL_INFO_MAX_LENGTH}文字
          </span>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !!getButtonDisabledReason()}
        className="w-full py-4 rounded-xl font-bold text-lg text-white bg-gradient-to-r from-rose-500 to-orange-500 hover:from-rose-600 hover:to-orange-600 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] shadow-xl hover:shadow-2xl border-2 border-rose-400 hover:border-rose-500 disabled:border-gray-400"
      >
        {loading ? '🤖 分析中...' : '✨ AIプレゼント分析を開始'}
      </button>

      {getButtonDisabledReason() && !loading && (
        <p className="mt-2 text-sm text-rose-700 text-center">
          💡 {getButtonDisabledReason()}
        </p>
      )}
    </form>
  );
};

export const UserForm = memo(UserFormComponent);