import React, { memo } from 'react';
import { AnalysisResult } from '../types';

interface ResultDisplayProps {
  result: AnalysisResult;
}

const ResultDisplayComponent: React.FC<ResultDisplayProps> = ({ result }) => {
  return (
    <div className="mt-8 space-y-8">
      <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-xl border border-rose-100 p-6 md:p-8">
        <h2 className="text-2xl font-bold text-rose-900 mb-6 flex items-center">
          <span className="mr-3">👤</span>
          ユーザープロフィール分析
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-rose-50 to-orange-50 rounded-2xl p-6 border border-rose-100">
            <h3 className="text-lg font-semibold text-rose-800 mb-4 flex items-center">
              <span className="mr-2">✨</span>
              興味・関心
            </h3>
            <div className="flex flex-wrap gap-2">
              {result.user_profile.interests.map((interest, index) => (
                <span 
                  key={index} 
                  className="px-3 py-2 bg-white text-rose-700 rounded-xl text-sm font-medium shadow-sm border border-rose-200 break-words max-w-full"
                  style={{ wordBreak: 'break-word', hyphens: 'auto' }}
                >
                  {interest}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl p-6 border border-orange-100">
            <h3 className="text-lg font-semibold text-orange-800 mb-4 flex items-center">
              <span className="mr-2">🎯</span>
              性格・特徴
            </h3>
            <div className="flex flex-wrap gap-2">
              {result.user_profile.personality_traits.map((trait, index) => (
                <span 
                  key={index} 
                  className="px-3 py-2 bg-white text-orange-700 rounded-xl text-sm font-medium shadow-sm border border-orange-200 break-words max-w-full"
                  style={{ wordBreak: 'break-word', hyphens: 'auto' }}
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-2xl p-6 border border-amber-100">
            <h3 className="text-lg font-semibold text-amber-800 mb-4 flex items-center">
              <span className="mr-2">💎</span>
              価値観
            </h3>
            <div className="flex flex-wrap gap-2">
              {result.user_profile.values.map((value, index) => (
                <span 
                  key={index} 
                  className="px-3 py-2 bg-white text-amber-700 rounded-xl text-sm font-medium shadow-sm border border-amber-200 break-words max-w-full"
                  style={{ wordBreak: 'break-word', hyphens: 'auto' }}
                >
                  {value}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-xl border border-rose-100 p-6 md:p-8">
        <h2 className="text-2xl font-bold text-rose-900 mb-6 flex items-center">
          <span className="mr-3">🎁</span>
          AIおすすめプレゼント
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {result.gift_recommendations.map((gift, index) => (
            <div 
              key={index} 
              className="relative bg-gradient-to-br from-rose-50 to-orange-50 rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 border-2 border-rose-100 hover:border-rose-200 transform hover:scale-[1.02]"
            >
              {/* 最推奨バッジ */}
              {index === 0 && (
                <div className="absolute -top-3 -right-3 bg-gradient-to-r from-yellow-400 to-orange-400 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                  最推奨
                </div>
              )}
              
              {/* ランキング番号 */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-rose-400 to-pink-400 text-white rounded-full flex items-center justify-center font-bold text-sm">
                    {index + 1}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-rose-900 leading-tight">{gift.name}</h3>
                  </div>
                </div>
              </div>

              {/* カテゴリと価格帯 */}
              <div className="flex items-center gap-2 mb-4">
                <span className="inline-block px-3 py-1 bg-gradient-to-r from-orange-100 to-rose-100 text-orange-700 rounded-full text-xs font-medium border border-orange-200">
                  📦 カテゴリ
                </span>
                <span className="text-rose-700 font-medium text-sm">
                  {gift.category}
                </span>
              </div>
              
              {/* 推薦理由セクション */}
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 mb-6 border border-rose-100">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-pink-500">💝</span>
                  <span className="text-sm font-semibold text-rose-700">推薦理由</span>
                </div>
                <div className="text-rose-800 text-sm leading-relaxed">
                  {gift.reason.split('。').filter(sentence => sentence.trim()).slice(0, 2).map((sentence, sentenceIndex) => (
                    <p key={sentenceIndex} className="mb-2 last:mb-0">
                      {sentence.trim()}。
                    </p>
                  ))}
                </div>
              </div>

              {/* 特別なポイント */}
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-3 mb-6 border border-yellow-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-yellow-600">✨</span>
                  <span className="text-xs font-semibold text-yellow-700">特別なポイント</span>
                </div>
                <p className="text-yellow-800 text-xs">
                  {index === 0 ? "誕生日をより楽しく過ごせる" : 
                   index === 1 ? "実用性と特別感を両立" : 
                   "サプライズ効果抜群"}
                </p>
              </div>
              
              {/* ショッピングボタン */}
              <div className="flex flex-col gap-2">
                {gift.amazon_link && (
                  <a 
                    href={gift.amazon_link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-full py-3 px-4 bg-gradient-to-r from-orange-400 to-red-400 hover:from-orange-500 hover:to-red-500 text-white rounded-xl font-medium text-center transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                  >
                    <span className="text-lg">🛒</span>
                    Amazonで探す
                  </a>
                )}
                {gift.rakuten_link && (
                  <a 
                    href={gift.rakuten_link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-full py-3 px-4 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white rounded-xl font-medium text-center transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                  >
                    <span className="text-lg">🛍️</span>
                    楽天で探す
                  </a>
                )}
                {gift.yahoo_link && (
                  <a 
                    href={gift.yahoo_link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-full py-3 px-4 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white rounded-xl font-medium text-center transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                  >
                    <span className="text-lg">🔍</span>
                    Yahoo!で探す
                  </a>
                )}
              </div>
              
              {/* 検索キーワード表示 */}
              <div className="mt-4 pt-4 border-t border-rose-200">
                <div className="flex items-center gap-2 text-xs text-rose-600">
                  <span>🔍</span>
                  <span>検索キーワード: 「{gift.amazon_keywords || gift.name}」</span>
                </div>
                <p className="text-xs text-rose-500 mt-1">※外部サイトに遷移します。価格や在庫状況は各サイトでご確認ください。</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const ResultDisplay = memo(ResultDisplayComponent);