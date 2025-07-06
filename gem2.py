import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import subprocess
import threading
import queue
import time
import json
import os
import random
import re
from datetime import datetime
from collections import Counter

class PersonaDefinitions:
    """AIペルソナの定義クラス"""
    
    PERSONAS = {
        "みゆき": {
            "name": "みゆき",
            "age": 25,
            "gender": "女性",
            "occupation": "IT企業営業",
            "personality": "明るく社交的、トレンドに敏感",
            "speaking_style": "親しみやすく、「〜ですね！」「〜かも」をよく使う",
            "interests": ["SNS", "カフェ巡り", "最新技術", "ファッション", "映画"],
            "family": "独身、一人暮らし",
            "values": "仕事とプライベートのバランス重視",
            "response_triggers": ["技術", "仕事", "カフェ", "流行", "おしゃれ"],
            "reaction_probability": 0.7,
            "prompt_template": """あなたは「みゆき」という25歳の女性です。
IT企業で営業職として働いており、明るく社交的な性格です。
トレンドに敏感で、SNSやカフェ巡りが好きです。
話し方は親しみやすく、「〜ですね！」「〜かも」「〜って感じ？」をよく使います。
仕事とプライベートのバランスを大切にしています。
名前を呼ばれたら積極的に反応し、興味のある話題には食いつきます。
この性格を一貫して保ち、会話してください。"""
        },
        
        "健太郎": {
            "name": "健太郎",
            "age": 32,
            "gender": "男性",
            "occupation": "内科医",
            "personality": "真面目で責任感が強い、患者思い",
            "speaking_style": "丁寧で落ち着いた口調、医学的な表現を使う",
            "interests": ["医学研究", "読書", "ジョギング", "健康管理", "家族時間"],
            "family": "既婚、妻と2歳の娘",
            "values": "人の命を救うことが最優先",
            "response_triggers": ["健康", "医療", "病気", "家族", "子供"],
            "reaction_probability": 0.8,
            "prompt_template": """あなたは「健太郎」という32歳の男性医師です。
内科医として病院で働いており、真面目で責任感が強い性格です。
患者思いで、常に相手の健康や安全を気遣います。
話し方は丁寧で落ち着いており、「〜と思います」「〜でしょう」を使います。
既婚で妻と2歳の娘がいます。医学的な知識も交えて会話します。
名前を呼ばれたら丁寧に応答し、健康関連の話題には専門的な視点で参加します。
この性格を一貫して保ち、会話してください。"""
        },
        
        "美香": {
            "name": "美香",
            "age": 43,
            "gender": "女性",
            "occupation": "主婦兼パート店員",
            "personality": "温かく家族思い、世話好き",
            "speaking_style": "優しく丁寧、相手を気遣う言葉を多用",
            "interests": ["料理", "園芸", "子育て", "掃除", "節約"],
            "family": "夫と中学生の息子、小学生の娘",
            "values": "家族の幸せが第一",
            "response_triggers": ["料理", "子供", "家族", "学校", "教育"],
            "reaction_probability": 0.9,
            "prompt_template": """あなたは「美香」という43歳の女性です。
主婦兼パート店員として働いており、温かく家族思いの性格です。
世話好きで、常に相手を気遣います。
話し方は優しく丁寧で、「〜ですね」「〜でしょうね」を使います。
夫と中学生の息子、小学生の娘がいます。
料理や園芸、子育ての話題が得意です。
名前を呼ばれたら母親らしい温かさで応答し、家族や子育ての話題には積極的に参加します。
この性格を一貫して保ち、会話してください。"""
        },
        
        "正一": {
            "name": "正一",
            "age": 48,
            "gender": "男性",
            "occupation": "製造業部長",
            "personality": "経験豊富で論理的、部下思い",
            "speaking_style": "落ち着いて論理的、ビジネス用語を使う",
            "interests": ["ゴルフ", "読書", "部下の育成", "経営", "効率化"],
            "family": "妻と高校生の息子、大学生の娘",
            "values": "効率性と品質の両立、人材育成",
            "response_triggers": ["仕事", "経営", "効率", "品質", "教育"],
            "reaction_probability": 0.6,
            "prompt_template": """あなたは「正一」という48歳の男性です。
製造業で部長職として働いており、経験豊富で論理的思考を好みます。
部下の成長を重視し、責任感が強い性格です。
話し方は落ち着いて論理的で、「〜だと考えます」「〜が重要です」を使います。
妻と高校生の息子、大学生の娘がいます。
効率性と品質、人材育成について語ることが多いです。
名前を呼ばれたら責任感を持って応答し、仕事や教育の話題には豊富な経験を活かして参加します。
この性格を一貫して保ち、会話してください。"""
        },
        
        "花子": {
            "name": "花子",
            "age": 64,
            "gender": "女性",
            "occupation": "元小学校教師（退職）",
            "personality": "知的で優しい、経験豊富",
            "speaking_style": "丁寧で品のある話し方、敬語を多用",
            "interests": ["読書", "習字", "孫との時間", "伝統文化", "歴史"],
            "family": "夫と同居、息子夫婦と孫2人が近所",
            "values": "教育の大切さ、伝統文化の継承",
            "response_triggers": ["教育", "文化", "歴史", "孫", "伝統"],
            "reaction_probability": 0.8,
            "prompt_template": """あなたは「花子」という64歳の女性です。
元小学校教師で、知的で優しく経験豊富な性格です。
教育に対する情熱があり、常に学ぶ姿勢を大切にします。
話し方は丁寧で品があり、「〜でございます」「〜と存じます」を使います。
夫と同居し、息子夫婦と孫2人が近所にいます。
読書や習字、孫との時間を大切にしています。
名前を呼ばれたら品格を持って応答し、教育や文化の話題には深い知識で参加します。
この性格を一貫して保ち、会話してください。"""
        },
        
        "翔太": {
            "name": "翔太",
            "age": 18,
            "gender": "男性",
            "occupation": "大学1年生",
            "personality": "好奇心旺盛で元気、少し生意気",
            "speaking_style": "カジュアルで若者らしい、略語や流行語を使う",
            "interests": ["ゲーム", "アニメ", "バイト", "友達", "新しい体験"],
            "family": "両親と姉と同居",
            "values": "自由と友情、新しい体験",
            "response_triggers": ["ゲーム", "アニメ", "学校", "バイト", "友達"],
            "reaction_probability": 0.9,
            "prompt_template": """あなたは「翔太」という18歳の男性大学生です。
大学1年生で、好奇心旺盛で元気、少し生意気な性格です。
新しいことに興味を持ち、流行に敏感です。
話し方はカジュアルで若者らしく、「〜っす」「〜じゃない？」「マジで」を使います。
両親と姉と同居しています。
ゲームやアニメ、バイト、友達との遊びが好きです。
名前を呼ばれたら元気よく反応し、ゲームやアニメの話題には熱心に参加します。
この性格を一貫して保ち、会話してください。"""
        }
    }

class ChatHistoryManager:
    """会話履歴管理クラス"""
    
    def __init__(self, filename="chat_history.json"):
        self.filename = filename
        self.history = []
        self.max_chars = 4000
        
    def load_history(self):
        """履歴をファイルから読み込み"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('messages', [])
                    return True
        except Exception as e:
            print(f"履歴読み込みエラー: {e}")
        return False
    
    def save_history(self):
        """履歴をファイルに保存"""
        try:
            data = {
                'messages': self.history,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"履歴保存エラー: {e}")
        return False
    
    def add_message(self, sender, message, sender_type="user"):
        """メッセージを履歴に追加"""
        timestamp = datetime.now().isoformat()
        self.history.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message,
            'sender_type': sender_type
        })
        
        # 文字数チェックと要約
        if self._calculate_total_chars() > self.max_chars:
            self._summarize_history()
    
    def clear_history(self):
        """履歴をクリア"""
        self.history = []
        self.save_history()
    
    def get_history_text(self):
        """履歴をテキスト形式で取得"""
        text_parts = []
        for msg in self.history:
            text_parts.append(f"{msg['sender']}: {msg['message']}")
        return "\n".join(text_parts)
    
    def get_recent_keywords(self, limit=10):
        """最近のメッセージからキーワードを抽出"""
        recent_messages = self.history[-limit:] if len(self.history) >= limit else self.history
        all_text = ' '.join([msg['message'] for msg in recent_messages])
        return self._extract_keywords(all_text)
    
    def _extract_keywords(self, text, top_n=5):
        """簡易キーワード抽出（日本語対応）"""
        # ひらがな、カタカナ、漢字、英数字を含む単語を抽出
        words = re.findall(r'[ぁ-ゖ|ァ-ヶー|一-龯|a-zA-Z0-9]+', text)
        # 短すぎる単語やよくある単語を除外
        filtered_words = [w for w in words if len(w) >= 2 and w not in ['です', 'ます', 'ある', 'する', 'いる', 'なる', 'てる', 'だから', 'そう', 'でも', 'けど']]
        counter = Counter(filtered_words)
        return [w for w, _ in counter.most_common(top_n)]
    
    def _calculate_total_chars(self):
        """履歴の総文字数を計算"""
        total = 0
        for msg in self.history:
            total += len(msg['message'])
        return total
    
    def _summarize_history(self):
        """履歴を要約して文字数を削減"""
        if len(self.history) <= 10:
            return
        
        # 最新10件は保持、それ以前を要約
        recent_messages = self.history[-10:]
        old_messages = self.history[:-10]
        
        # 簡単な要約
        summary_text = "【過去の会話要約】\n"
        for msg in old_messages[-5:]:
            summary_text += f"{msg['sender']}: {msg['message'][:50]}...\n"
        
        # 要約を履歴の最初に配置
        summary_message = {
            'timestamp': datetime.now().isoformat(),
            'sender': 'システム',
            'message': summary_text,
            'sender_type': 'system'
        }
        
        self.history = [summary_message] + recent_messages

class HumanLikeBehaviorManager:
    """人間らしい挙動管理クラス"""
    
    def __init__(self, personas):
        self.personas = personas
        self.conversation_topics = [
            "最近の天気", "好きな食べ物", "趣味の話", "仕事の話", "家族のこと",
            "最近のニュース", "休日の過ごし方", "好きな映画", "音楽の話", "旅行の話",
            "健康について", "お金の話", "将来の夢", "昔の思い出", "季節の話"
        ]
        
    def detect_mention(self, message, personas):
        """名前呼びかけを検出"""
        mentioned_personas = []
        for name in personas.keys():
            if name in message or f"{name}さん" in message or f"{name}くん" in message or f"{name}ちゃん" in message:
                mentioned_personas.append(name)
        return mentioned_personas
    
    def should_react_to_keyword(self, message, persona_name):
        """キーワードに反応すべきかチェック"""
        persona = self.personas[persona_name]
        triggers = persona.get('response_triggers', [])
        
        for trigger in triggers:
            if trigger in message:
                base_probability = persona.get('reaction_probability', 0.5)
                # キーワードが含まれている場合、反応確率を上げる
                return random.random() < (base_probability + 0.3)
        
        return random.random() < persona.get('reaction_probability', 0.3)
    
    def generate_topic_deepening_prompt(self, keywords, persona_name):
        """話題を深掘りするプロンプトを生成"""
        if not keywords:
            return None
        
        keyword = random.choice(keywords)
        persona = self.personas[persona_name]
        
        deepening_prompt = f"""
会話の中で「{keyword}」という話題が出ました。
{persona['name']}として、この話題についてもう少し詳しく聞いてみたり、
自分の経験を話したりして、会話を深めてください。
{persona['name']}らしい視点で自然に話題を発展させてください。
"""
        return deepening_prompt
    
    def generate_random_topic_change(self, persona_name):
        """ランダムな話題変更を生成"""
        topic = random.choice(self.conversation_topics)
        persona = self.personas[persona_name]
        
        topic_prompt = f"""
{persona['name']}として、自然に「{topic}」について話題を振ってください。
唐突にならないよう、今までの会話の流れを意識して、
{persona['name']}らしい話し方で話題を変えてください。
"""
        return topic_prompt
    
    def should_change_topic(self):
        """話題を変更すべきかチェック"""
        return random.random() < 0.15  # 15%の確率で話題変更

class ThemeManager:
    """テーマ管理クラス - ダークモード対応"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "chat_bg": "#ffffff",
                "chat_fg": "#000000",
                "progress_bg": "#f0f0f0",
                "progress_fg": "#000000",
                "button_bg": "#e1e1e1",
                "button_fg": "#000000",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "user_color": "#0066cc",
                "ai_color": "#009900",
                "system_color": "#cc0000",
                "frame_bg": "#f5f5f5"
            },
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "chat_bg": "#1e1e1e",
                "chat_fg": "#ffffff",
                "progress_bg": "#000000",
                "progress_fg": "#00ff00",
                "button_bg": "#404040",
                "button_fg": "#ffffff",
                "entry_bg": "#404040",
                "entry_fg": "#ffffff",
                "user_color": "#4da6ff",
                "ai_color": "#66ff66",
                "system_color": "#ff6666",
                "frame_bg": "#333333"
            }
        }
    
    def switch_theme(self):
        """テーマを切り替え"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        return self.current_theme
    
    def get_colors(self):
        """現在のテーマの色を取得"""
        return self.themes[self.current_theme]

class GeminiHumanLikeChat:
    def __init__(self, root):
        self.root = root
        self.root.title("ジェミニCLI 人間らしい多人格チャットアプリ")
        self.root.geometry("1400x950")
        
        # 基本設定
        self.personas = PersonaDefinitions.PERSONAS
        self.history_manager = ChatHistoryManager()
        self.behavior_manager = HumanLikeBehaviorManager(self.personas)
        self.theme_manager = ThemeManager()
        self.current_persona = "みゆき"
        
        # キューとフラグ
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.is_processing = False
        self.auto_chat_enabled = False
        self.auto_chat_timer = None
        self.mention_reaction_enabled = True
        self.keyword_reaction_enabled = True
        
        # GUI要素の作成
        self.create_widgets()
        self.apply_theme()
        
        # 履歴読み込み
        self.load_chat_history()
        
        # 定期的な出力チェック
        self.check_queues()
        
        # 自動会話開始
        self.start_auto_chat()
        
    def create_widgets(self):
        # メインフレーム
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上部コントロールフレーム
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第1行コントロール
        control_row1 = tk.Frame(self.control_frame)
        control_row1.pack(fill=tk.X, pady=(0, 5))
        
        # ペルソナ選択
        tk.Label(control_row1, text="話し相手:", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT)
        self.persona_var = tk.StringVar(value=self.current_persona)
        self.persona_combo = ttk.Combobox(
            control_row1, 
            textvariable=self.persona_var,
            values=list(self.personas.keys()),
            state="readonly",
            width=10
        )
        self.persona_combo.pack(side=tk.LEFT, padx=(5, 20))
        self.persona_combo.bind('<<ComboboxSelected>>', self.on_persona_changed)
        
        # 自動会話トグル
        self.auto_chat_var = tk.BooleanVar(value=True)
        self.auto_chat_check = tk.Checkbutton(
            control_row1,
            text="AI同士の自動会話",
            variable=self.auto_chat_var,
            command=self.toggle_auto_chat,
            font=('Helvetica', 10)
        )
        self.auto_chat_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # テーマ切り替えボタン
        self.theme_button = tk.Button(
            control_row1,
            text="🌙 ダークモード",
            command=self.toggle_theme,
            font=('Helvetica', 10)
        )
        self.theme_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # 履歴クリアボタン
        self.clear_button = tk.Button(
            control_row1,
            text="履歴クリア",
            command=self.clear_chat_history,
            font=('Helvetica', 10)
        )
        self.clear_button.pack(side=tk.RIGHT)
        
        # 第2行コントロール（人間らしい挙動設定）
        control_row2 = tk.Frame(self.control_frame)
        control_row2.pack(fill=tk.X)
        
        # 名前呼びかけ反応
        self.mention_reaction_var = tk.BooleanVar(value=True)
        self.mention_check = tk.Checkbutton(
            control_row2,
            text="名前呼びかけ反応",
            variable=self.mention_reaction_var,
            command=self.toggle_mention_reaction,
            font=('Helvetica', 10)
        )
        self.mention_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # キーワード反応
        self.keyword_reaction_var = tk.BooleanVar(value=True)
        self.keyword_check = tk.Checkbutton(
            control_row2,
            text="キーワード反応",
            variable=self.keyword_reaction_var,
            command=self.toggle_keyword_reaction,
            font=('Helvetica', 10)
        )
        self.keyword_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # 現在のキーワード表示
        tk.Label(control_row2, text="注目キーワード:", font=('Helvetica', 9)).pack(side=tk.LEFT, padx=(20, 5))
        self.keyword_label = tk.Label(control_row2, text="", font=('Helvetica', 9), fg="blue")
        self.keyword_label.pack(side=tk.LEFT)
        
        # チャット履歴表示エリア
        self.chat_frame = tk.LabelFrame(self.main_frame, text="チャット履歴", font=('Helvetica', 10, 'bold'))
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=22,
            font=('Helvetica', 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 進捗・ログ表示エリア
        self.progress_frame = tk.LabelFrame(self.main_frame, text="進捗・ログ情報", font=('Helvetica', 10, 'bold'))
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_display = scrolledtext.ScrolledText(
            self.progress_frame,
            wrap=tk.WORD,
            width=80,
            height=6,
            font=('Consolas', 9)
        )
        self.progress_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 入力フレーム
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # メッセージ入力欄
        self.message_entry = tk.Entry(
            self.input_frame, 
            font=('Helvetica', 12)
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        # 送信ボタン
        self.send_button = tk.Button(
            self.input_frame, 
            text="送信", 
            command=self.send_message,
            font=('Helvetica', 12)
        )
        self.send_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # キャンセルボタン
        self.cancel_button = tk.Button(
            self.input_frame,
            text="キャンセル",
            command=self.cancel_processing,
            font=('Helvetica', 12),
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.RIGHT)
        
        # ステータスフレーム
        self.status_frame = tk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="待機中", 
            font=('Helvetica', 10),
            anchor="w"
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.time_label = tk.Label(
            self.status_frame,
            text="",
            font=('Helvetica', 10)
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # 初期メッセージ
        self.add_message("システム", "ジェミニCLI 人間らしい多人格チャットアプリへようこそ！", "system")
        self.add_progress_log("INFO", "アプリケーション起動完了")
        self.display_current_persona_info()
        self.update_keyword_display()
    
    def apply_theme(self):
        """現在のテーマを適用"""
        colors = self.theme_manager.get_colors()
        
        # メインウィンドウ
        self.root.configure(bg=colors["bg"])
        
        # フレーム類
        for frame in [self.main_frame, self.control_frame, self.input_frame, self.status_frame]:
            frame.configure(bg=colors["bg"])
        
        self.chat_frame.configure(bg=colors["frame_bg"])
        self.progress_frame.configure(bg=colors["frame_bg"])
        
        # チャット表示エリア
        self.chat_display.configure(
            bg=colors["chat_bg"],
            fg=colors["chat_fg"],
            insertbackground=colors["chat_fg"]
        )
        
        # 進捗表示エリア
        self.progress_display.configure(
            bg=colors["progress_bg"],
            fg=colors["progress_fg"],
            insertbackground=colors["progress_fg"]
        )
        
        # 入力欄
        self.message_entry.configure(
            bg=colors["entry_bg"],
            fg=colors["entry_fg"],
            insertbackground=colors["entry_fg"]
        )
        
        # ボタン類
        for widget in [self.send_button, self.cancel_button, self.clear_button, self.theme_button]:
            widget.configure(
                bg=colors["button_bg"],
                fg=colors["button_fg"],
                activebackground=colors["frame_bg"]
            )
        
        # ラベル類とチェックボックス
        for child in self.control_frame.winfo_children():
            for grandchild in child.winfo_children():
                if isinstance(grandchild, tk.Label):
                    grandchild.configure(bg=colors["bg"], fg=colors["fg"])
                elif isinstance(grandchild, tk.Checkbutton):
                    grandchild.configure(
                        bg=colors["bg"],
                        fg=colors["fg"],
                        activebackground=colors["frame_bg"],
                        selectcolor=colors["button_bg"]
                    )
        
        self.status_label.configure(bg=colors["bg"], fg=colors["fg"])
        self.time_label.configure(bg=colors["bg"], fg=colors["fg"])
        self.keyword_label.configure(bg=colors["bg"])
        
        # チャット表示の色設定更新
        self.chat_display.tag_config("user", foreground=colors["user_color"], font=('Helvetica', 10, 'bold'))
        self.chat_display.tag_config("ai", foreground=colors["ai_color"], font=('Helvetica', 10, 'bold'))
        self.chat_display.tag_config("system", foreground=colors["system_color"], font=('Helvetica', 10, 'bold'))
        
        # 進捗ログの色設定更新
        self.progress_display.tag_config("error", foreground="#ff6666")
        self.progress_display.tag_config("warn", foreground="#ffff66")
        self.progress_display.tag_config("info", foreground=colors["progress_fg"])
    
    def toggle_theme(self):
        """テーマを切り替え"""
        new_theme = self.theme_manager.switch_theme()
        self.apply_theme()
        
        if new_theme == "dark":
            self.theme_button.configure(text="☀️ ライトモード")
            self.add_progress_log("INFO", "ダークモードに切り替えました")
        else:
            self.theme_button.configure(text="🌙 ダークモード")
            self.add_progress_log("INFO", "ライトモードに切り替えました")
    
    def toggle_mention_reaction(self):
        """名前呼びかけ反応のON/OFF切り替え"""
        self.mention_reaction_enabled = self.mention_reaction_var.get()
        status = "有効" if self.mention_reaction_enabled else "無効"
        self.add_progress_log("INFO", f"名前呼びかけ反応を{status}にしました")
    
    def toggle_keyword_reaction(self):
        """キーワード反応のON/OFF切り替え"""
        self.keyword_reaction_enabled = self.keyword_reaction_var.get()
        status = "有効" if self.keyword_reaction_enabled else "無効"
        self.add_progress_log("INFO", f"キーワード反応を{status}にしました")
    
    def update_keyword_display(self):
        """現在のキーワードを表示更新"""
        keywords = self.history_manager.get_recent_keywords()
        if keywords:
            self.keyword_label.configure(text=", ".join(keywords[:3]))
        else:
            self.keyword_label.configure(text="なし")
    
    def display_current_persona_info(self):
        """現在のペルソナ情報を表示"""
        persona = self.personas[self.current_persona]
        info = f"【{persona['name']}】{persona['age']}歳・{persona['gender']}・{persona['occupation']}\n"
        info += f"性格: {persona['personality']}\n"
        info += f"家族: {persona['family']}\n"
        info += f"興味: {', '.join(persona['interests'][:3])}など"
        self.add_message("システム", info, "system")
    
    def on_persona_changed(self, event=None):
        """ペルソナ変更時の処理"""
        self.current_persona = self.persona_var.get()
        self.add_progress_log("INFO", f"ペルソナを{self.current_persona}に変更")
        self.display_current_persona_info()
    
    def toggle_auto_chat(self):
        """自動会話のON/OFF切り替え"""
        self.auto_chat_enabled = self.auto_chat_var.get()
        if self.auto_chat_enabled:
            self.start_auto_chat()
            self.add_progress_log("INFO", "AI同士の自動会話を開始")
        else:
            self.stop_auto_chat()
            self.add_progress_log("INFO", "AI同士の自動会話を停止")
    
    def start_auto_chat(self):
        """自動会話を開始"""
        if self.auto_chat_enabled and not self.is_processing:
            # 20-40秒後にランダムでAI会話を発生
            delay = random.randint(20000, 40000)  # ミリ秒
            self.auto_chat_timer = self.root.after(delay, self.trigger_auto_chat)
    
    def stop_auto_chat(self):
        """自動会話を停止"""
        if self.auto_chat_timer:
            self.root.after_cancel(self.auto_chat_timer)
            self.auto_chat_timer = None
    
    def trigger_auto_chat(self):
        """自動会話をトリガー"""
        if not self.is_processing and self.auto_chat_enabled:
            # 人間らしい挙動を決定
            behavior_type = self.decide_auto_behavior()
            
            if behavior_type == "keyword_deepening":
                self.trigger_keyword_deepening()
            elif behavior_type == "topic_change":
                self.trigger_topic_change()
            else:
                self.trigger_normal_conversation()
        
        # 次の自動会話をスケジュール
        self.start_auto_chat()
    
    def decide_auto_behavior(self):
        """自動会話の挙動タイプを決定"""
        keywords = self.history_manager.get_recent_keywords()
        
        if keywords and random.random() < 0.4:  # 40%でキーワード深掘り
            return "keyword_deepening"
        elif random.random() < 0.2:  # 20%で話題変更
            return "topic_change"
        else:  # 40%で通常会話
            return "normal_conversation"
    
    def trigger_keyword_deepening(self):
        """キーワード深掘り会話をトリガー"""
        keywords = self.history_manager.get_recent_keywords()
        if not keywords:
            self.trigger_normal_conversation()
            return
        
        # キーワードに興味を持ちそうなペルソナを選択
        interested_persona = self.find_interested_persona(keywords)
        if not interested_persona:
            interested_persona = random.choice(list(self.personas.keys()))
        
        # 深掘りプロンプトを生成
        deepening_prompt = self.behavior_manager.generate_topic_deepening_prompt(keywords, interested_persona)
        
        self.add_progress_log("INFO", f"{interested_persona}がキーワード「{keywords[0]}」について深掘り開始")
        
        # AIに深掘り会話を実行させる
        old_persona = self.current_persona
        self.current_persona = interested_persona
        self.start_processing(deepening_prompt, is_auto=True, is_deepening=True)
        self.current_persona = old_persona
    
    def trigger_topic_change(self):
        """話題変更をトリガー"""
        topic_changer = random.choice(list(self.personas.keys()))
        topic_prompt = self.behavior_manager.generate_random_topic_change(topic_changer)
        
        self.add_progress_log("INFO", f"{topic_changer}が話題変更を開始")
        
        old_persona = self.current_persona
        self.current_persona = topic_changer
        self.start_processing(topic_prompt, is_auto=True, is_topic_change=True)
        self.current_persona = old_persona
    
    def trigger_normal_conversation(self):
        """通常の自動会話をトリガー"""
        available_personas = list(self.personas.keys())
        auto_persona = random.choice(available_personas)
        
        topics = [
            "最近どうですか？",
            "何か面白いことありました？",
            "今日の調子はいかがですか？",
            "最近気になることはありますか？",
            "何か新しい発見はありましたか？"
        ]
        topic = random.choice(topics)
        
        self.add_message(auto_persona, topic, "ai")
        self.add_progress_log("INFO", f"{auto_persona}が自動会話を開始")
        
        # 他のペルソナが反応するかチェック
        self.check_for_reactions(topic, auto_persona)
    
    def find_interested_persona(self, keywords):
        """キーワードに興味を持ちそうなペルソナを見つける"""
        best_persona = None
        max_matches = 0
        
        for persona_name, persona_data in self.personas.items():
            triggers = persona_data.get('response_triggers', [])
            interests = persona_data.get('interests', [])
            
            matches = 0
            for keyword in keywords:
                if any(trigger in keyword or keyword in trigger for trigger in triggers):
                    matches += 2
                if any(interest in keyword or keyword in interest for interest in interests):
                    matches += 1
            
            if matches > max_matches:
                max_matches = matches
                best_persona = persona_name
        
        return best_persona
    
    def check_for_reactions(self, message, sender):
        """メッセージに対する反応をチェック"""
        # 名前呼びかけチェック
        if self.mention_reaction_enabled:
            mentioned_personas = self.behavior_manager.detect_mention(message, self.personas)
            for mentioned in mentioned_personas:
                if mentioned != sender:
                    self.add_progress_log("INFO", f"{mentioned}が名前を呼ばれて反応予定")
                    self.schedule_reaction(mentioned, message, "mention")
        
        # キーワード反応チェック
        if self.keyword_reaction_enabled:
            for persona_name in self.personas.keys():
                if persona_name != sender:
                    if self.behavior_manager.should_react_to_keyword(message, persona_name):
                        self.add_progress_log("INFO", f"{persona_name}がキーワードに反応予定")
                        self.schedule_reaction(persona_name, message, "keyword")
                        break  # 一度に一人だけ反応
    
    def schedule_reaction(self, persona_name, message, reaction_type):
        """反応をスケジュール"""
        delay = random.randint(3000, 8000)  # 3-8秒後に反応
        self.root.after(delay, lambda: self.execute_reaction(persona_name, message, reaction_type))
    
    def execute_reaction(self, persona_name, message, reaction_type):
        """反応を実行"""
        if self.is_processing:
            return  # 処理中の場合はスキップ
        
        persona = self.personas[persona_name]
        
        if reaction_type == "mention":
            reaction_prompt = f"""
あなたの名前が呼ばれました！
メッセージ: "{message}"

{persona['name']}として、名前を呼ばれたことに対して自然に反応してください。
喜びや驚き、親しみやすさを表現して応答してください。
"""
        else:  # keyword reaction
            reaction_prompt = f"""
興味深い話題が出ました！
メッセージ: "{message}"

{persona['name']}として、この話題に興味を持って自然に反応してください。
あなたの性格や興味に基づいて応答してください。
"""
        
        old_persona = self.current_persona
        self.current_persona = persona_name
        self.start_processing(reaction_prompt, is_auto=True, is_reaction=True)
        self.current_persona = old_persona
    
    def load_chat_history(self):
        """チャット履歴を読み込み"""
        if self.history_manager.load_history():
            self.add_progress_log("INFO", "履歴を読み込みました")
            for msg in self.history_manager.history:
                self.display_message_in_chat(msg['sender'], msg['message'], msg['sender_type'])
        else:
            self.add_progress_log("WARN", "履歴ファイルが見つかりません")
    
    def clear_chat_history(self):
        """チャット履歴をクリア"""
        result = messagebox.askyesno("確認", "チャット履歴をクリアしますか？")
        if result:
            self.history_manager.clear_history()
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.add_progress_log("INFO", "チャット履歴をクリアしました")
            self.add_message("システム", "チャット履歴がクリアされました", "system")
            self.update_keyword_display()
    
    def add_progress_log(self, level, message):
        """進捗ログに情報を追加"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        self.progress_display.config(state=tk.NORMAL)
        self.progress_display.insert(tk.END, log_message)
        
        start_index = self.progress_display.index(f"end-{len(log_message)}c")
        end_index = self.progress_display.index("end-1c")
        
        if level == "ERROR":
            self.progress_display.tag_add("error", start_index, end_index)
        elif level == "WARN":
            self.progress_display.tag_add("warn", start_index, end_index)
        elif level == "INFO":
            self.progress_display.tag_add("info", start_index, end_index)
        
        self.progress_display.config(state=tk.DISABLED)
        self.progress_display.see(tk.END)
    
    def send_message(self, event=None):
        """メッセージを送信"""
        if self.is_processing:
            self.add_progress_log("WARN", "既に処理中です")
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
        
        # 入力欄をクリア
        self.message_entry.delete(0, tk.END)
        
        # チャット履歴に追加
        self.add_message("あなた", message, "user")
        
        # 反応チェック
        self.check_for_reactions(message, "あなた")
        
        # 処理開始
        self.start_processing(message)
    
    def start_processing(self, message, is_auto=False, is_deepening=False, is_topic_change=False, is_reaction=False):
        """ジェミニCLI処理を開始"""
        self.is_processing = True
        self.send_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.status_label.config(text="処理中...", fg="orange")
        
        self.start_time = time.time()
        
        # 別スレッドでジェミニCLIを実行
        self.processing_thread = threading.Thread(
            target=self.call_gemini_cli_with_persona, 
            args=(message, is_auto, is_deepening, is_topic_change, is_reaction),
            daemon=True
        )
        self.processing_thread.start()
        
        # タイマーを開始
        self.update_processing_time()
    
    def call_gemini_cli_with_persona(self, message, is_auto=False, is_deepening=False, is_topic_change=False, is_reaction=False):
        """ペルソナ設定でジェミニCLIを実行"""
        try:
            persona = self.personas[self.current_persona]
            
            if is_deepening or is_topic_change or is_reaction:
                # 特殊な挙動の場合は、メッセージをそのまま使用
                prompt = persona['prompt_template'] + "\n\n"
                prompt += "これまでの会話履歴:\n" + self.history_manager.get_history_text() + "\n\n"
                prompt += message
            else:
                # 通常の会話の場合
                prompt = persona['prompt_template'] + "\n\n"
                prompt += "これまでの会話履歴:\n" + self.history_manager.get_history_text() + "\n\n"
                prompt += f"新しいメッセージ: {message}\n\n"
                prompt += "上記の性格設定に従って、自然に応答してください。"
            
            self.add_progress_log("INFO", f"{persona['name']}として応答中...")
            
            # ジェミニCLIプロセスを開始
            process = subprocess.Popen(
                ['gemini', '--prompt', prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.current_process = process
            self.add_progress_log("INFO", f"プロセスID: {process.pid}")
            
            # 標準出力を監視
            output_lines = []
            while True:
                if process.poll() is not None:
                    break
                
                line = process.stdout.readline()
                if line:
                    line = line.rstrip()
                    output_lines.append(line)
                    self.add_progress_log("OUTPUT", f"受信: {line[:80]}...")
                
                time.sleep(0.1)
            
            # 残りの出力を取得
            remaining_output, error_output = process.communicate()
            if remaining_output:
                for line in remaining_output.split('\n'):
                    if line.strip():
                        output_lines.append(line.strip())
            
            # 結果を処理
            if process.returncode == 0:
                if output_lines:
                    full_response = '\n'.join(output_lines)
                    self.output_queue.put(("SUCCESS", full_response, persona['name']))
                    self.add_progress_log("INFO", f"正常終了 (戻り値: {process.returncode})")
                else:
                    self.output_queue.put(("EMPTY", "", persona['name']))
                    self.add_progress_log("WARN", "応答が空でした")
            else:
                error_msg = error_output if error_output else f"エラー終了 (戻り値: {process.returncode})"
                self.error_queue.put(error_msg)
                self.add_progress_log("ERROR", f"エラー終了: {error_msg}")
                
        except FileNotFoundError:
            self.error_queue.put("ジェミニCLIが見つかりません")
            self.add_progress_log("ERROR", "ジェミニCLIが見つかりません")
        except Exception as e:
            self.error_queue.put(f"予期しないエラー: {str(e)}")
            self.add_progress_log("ERROR", f"予期しないエラー: {str(e)}")
        finally:
            self.current_process = None
    
    def cancel_processing(self):
        """処理をキャンセル"""
        if hasattr(self, 'current_process') and self.current_process:
            try:
                self.current_process.terminate()
                self.add_progress_log("WARN", "処理をキャンセルしました")
            except:
                pass
        
        self.finish_processing()
        self.add_message("システム", "処理がキャンセルされました", "system")
    
    def finish_processing(self):
        """処理終了時の後処理"""
        self.is_processing = False
        self.send_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        colors = self.theme_manager.get_colors()
        self.status_label.config(text="待機中", fg=colors["fg"])
        self.time_label.config(text="")
    
    def update_processing_time(self):
        """処理時間を更新"""
        if self.is_processing:
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"処理時間: {elapsed:.1f}秒")
            self.root.after(100, self.update_processing_time)
    
    def check_queues(self):
        """キューをチェックしてGUIを更新"""
        # 成功結果をチェック
        try:
            while True:
                result_type, response, persona_name = self.output_queue.get_nowait()
                if result_type == "SUCCESS":
                    self.add_message(persona_name, response, "ai")
                    # 新しいメッセージに対して反応をチェック
                    self.check_for_reactions(response, persona_name)
                elif result_type == "EMPTY":
                    self.add_message("システム", f"{persona_name}からの応答がありませんでした", "system")
                self.finish_processing()
        except queue.Empty:
            pass
        
        # エラー結果をチェック
        try:
            while True:
                error_msg = self.error_queue.get_nowait()
                self.add_message("システム", f"エラー: {error_msg}", "system")
                self.finish_processing()
        except queue.Empty:
            pass
        
        # 100ms後に再度チェック
        self.root.after(100, self.check_queues)
    
    def add_message(self, sender, message, sender_type):
        """チャット履歴にメッセージを追加"""
        # 履歴管理に保存
        self.history_manager.add_message(sender, message, sender_type)
        self.history_manager.save_history()
        
        # 画面に表示
        self.display_message_in_chat(sender, message, sender_type)
        
        # キーワード表示を更新
        self.update_keyword_display()
    
    def display_message_in_chat(self, sender, message, sender_type):
        """チャット画面にメッセージを表示"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        # 送信者に応じて色を変更
        if sender_type == "user":
            self.chat_display.insert(tk.END, f"[{timestamp}] 【{sender}】 ", "user")
        elif sender_type == "ai":
            self.chat_display.insert(tk.END, f"[{timestamp}] 【{sender}】 ", "ai")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] 【{sender}】 ", "system")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

def main():
    root = tk.Tk()
    app = GeminiHumanLikeChat(root)
    root.mainloop()

if __name__ == "__main__":
    main()
