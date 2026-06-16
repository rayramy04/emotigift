"""
検索しやすいキーワード生成・最適化スクリプト
AIが生成した具体的すぎるプレゼント名を、Amazon・楽天・Yahoo!で実際に商品が見つかる検索キーワードに変換
"""

import re
from typing import Dict, List, Tuple

class KeywordOptimizer:
    def __init__(self):
        # カテゴリごとの検索キーワードマッピング
        self.category_keywords = {
            # テクノロジー・ガジェット関連
            "プログラミング": ["プログラミング", "開発", "コーディング", "入門書", "技術書"],
            "開発": ["開発環境", "IDE", "エディタ", "開発ツール"],
            "ガジェット": ["スマート", "電子機器", "ガジェット", "アクセサリー"],
            "PC": ["パソコン", "PC周辺機器", "キーボード", "マウス", "モニター"],
            "音響": ["ヘッドホン", "イヤホン", "スピーカー", "オーディオ"],
            
            # 趣味・エンターテインメント
            "ゲーム": ["ゲーム", "コントローラー", "ゲーミング", "周辺機器"],
            "読書": ["本", "書籍", "小説", "漫画", "雑誌"],
            "映画": ["映画", "DVD", "Blu-ray", "ホームシアター"],
            "音楽": ["CD", "レコード", "音楽", "楽器"],
            "アニメ": ["アニメ", "フィギュア", "グッズ", "コレクション"],
            
            # 健康・フィットネス
            "フィットネス": ["フィットネス", "トレーニング", "運動", "ジム"],
            "健康": ["健康", "サプリ", "健康食品", "医療機器"],
            "スポーツ": ["スポーツ", "運動用品", "ウェア", "シューズ"],
            
            # ライフスタイル
            "料理": ["料理", "調理器具", "キッチン", "食材"],
            "インテリア": ["インテリア", "家具", "雑貨", "装飾"],
            "ファッション": ["ファッション", "服", "アクセサリー", "バッグ"],
            "美容": ["美容", "スキンケア", "コスメ", "化粧品"],
            
            # アウトドア・旅行
            "アウトドア": ["アウトドア", "キャンプ", "登山", "釣り"],
            "旅行": ["旅行", "トラベル", "旅行用品", "キャリー"],
            
            # 学習・自己啓発
            "学習": ["学習", "勉強", "教材", "参考書"],
            "語学": ["語学", "英語", "外国語", "辞書"],
            "資格": ["資格", "試験", "検定", "対策"],
        }
        
        # 具体的すぎるキーワードの一般化ルール
        self.generalization_rules = {
            # ブランド・型番を一般化
            r"(MacBook|Surface|ThinkPad|Dell|HP)\s*(Pro|Air|Book)?\s*\d*": "ノートパソコン",
            r"(iPhone|Galaxy|Pixel|Xperia)\s*\d*": "スマートフォン アクセサリー",
            r"(iPad|Surface|Galaxy Tab)\s*(Pro|Air)?\s*\d*": "タブレット アクセサリー",
            
            # 専門用語を一般化
            r"(React|Vue|Angular|Node\.js|Python|Java|JavaScript).*開発": "プログラミング 入門書",
            r"(Docker|Kubernetes|AWS|Azure).*環境": "クラウド 技術書",
            r"(Photoshop|Illustrator|Premiere|After Effects).*": "デザイン ソフト",
            
            # 過度に具体的な商品名を一般化
            r".*カスタマイズ.*キーボード": "メカニカルキーボード",
            r".*プロフェッショナル.*マウス": "ゲーミングマウス",
            r".*スタジオ.*ヘッドホン": "モニターヘッドホン",
            
            # 抽象的すぎる表現を具体化
            r".*創作.*支援.*ツール": "ペンタブレット",
            r".*学習.*環境.*システム": "学習机 セット",
            r".*健康.*管理.*システム": "スマートウォッチ",
            r".*音楽.*制作.*環境": "オーディオインターフェース",
        }
        
        # NGワード（検索結果が出にくいワード）
        self.ng_words = [
            "システム", "環境", "ソリューション", "プラットフォーム", "サービス",
            "体験", "カスタマイズ", "プロフェッショナル", "エクスペリエンス",
            "パーソナライズド", "最適化された", "高性能な", "革新的な"
        ]
    
    def optimize_keywords(self, gift_name: str, category: str = "") -> Dict[str, str]:
        """
        ギフト名を最適化して、Amazon・楽天・Yahoo!で検索しやすいキーワードに変換
        
        Args:
            gift_name: AIが生成したギフト名
            category: ギフトのカテゴリ（任意）
            
        Returns:
            Dict containing optimized keywords for Amazon and Rakuten
        """
        # 1. 一般化ルールを適用
        optimized = self._apply_generalization_rules(gift_name)
        
        # 2. NGワードを除去・置換
        optimized = self._remove_ng_words(optimized)
        
        # 3. カテゴリ情報を活用してキーワードを強化
        if category:
            optimized = self._enhance_with_category(optimized, category)
        
        # 4. 検索プラットフォーム別に最適化
        amazon_keywords = self._optimize_for_amazon(optimized)
        rakuten_keywords = self._optimize_for_rakuten(optimized)
        
        return {
            "amazon_keywords": amazon_keywords,
            "rakuten_keywords": rakuten_keywords,
            "original": gift_name,
            "base_optimized": optimized
        }
    
    def _apply_generalization_rules(self, text: str) -> str:
        """一般化ルールを適用"""
        for pattern, replacement in self.generalization_rules.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
    
    def _remove_ng_words(self, text: str) -> str:
        """NGワードを除去・置換"""
        for ng_word in self.ng_words:
            text = text.replace(ng_word, "")
        
        # 連続するスペースを整理
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _enhance_with_category(self, text: str, category: str) -> str:
        """カテゴリ情報でキーワードを強化"""
        for cat_key, keywords in self.category_keywords.items():
            if cat_key in category or any(keyword in text for keyword in keywords):
                # カテゴリに関連する検索しやすいキーワードを追加
                if not any(keyword in text for keyword in keywords):
                    text = f"{keywords[0]} {text}"
                break
        return text
    
    def _optimize_for_amazon(self, text: str) -> str:
        """Amazon検索用に最適化"""
        # Amazonで検索しやすい形式に調整
        text = text.replace("・", " ")
        text = re.sub(r'[（）()【】\[\]]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 長すぎる場合は重要なキーワードを抽出
        words = text.split()
        if len(words) > 5:
            # 重要そうなキーワードを優先
            important_words = []
            for word in words:
                if len(word) > 1 and not word in ['の', 'と', 'で', 'に', 'は', 'が']:
                    important_words.append(word)
                if len(important_words) >= 4:
                    break
            text = " ".join(important_words)
        
        return text
    
    def _optimize_for_rakuten(self, text: str) -> str:
        """楽天検索用に最適化（Amazonより日本語寄り）"""
        # 楽天は日本語検索に強いので、より自然な日本語表現を保持
        text = text.replace("・", " ")
        text = re.sub(r'[（）()【】\[\]]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 楽天特有の検索しやすいキーワードに調整
        text = text.replace("アクセサリー", "グッズ")
        text = text.replace("デバイス", "機器")
        
        return text
    
    def suggest_alternative_keywords(self, gift_name: str) -> List[str]:
        """
        検索がヒットしない場合の代替キーワード候補を提案
        """
        alternatives = []
        
        # 単語を分解して組み合わせパターンを生成
        words = re.findall(r'[ぁ-んァ-ヶ一-龯a-zA-Z]+', gift_name)
        
        if len(words) >= 2:
            # 順序を変えた組み合わせ
            alternatives.append(" ".join(words[::-1]))
            
            # 主要な単語のみ
            if len(words) > 2:
                alternatives.append(" ".join(words[:2]))
                alternatives.append(" ".join(words[-2:]))
        
        # カテゴリから類推
        for category, keywords in self.category_keywords.items():
            if any(keyword in gift_name for keyword in keywords):
                alternatives.extend(keywords[:3])
                break
        
        return list(set(alternatives))  # 重複除去

