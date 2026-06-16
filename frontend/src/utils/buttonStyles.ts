/**
 * ボタンスタイル生成ユーティリティ
 * 重複していたボタンクラス生成ロジックを統合
 */

interface ButtonStyleConfig {
  baseClasses: string;
  activeClasses: string;
  inactiveClasses: string;
}

/**
 * ボタンクラス生成関数を作成
 * @param config - ボタンスタイル設定
 * @param currentValue - 現在選択されている値
 * @returns ボタンクラス生成関数
 */
export const createButtonClassGenerator = (config: ButtonStyleConfig, currentValue: string) => {
  return (value: string): string => {
    const { baseClasses, activeClasses, inactiveClasses } = config;
    return `${baseClasses} ${currentValue === value ? activeClasses : inactiveClasses}`;
  };
};

// 共通のスタイル定数
export const BUTTON_STYLES = {
  // 分析タイプボタン用
  ANALYSIS_TYPE: {
    baseClasses: 'px-6 py-3 rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-base',
    activeClasses: 'bg-gradient-to-r from-rose-500 to-orange-500 text-white shadow-xl border-2 border-rose-400 transform scale-105 ring-2 ring-rose-300',
    inactiveClasses: 'bg-white text-rose-700 hover:bg-rose-50 border-2 border-rose-200 hover:border-rose-300 shadow-md hover:shadow-lg'
  },
  
  // 予算ボタン用
  BUDGET: {
    baseClasses: 'px-4 py-3 rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-w-[160px] flex-1',
    activeClasses: 'bg-gradient-to-r from-rose-500 to-orange-500 text-white shadow-xl border-2 border-rose-400 transform scale-105 ring-2 ring-rose-300',
    inactiveClasses: 'bg-white text-rose-700 hover:bg-rose-50 border-2 border-rose-200 hover:border-rose-300 shadow-md hover:shadow-lg'
  }
} as const;