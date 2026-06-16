import { HeartIcon, SparklesIcon } from './components/Icons'
import { ProgressState } from './types'

interface HeartProgressProps extends ProgressState {}

export const HeartProgress = ({ progress, currentStep, isLoading }: HeartProgressProps) => {
  return (
    <div className="heart-progress-container">
      <div className="heart-progress-wrapper">
        {/* キラキラエフェクト */}
        <div className="sparkles-container">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="sparkle animate-sparkle"
              style={{
                left: `${20 + i * 12}%`,
                top: `${15 + (i % 2) * 15}%`,
                animationDelay: `${i * 0.3}s`,
              }}
            >
              <SparklesIcon className="w-4 h-4 text-yellow-400" />
            </div>
          ))}
        </div>

        {/* メインロゴプログレス */}
        <div className="heart-main">
          {/* 背景ロゴ */}
          <div className="heart-background">
            <img 
              src="/emotigift-logo.jpg" 
              alt="EmotiGift Logo" 
              className="heart-base opacity-20 w-[100px] h-[100px] rounded-2xl object-cover"
            />
          </div>

          {/* プログレス用のロゴ */}
          <div 
            className={`heart-progress ${isLoading ? 'animate-pulse-scale' : ''}`}
            style={{
              clipPath: `inset(${100 - progress}% 0 0 0)`,
            }}
          >
            <img 
              src="/emotigift-logo.jpg" 
              alt="EmotiGift Logo Progress" 
              className="heart-fill w-[100px] h-[100px] rounded-2xl object-cover"
            />
          </div>

          {/* プログレス数値 */}
          <div className="progress-percentage">
            <span className="animate-text-pulse">
              {Math.round(progress)}%
            </span>
          </div>
        </div>

        {/* ステップテキスト */}
        <p className="progress-step-text animate-text-pulse">
          {currentStep}
        </p>

        {/* 浮遊ハートエフェクト */}
        {isLoading && (
          <div className="floating-hearts">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="floating-heart animate-float-heart"
                style={{
                  left: `${30 + i * 20}%`,
                  animationDelay: `${i * 0.8}s`,
                }}
              >
                <HeartIcon className="w-6 h-6 text-pink-400" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}