import React, { useCallback } from 'react';

interface ChatUploadProps {
  platform: 'line' | 'whatsapp';
  chatContent: string;
  setChatContent: (content: string) => void;
  fileName: string;
  setFileName: (fileName: string) => void;
  loading: boolean;
}

export const ChatUpload: React.FC<ChatUploadProps> = ({
  platform,
  chatContent,
  setChatContent,
  fileName,
  setFileName,
  loading
}) => {
  const platformInfo = {
    line: {
      name: 'LINE',
      icon: '💬',
      formats: 'どんなファイル名でも対応（.txtのみ）',
      exportSteps: [
        'スマホ: トーク画面 → 右上の「≡」→「その他」→「トーク履歴を送信」',
        'PC: チャットルーム → 右上の「⋯」→「トークを保存」',
        'デバイスに保存'
      ],
      additionalSteps: []
    },
    whatsapp: {
      name: 'WhatsApp',
      icon: '💬',
      formats: 'どんなファイル名でも対応（.txtのみ）',
      exportSteps: [
        'チャット画面 → 設定メニュー → 「チャットをエクスポート」',
        '「メディアを含めない」を必ず選択',
        'デバイスに保存'
      ],
      additionalSteps: [
        {
          title: '2. ZIPファイルを解凍してテキストファイルを取得',
          steps: [
            'AndroidやiOSでも標準で解凍可能',
            '解凍後、.txtファイルをアップロードしてください',
            'ファイル名は何でもOK（内容から自動判定）'
          ]
        }
      ]
    }
  };

  const info = platformInfo[platform];

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // ファイル名の検証
    const validExtensions = ['.txt'];
    const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
    
    if (!validExtensions.includes(fileExtension)) {
      alert('対応形式は.txtファイルのみです。');
      event.target.value = '';
      return;
    }

    setFileName(file.name);
    
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setChatContent(content);
    };
    reader.readAsText(file, 'UTF-8');
  }, [setChatContent, setFileName]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      
      // ファイル名の検証
      const validExtensions = ['.txt'];
      const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
      
      if (!validExtensions.includes(fileExtension)) {
        alert('対応形式は.txtファイルのみです。');
        return;
      }

      setFileName(file.name);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setChatContent(content);
      };
      reader.readAsText(file, 'UTF-8');
    }
  }, [setChatContent, setFileName]);

  return (
    <div className="mb-8">
      <label className="block text-lg font-semibold text-gray-700 mb-2">
        {info.name}チャット履歴をアップロード
      </label>
      
      <div className="text-sm text-gray-600 mb-4 bg-rose-50 p-4 rounded-lg">
        <h4 className="font-semibold text-rose-800 mb-3">📝 {info.name}ファイルの準備方法</h4>
        
        <div className="mb-3">
          <strong className="text-rose-700">1. {info.name}からエクスポート</strong>
          <ul className="ml-4 mt-1 text-xs list-disc">
            {info.exportSteps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>

        {info.additionalSteps.map((section, index) => (
          <div key={index} className="mb-3">
            <strong className="text-rose-700">{section.title}</strong>
            <ul className="ml-4 mt-1 text-xs list-disc">
              {section.steps.map((step, stepIndex) => (
                <li key={stepIndex}>{step}</li>
              ))}
            </ul>
          </div>
        ))}
        
        <div className="bg-rose-50 border border-rose-200 rounded p-3 mt-3">
          <div className="text-xs text-rose-800">
            <div className="flex items-center mb-2">
              <span className="text-rose-600 mr-2">📁</span>
              <strong>アップロード要件</strong>
            </div>
            <ul className="ml-6 space-y-1 text-rose-700">
              <li>• <strong>対応形式:</strong> .txtファイルのみ</li>
              <li>• <strong>自動判定:</strong> チャット内容から分析対象を特定</li>
              <li>• <strong>1対1:</strong> 自動で相手を分析対象に設定</li>
              <li>• <strong>2人検出:</strong> 選択画面で分析対象を選択</li>
            </ul>
          </div>
        </div>
        
        <div className="bg-rose-50 border border-rose-200 rounded p-2 mt-3">
          <div className="flex items-start">
            <span className="text-rose-600 mr-2">⚠️</span>
            <div className="text-xs text-rose-800">
              <strong>重要:</strong> 一対一の個人チャットのみ対応しています。グループチャットは分析できません。
            </div>
          </div>
        </div>
        
        <div className="bg-rose-50 border border-rose-200 rounded p-2 mt-3">
          <div className="flex items-start">
            <span className="text-rose-600 mr-2">🔒</span>
            <div className="text-xs text-rose-800">
              <strong>プライバシー保護:</strong> アップロードされたファイルは分析後に自動削除され、サーバーに保存されません。
            </div>
          </div>
        </div>
      </div>

      <div 
        className={`border-2 border-dashed border-rose-300 rounded-xl p-8 text-center transition-colors ${
          loading ? 'bg-rose-50 opacity-50' : 'hover:border-rose-400 hover:bg-rose-50'
        }`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {chatContent ? (
          <div className="text-rose-600">
            <span className="text-2xl mb-2 block">✅</span>
            <p className="font-medium">ファイルがアップロードされました</p>
            <p className="text-sm text-gray-600 mt-1">
              <span className="font-medium">ファイル名:</span> {fileName}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {chatContent.length}文字のチャット履歴
            </p>
            <button
              type="button"
              onClick={() => {
                setChatContent('');
                setFileName('');
              }}
              className="mt-2 text-sm text-rose-600 hover:text-rose-800 underline"
              disabled={loading}
            >
              ファイルを削除
            </button>
          </div>
        ) : (
          <div>
            <span className="text-4xl mb-4 block">📎</span>
            <p className="text-lg font-medium text-gray-700 mb-2">
              ファイルをドラッグ&ドロップ
            </p>
            <p className="text-sm text-gray-500 mb-4">
              または
            </p>
            <label className="inline-block bg-rose-500 text-white px-6 py-2 rounded-lg cursor-pointer hover:bg-rose-600 transition-colors">
              ファイルを選択
              <input
                type="file"
                accept=".txt"
                className="hidden"
                onChange={handleFileUpload}
                disabled={loading}
              />
            </label>
          </div>
        )}
      </div>
    </div>
  );
};