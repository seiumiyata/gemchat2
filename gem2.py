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

class GeminiModelManager:
    """Geminiモデル管理クラス"""
    
    def __init__(self):
        self.models = {
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "description": "最高性能（制限：25回/日）",
                "daily_limit": 25,
                "minute_limit": 5,
                "priority": 1,
                "fallback_chain": ["gemini-2.5-flash", "gemini-1.5-flash"]
            },
            "gemini-2.5-flash": {
                "name": "Gemini 2.5 Flash",
                "description": "高速・高制限（1500回/日）",
                "daily_limit": 1500,
                "minute_limit": 15,
                "priority": 2,
                "fallback_chain": ["gemini-1.5-flash"]
            },
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "description": "安定・高制限（1500回/日）",
                "daily_limit": 1500,
                "minute_limit": 15,
                "priority": 3,
                "fallback_chain": ["gemini-1.5-pro"]
            },
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "description": "バランス型（50回/日）",
                "daily_limit": 50,
                "minute_limit": 5,
                "priority": 4,
                "fallback_chain": ["gemini-2.5-flash", "gemini-1.5-flash"]
            }
        }
        
        self.current_model = "gemini-2.5-pro"
        self.error_history = {}
        self.last_error_time = {}
        
    def get_model_info(self, model_id):
        """モデル情報を取得"""
        return self.models.get(model_id, {})
    
    def get_available_models(self):
        """利用可能なモデル一覧を取得"""
        return list(self.models.keys())
    
    def should_fallback(self, error_message):
        """フォールバックが必要かチェック"""
        fallback_indicators = [
            "429",
            "Too Many Requests",
            "Quota exceeded",
            "rateLimitExceeded",
            "RESOURCE_EXHAUSTED",
            "404",
            "not found",
            "NOT_FOUND"
        ]
        return any(indicator in str(error_message) for indicator in fallback_indicators)
    
    def get_next_model(self, current_model):
        """次のフォールバックモデルを取得"""
        model_info = self.models.get(current_model, {})
        fallback_chain = model_info.get("fallback_chain", [])
        
        for next_model in fallback_chain:
            if self._is_model_available(next_model):
                return next_model
        
        return None
    
    def _is_model_available(self, model_id):
        """モデルが利用可能かチェック"""
        last_error = self.last_error_time.get(model_id, 0)
        return (time.time() - last_error) > 300
    
    def record_error(self, model_id, error_message):
        """エラーを記録"""
        self.error_history[model_id] = self.error_history.get(model_id, 0) + 1
        self.last_error_time[model_id] = time.time()
    
    def get_recommended_model(self):
        """推奨モデルを取得"""
        available_models = [
            (model_id, info) for model_id, info in self.models.items()
            if self._is_model_available(model_id)
        ]
        
        if not available_models:
            return "gemini-1.5-flash"
        
        best_model = min(available_models, 
                        key=lambda x: (x[1]["priority"], 
                                     self.error_history.get(x[0], 0)))
        return best_model[0]

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
            "reaction_probability": 0.8,
            "color": "#FF69B4",
            "status": "待機中",
            "prompt_template": """あなたは「みゆき」という25歳の女性です。
IT企業で営業職として働いており、明るく社交的な性格です。
トレンドに敏感で、SNSやカフェ巡りが好きです。
話し方は親しみやすく、「〜ですね！」「〜かも」「〜って感じ？」をよく使います。
仕事とプライベートのバランスを大切にしています。
この性格を一貫して保ち、会話してください。"""
        },
        
        "さやか": {
            "name": "さやか",
            "age": 30,
            "gender": "女性",
            "occupation": "マーケティング担当",
            "personality": "クリエイティブで積極的、企画力がある",
            "speaking_style": "元気で親しみやすい、「〜よね」「すごい！」をよく使う",
            "interests": ["デザイン", "広告", "ブランディング", "アート", "猫"],
            "family": "独身、ペットの猫（みかん）と同居",
            "values": "創造性と革新性を重視",
            "response_triggers": ["デザイン", "広告", "マーケティング", "創造", "猫"],
            "reaction_probability": 0.9,
            "color": "#FF6347",
            "status": "待機中",
            "prompt_template": """あなたは「さやか」という30歳の女性です。
マーケティング担当として働いており、クリエイティブで積極的な性格です。
企画力があり、常に新しいアイデアを考えています。
話し方は元気で親しみやすく、「〜よね」「すごい！」「面白そう！」をよく使います。
独身でペットの猫（みかん）と同居しています。
デザインやアートに興味があり、創造性を大切にしています。
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
            "reaction_probability": 0.7,
            "color": "#4169E1",
            "status": "待機中",
            "prompt_template": """あなたは「健太郎」という32歳の男性医師です。
内科医として病院で働いており、真面目で責任感が強い性格です。
患者思いで、常に相手の健康や安全を気遣います。
話し方は丁寧で落ち着いており、「〜と思います」「〜でしょう」を使います。
既婚で妻と2歳の娘がいます。医学的な知識も交えて会話します。
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
            "color": "#32CD32",
            "status": "待機中",
            "prompt_template": """あなたは「美香」という43歳の女性です。
主婦兼パート店員として働いており、温かく家族思いの性格です。
世話好きで、常に相手を気遣います。
話し方は優しく丁寧で、「〜ですね」「〜でしょうね」を使います。
夫と中学生の息子、小学生の娘がいます。
料理や園芸、子育ての話題が得意です。
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
            "color": "#8B4513",
            "status": "待機中",
            "prompt_template": """あなたは「正一」という48歳の男性です。
製造業で部長職として働いており、経験豊富で論理的思考を好みます。
部下の成長を重視し、責任感が強い性格です。
話し方は落ち着いて論理的で、「〜だと考えます」「〜が重要です」を使います。
妻と高校生の息子、大学生の娘がいます。
効率性と品質、人材育成について語ることが多いです。
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
            "color": "#9370DB",
            "status": "待機中",
            "prompt_template": """あなたは「花子」という64歳の女性です。
元小学校教師で、知的で優しく経験豊富な性格です。
教育に対する情熱があり、常に学ぶ姿勢を大切にします。
話し方は丁寧で品があり、「〜でございます」「〜と存じます」を使います。
夫と同居し、息子夫婦と孫2人が近所にいます。
読書や習字、孫との時間を大切にしています。
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
            "color": "#FF4500",
            "status": "待機中",
            "prompt_template": """あなたは「翔太」という18歳の男性大学生です。
大学1年生で、好奇心旺盛で元気、少し生意気な性格です。
新しいことに興味を持ち、流行に敏感です。
話し方はカジュアルで若者らしく、「〜っす」「〜じゃない？」「マジで」を使います。
両親と姉と同居しています。
ゲームやアニメ、バイト、友達との遊びが好きです。
この性格を一貫して保ち、会話してください。"""
        },
        
        "りな": {
            "name": "りな",
            "age": 16,
            "gender": "女性",
            "occupation": "高校生",
            "personality": "明るく活発、努力家で仲間思い",
            "speaking_style": "元気で親しみやすい、「〜だよ」「〜だと思う」をよく使う",
            "interests": ["バスケットボール", "勉強", "音楽", "友達", "お菓子作り"],
            "family": "両親と中学生の弟と同居",
            "values": "努力と友情、チームワークを大切にする",
            "response_triggers": ["スポーツ", "バスケ", "勉強", "学校", "友達"],
            "reaction_probability": 0.8,
            "color": "#228B22",
            "status": "待機中",
            "prompt_template": """あなたは「りな」という16歳の女性高校生です。
高校2年生で、バスケットボール部に所属しており、明るく活発な性格です。
努力家で仲間思いで、いつも前向きです。
話し方は元気で親しみやすく、「〜だよ」「〜だと思う」「頑張ろう！」をよく使います。
両親と中学生の弟と同居しています。
バスケットボールと勉強の両立を頑張っており、友達との時間も大切にしています。
お菓子作りも趣味の一つです。
この性格を一貫して保ち、会話してください。"""
        }
    }

class ChatFormatter:
    """チャット表示フォーマット管理クラス"""
    
    def __init__(self):
        self.max_line_length = 40
        self.break_characters = ['。', '、', '！', '？', 'です', 'ます', 'でした', 'ました']
        
    def format_message(self, message):
        """メッセージを読みやすい形にフォーマット"""
        if len(message) <= self.max_line_length:
            return message
        
        formatted_lines = []
        current_line = ""
        
        sentences = re.split(r'([。！？])', message)
        
        for i, part in enumerate(sentences):
            if not part:
                continue
                
            if part in ['。', '！', '？']:
                if i > 0:
                    current_line += part
                    formatted_lines.append(current_line.strip())
                    current_line = ""
                continue
            
            if len(current_line + part) > self.max_line_length:
                if current_line:
                    formatted_lines.append(current_line.strip())
                    current_line = part
                else:
                    formatted_lines.extend(self._force_break_long_text(part))
                    current_line = ""
            else:
                current_line += part
        
        if current_line.strip():
            formatted_lines.append(current_line.strip())
        
        return '\n'.join(formatted_lines)
    
    def _force_break_long_text(self, text):
        """長すぎるテキストを強制的に分割"""
        lines = []
        while len(text) > self.max_line_length:
            break_pos = self.max_line_length
            for char in self.break_characters:
                pos = text.rfind(char, 0, self.max_line_length)
                if pos > self.max_line_length * 0.7:
                    break_pos = pos + len(char)
                    break
            
            lines.append(text[:break_pos])
            text = text[break_pos:]
        
        if text:
            lines.append(text)
        
        return lines

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
        
        recent_messages = self.history[-10:]
        old_messages = self.history[:-10]
        
        summary_text = "【過去の会話要約】\n"
        for msg in old_messages[-5:]:
            summary_text += f"{msg['sender']}: {msg['message'][:50]}...\n"
        
        summary_message = {
            'timestamp': datetime.now().isoformat(),
            'sender': 'システム',
            'message': summary_text,
            'sender_type': 'system'
        }
        
        self.history = [summary_message] + recent_messages

class BatchConversationProcessor:
    """バッチ会話処理クラス"""
    
    def __init__(self, personas):
        self.personas = personas
        
    def create_batch_prompt(self, user_message, history_text):
        """バッチ処理用プロンプトを作成"""
        prompt = f"""以下の8人のキャラクターが会話に参加します。
ユーザーの発言に対して、各キャラクターの性格に基づいて自然に応答してください。

キャラクター設定:
"""
        
        for name, persona in self.personas.items():
            prompt += f"""
【{persona['name']}】{persona['age']}歳・{persona['gender']}・{persona['occupation']}
性格: {persona['personality']}
話し方: {persona['speaking_style']}
"""
        
        prompt += f"""
これまでの会話履歴:
{history_text}

新しいユーザーの発言: "{user_message}"

指示:
1. 各キャラクターの性格を維持してください
2. 全員が必ず反応する必要はありません（興味を持った人だけ）
3. 自然な会話の流れを作ってください
4. 読みやすさのため、長い文章は適度に改行を入れてください
5. 以下の形式で出力してください:

【キャラクター名】
発言内容

【キャラクター名】
発言内容

（発言しないキャラクターは出力しないでください）
"""
        
        return prompt
    
    def parse_batch_response(self, response):
        """バッチレスポンスを解析"""
        conversations = []
        lines = response.split('\n')
        
        current_speaker = None
        current_message = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('【') and line.endswith('】'):
                if current_speaker and current_message:
                    conversations.append({
                        'speaker': current_speaker,
                        'message': '\n'.join(current_message).strip()
                    })
                
                current_speaker = line[1:-1]
                current_message = []
            elif line and current_speaker:
                current_message.append(line)
        
        if current_speaker and current_message:
            conversations.append({
                'speaker': current_speaker,
                'message': '\n'.join(current_message).strip()
            })
        
        return conversations

class ThemeManager:
    """テーマ管理クラス"""
    
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
                "frame_bg": "#f5f5f5",
                "listbox_bg": "#ffffff",
                "listbox_fg": "#000000"
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
                "frame_bg": "#333333",
                "listbox_bg": "#2b2b2b",
                "listbox_fg": "#ffffff"
            }
        }
    
    def switch_theme(self):
        """テーマを切り替え"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        return self.current_theme
    
    def get_colors(self):
        """現在のテーマの色を取得"""
        return self.themes[self.current_theme]

class GeminiAutoModelChat:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini CLI 自動モデル切り替えチャット（女性ペルソナ対応版）")
        self.root.geometry("1700x1050")
        
        # 基本設定
        self.personas = PersonaDefinitions.PERSONAS
        self.history_manager = ChatHistoryManager()
        self.batch_processor = BatchConversationProcessor(self.personas)
        self.theme_manager = ThemeManager()
        self.chat_formatter = ChatFormatter()
        self.model_manager = GeminiModelManager()
        
        # キューとフラグ
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.display_queue = queue.Queue()
        self.is_processing = False
        self.auto_chat_enabled = True
        self.auto_chat_timer = None
        
        # GUI要素の作成
        self.create_widgets()
        self.apply_theme()
        
        # 履歴読み込み
        self.load_chat_history()
        
        # 定期的な出力チェック
        self.check_queues()
        self.check_display_queue()
        
        # 自動会話開始
        self.start_auto_chat()
        
    def create_widgets(self):
        # メインフレーム
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左パネル（参加者一覧とモデル情報）
        self.left_panel = tk.Frame(self.main_frame, width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_panel.pack_propagate(False)
        
        # モデル選択フレーム
        self.model_frame = tk.LabelFrame(self.left_panel, text="AIモデル設定", font=('Helvetica', 12, 'bold'))
        self.model_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 現在のモデル表示
        self.current_model_label = tk.Label(
            self.model_frame, 
            text="現在のモデル:", 
            font=('Helvetica', 10, 'bold')
        )
        self.current_model_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        self.model_display = tk.Label(
            self.model_frame,
            text="Gemini 2.5 Pro",
            font=('Helvetica', 10),
            fg="blue"
        )
        self.model_display.pack(anchor=tk.W, padx=5)
        
        # モデル選択コンボボックス
        tk.Label(self.model_frame, text="手動切り替え:", font=('Helvetica', 10)).pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        self.model_var = tk.StringVar(value=self.model_manager.current_model)
        self.model_combo = ttk.Combobox(
            self.model_frame,
            textvariable=self.model_var,
            values=self.model_manager.get_available_models(),
            state="readonly",
            width=25
        )
        self.model_combo.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_changed)
        
        # モデル情報表示
        self.model_info_text = tk.Text(
            self.model_frame,
            height=4,
            width=30,
            font=('Helvetica', 9),
            wrap=tk.WORD
        )
        self.model_info_text.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.update_model_info_display()
        
        # 自動切り替え設定
        self.auto_fallback_var = tk.BooleanVar(value=True)
        self.auto_fallback_check = tk.Checkbutton(
            self.model_frame,
            text="自動フォールバック",
            variable=self.auto_fallback_var,
            font=('Helvetica', 10)
        )
        self.auto_fallback_check.pack(anchor=tk.W, padx=5, pady=(0, 5))
        
        # 参加者一覧フレーム
        self.participants_frame = tk.LabelFrame(self.left_panel, text="参加者一覧（女性6名・男性2名）", font=('Helvetica', 12, 'bold'))
        self.participants_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 参加者リスト
        self.participants_listbox = tk.Listbox(
            self.participants_frame,
            font=('Helvetica', 10),
            height=16,
            selectmode=tk.BROWSE
        )
        self.participants_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 参加者情報を表示
        self.update_participants_list()
        
        # 右パネル（チャットとコントロール）
        self.right_panel = tk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 上部コントロールフレーム
        self.control_frame = tk.Frame(self.right_panel)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 自動会話トグル
        self.auto_chat_var = tk.BooleanVar(value=True)
        self.auto_chat_check = tk.Checkbutton(
            self.control_frame,
            text="自動会話モード",
            variable=self.auto_chat_var,
            command=self.toggle_auto_chat,
            font=('Helvetica', 11, 'bold')
        )
        self.auto_chat_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # テーマ切り替えボタン
        self.theme_button = tk.Button(
            self.control_frame,
            text="🌙 ダークモード",
            command=self.toggle_theme,
            font=('Helvetica', 10)
        )
        self.theme_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # 履歴クリアボタン
        self.clear_button = tk.Button(
            self.control_frame,
            text="履歴クリア",
            command=self.clear_chat_history,
            font=('Helvetica', 10)
        )
        self.clear_button.pack(side=tk.RIGHT)
        
        # チャット履歴表示エリア
        self.chat_frame = tk.LabelFrame(self.right_panel, text="チャット履歴", font=('Helvetica', 11, 'bold'))
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame, 
            wrap=tk.WORD, 
            width=90, 
            height=22,
            font=('Helvetica', 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 進捗・ログ表示エリア
        self.progress_frame = tk.LabelFrame(self.right_panel, text="システムログ", font=('Helvetica', 10, 'bold'))
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_display = scrolledtext.ScrolledText(
            self.progress_frame,
            wrap=tk.WORD,
            width=90,
            height=5,
            font=('Consolas', 9)
        )
        self.progress_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 入力フレーム
        self.input_frame = tk.Frame(self.right_panel)
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
        self.status_frame = tk.Frame(self.right_panel)
        self.status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="待機中 - 自動会話モードが有効です（女性6名・男性2名）", 
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
        self.add_message("システム", "Gemini CLI 多人格チャット（女性ペルソナ対応版）へようこそ！", "system")
        self.add_message("システム", "新メンバー：りな（16歳・女性・高校生）が参加しました", "system")
        self.add_message("システム", "女性6名・男性2名でバランス良く会話が楽しめます", "system")
        self.add_progress_log("INFO", "アプリケーション起動完了")
        self.add_progress_log("INFO", f"現在のモデル: {self.model_manager.current_model}")
        self.add_progress_log("INFO", f"参加者数: {len(self.personas)}名（女性6名・男性2名）")
    
    def update_participants_list(self):
        """参加者リストを更新"""
        self.participants_listbox.delete(0, tk.END)
        
        for name, persona in self.personas.items():
            status_icon = "💭" if persona["status"] == "思考中" else "💬" if persona["status"] == "話し中" else "😊"
            display_text = f"{status_icon} {persona['name']} ({persona['age']}歳・{persona['gender']})"
            self.participants_listbox.insert(tk.END, display_text)
            
            index = self.participants_listbox.size() - 1
            self.participants_listbox.itemconfig(index, {'fg': persona['color']})
    
    def update_persona_status(self, persona_name, status):
        """ペルソナの状態を更新"""
        if persona_name in self.personas:
            self.personas[persona_name]["status"] = status
            self.update_participants_list()
    
    def on_model_changed(self, event=None):
        """モデル変更時の処理"""
        new_model = self.model_var.get()
        self.model_manager.current_model = new_model
        self.update_model_display()
        self.update_model_info_display()
        self.add_progress_log("INFO", f"モデルを手動で変更: {new_model}")
        self.add_message("システム", f"AIモデルを {self.model_manager.get_model_info(new_model)['name']} に変更しました", "system")
    
    def update_model_display(self):
        """現在のモデル表示を更新"""
        model_info = self.model_manager.get_model_info(self.model_manager.current_model)
        self.model_display.config(text=model_info.get('name', 'Unknown Model'))
    
    def update_model_info_display(self):
        """モデル情報表示を更新"""
        model_info = self.model_manager.get_model_info(self.model_manager.current_model)
        info_text = f"説明: {model_info.get('description', 'N/A')}\n"
        info_text += f"制限: {model_info.get('daily_limit', 'N/A')}回/日\n"
        info_text += f"優先度: {model_info.get('priority', 'N/A')}"
        
        self.model_info_text.delete(1.0, tk.END)
        self.model_info_text.insert(1.0, info_text)
        self.model_info_text.config(state=tk.DISABLED)
    
    def handle_model_fallback(self, error_message):
        """モデルフォールバックを処理"""
        if not self.auto_fallback_var.get():
            return False
        
        if not self.model_manager.should_fallback(error_message):
            return False
        
        current_model = self.model_manager.current_model
        next_model = self.model_manager.get_next_model(current_model)
        
        if next_model:
            self.model_manager.record_error(current_model, error_message)
            
            self.model_manager.current_model = next_model
            self.model_var.set(next_model)
            self.update_model_display()
            self.update_model_info_display()
            
            model_info = self.model_manager.get_model_info(next_model)
            self.add_progress_log("WARN", f"モデル自動切り替え: {current_model} → {next_model}")
            self.add_message("システム", 
                           f"API制限のため、AIモデルを {model_info['name']} に自動切り替えしました", 
                           "system")
            return True
        else:
            self.add_progress_log("ERROR", "利用可能なフォールバックモデルがありません")
            self.add_message("システム", 
                           "すべてのモデルで制限に達しています。しばらく時間をおいてから再試行してください", 
                           "system")
            return False
    
    def apply_theme(self):
        """現在のテーマを適用"""
        colors = self.theme_manager.get_colors()
        
        # メインウィンドウ
        self.root.configure(bg=colors["bg"])
        
        # フレーム類
        for frame in [self.main_frame, self.left_panel, self.right_panel, self.control_frame, 
                     self.input_frame, self.status_frame]:
            frame.configure(bg=colors["bg"])
        
        for labelframe in [self.model_frame, self.participants_frame, self.chat_frame, self.progress_frame]:
            labelframe.configure(bg=colors["frame_bg"])
        
        # UI要素
        self.participants_listbox.configure(bg=colors["listbox_bg"], fg=colors["listbox_fg"])
        self.chat_display.configure(bg=colors["chat_bg"], fg=colors["chat_fg"], insertbackground=colors["chat_fg"])
        self.progress_display.configure(bg=colors["progress_bg"], fg=colors["progress_fg"], insertbackground=colors["progress_fg"])
        self.message_entry.configure(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["entry_fg"])
        self.model_info_text.configure(bg=colors["entry_bg"], fg=colors["entry_fg"])
        
        # ボタン類
        for widget in [self.send_button, self.cancel_button, self.clear_button, self.theme_button]:
            widget.configure(bg=colors["button_bg"], fg=colors["button_fg"], activebackground=colors["frame_bg"])
        
        # チェックボックス
        for widget in [self.auto_chat_check, self.auto_fallback_check]:
            widget.configure(bg=colors["bg"], fg=colors["fg"], activebackground=colors["frame_bg"], selectcolor=colors["button_bg"])
        
        # ラベル類
        for widget in [self.status_label, self.time_label, self.current_model_label, self.model_display]:
            widget.configure(bg=colors["bg"], fg=colors["fg"])
        
        # チャット表示の色設定更新
        self.chat_display.tag_config("user", foreground="#0066cc", font=('Helvetica', 10, 'bold'))
        self.chat_display.tag_config("ai", foreground="#009900", font=('Helvetica', 10, 'bold'))
        self.chat_display.tag_config("system", foreground="#cc0000", font=('Helvetica', 10, 'bold'))
        
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
    
    def toggle_auto_chat(self):
        """自動会話のON/OFF切り替え"""
        self.auto_chat_enabled = self.auto_chat_var.get()
        if self.auto_chat_enabled:
            self.start_auto_chat()
            self.status_label.config(text="待機中 - 自動会話モードが有効です（女性6名・男性2名）")
            self.add_progress_log("INFO", "自動会話モードを有効にしました")
        else:
            self.stop_auto_chat()
            self.status_label.config(text="待機中 - 自動会話モードが無効です（女性6名・男性2名）")
            self.add_progress_log("INFO", "自動会話モードを無効にしました")
    
    def start_auto_chat(self):
        """自動会話を開始"""
        if self.auto_chat_enabled and not self.is_processing:
            delay = random.randint(20000, 40000)  # 20-40秒間隔
            self.auto_chat_timer = self.root.after(delay, self.trigger_auto_conversation)
    
    def stop_auto_chat(self):
        """自動会話を停止"""
        if self.auto_chat_timer:
            self.root.after_cancel(self.auto_chat_timer)
            self.auto_chat_timer = None
    
    def trigger_auto_conversation(self):
        """自動会話をトリガー"""
        if not self.is_processing and self.auto_chat_enabled:
            topics = [
                "最近の天気について話したいと思います",
                "みなさんの趣味について聞かせてください",
                "今日はいい日ですね、何か楽しいことはありましたか？",
                "最近気になるニュースはありますか？",
                "おすすめの本や映画があれば教えてください",
                "今度の休日はどう過ごす予定ですか？",
                "最近始めた新しいことはありますか？",
                "好きな音楽や歌手はいますか？",
                "美味しい食べ物の話をしませんか？",
                "将来の夢や目標について話しましょう",
                "学校や仕事で楽しいことはありますか？",
                "おすすめのお店やカフェはありますか？"
            ]
            
            topic = random.choice(topics)
            starter = random.choice(list(self.personas.keys()))
            
            self.add_message(starter, topic, "ai")
            self.add_progress_log("INFO", f"{starter}が自動会話を開始しました")
            
            self.start_batch_processing(topic)
        
        self.start_auto_chat()
    
    def start_batch_processing(self, user_message):
        """バッチ処理を開始"""
        self.is_processing = True
        self.send_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.status_label.config(text="AIが会話を生成中...")
        
        for name in self.personas.keys():
            self.update_persona_status(name, "思考中")
        
        self.start_time = time.time()
        
        self.processing_thread = threading.Thread(
            target=self.execute_batch_processing_with_fallback, 
            args=(user_message,),
            daemon=True
        )
        self.processing_thread.start()
        
        self.update_processing_time()
    
    def execute_batch_processing_with_fallback(self, user_message):
        """フォールバック機能付きバッチ処理を実行"""
        max_attempts = 4
        attempt = 0
        
        while attempt < max_attempts:
            try:
                current_model = self.model_manager.current_model
                batch_prompt = self.batch_processor.create_batch_prompt(
                    user_message, 
                    self.history_manager.get_history_text()
                )
                
                self.add_progress_log("INFO", f"バッチ会話生成を開始 (モデル: {current_model})")
                
                # Gemini CLIプロセスを開始（モデル指定付き）
                process = subprocess.Popen(
                    ['gemini', '--model', current_model, '--prompt', batch_prompt],
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
                        conversations = self.batch_processor.parse_batch_response(full_response)
                        self.output_queue.put(("BATCH_SUCCESS", conversations))
                        self.add_progress_log("INFO", f"バッチ処理完了 ({len(conversations)}件の応答)")
                        return
                    else:
                        self.output_queue.put(("BATCH_EMPTY", []))
                        self.add_progress_log("WARN", "バッチ処理の応答が空でした")
                        return
                else:
                    error_msg = error_output if error_output else f"エラー終了 (戻り値: {process.returncode})"
                    
                    # フォールバック処理
                    if self.handle_model_fallback(error_msg):
                        attempt += 1
                        self.add_progress_log("INFO", f"フォールバック試行 {attempt}/{max_attempts}")
                        continue
                    else:
                        self.error_queue.put(error_msg)
                        self.add_progress_log("ERROR", f"バッチ処理エラー: {error_msg}")
                        return
                        
            except FileNotFoundError:
                self.error_queue.put("ジェミニCLIが見つかりません")
                self.add_progress_log("ERROR", "ジェミニCLIが見つかりません")
                return
            except Exception as e:
                self.error_queue.put(f"予期しないエラー: {str(e)}")
                self.add_progress_log("ERROR", f"予期しないエラー: {str(e)}")
                return
            finally:
                self.current_process = None
        
        # 最大試行回数に達した場合
        self.error_queue.put("すべてのフォールバックモデルで処理に失敗しました")
        self.add_progress_log("ERROR", "すべてのフォールバックモデルで処理に失敗")
    
    def schedule_conversation_display(self, conversations):
        """会話の時間差表示をスケジュール"""
        base_delay = 2000
        for i, conv in enumerate(conversations):
            delay = base_delay + (i * random.randint(1500, 3000))
            self.root.after(delay, lambda c=conv: self.display_queue.put(c))
    
    def check_display_queue(self):
        """時間差表示キューをチェック"""
        try:
            while True:
                conv = self.display_queue.get_nowait()
                speaker = conv['speaker']
                message = conv['message']
                
                if speaker in self.personas:
                    self.update_persona_status(speaker, "話し中")
                    
                    formatted_message = self.chat_formatter.format_message(message)
                    self.display_message_in_chat(speaker, formatted_message, "ai")
                    self.add_progress_log("INFO", f"{speaker}が発言しました")
                    
                    self.root.after(2000, lambda s=speaker: self.update_persona_status(s, "待機中"))
        except queue.Empty:
            pass
        
        self.root.after(1000, self.check_display_queue)
    
    def send_message(self, event=None):
        """メッセージを送信"""
        if self.is_processing:
            self.add_progress_log("WARN", "既に処理中です")
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
        
        self.message_entry.delete(0, tk.END)
        
        formatted_message = self.chat_formatter.format_message(message)
        self.add_message("あなた", formatted_message, "user")
        
        self.start_batch_processing(message)
    
    def load_chat_history(self):
        """チャット履歴を読み込み"""
        if self.history_manager.load_history():
            self.add_progress_log("INFO", "履歴を読み込みました")
            for msg in self.history_manager.history:
                formatted_message = self.chat_formatter.format_message(msg['message'])
                self.display_message_in_chat(msg['sender'], formatted_message, msg['sender_type'])
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
        
        for name in self.personas.keys():
            self.update_persona_status(name, "待機中")
        
        colors = self.theme_manager.get_colors()
        status_text = "待機中 - 自動会話モードが有効です（女性6名・男性2名）" if self.auto_chat_enabled else "待機中 - 自動会話モードが無効です（女性6名・男性2名）"
        self.status_label.config(text=status_text, fg=colors["fg"])
        self.time_label.config(text="")
    
    def update_processing_time(self):
        """処理時間を更新"""
        if self.is_processing:
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"処理時間: {elapsed:.1f}秒")
            self.root.after(100, self.update_processing_time)
    
    def check_queues(self):
        """キューをチェックしてGUIを更新"""
        try:
            while True:
                result_type, data = self.output_queue.get_nowait()
                if result_type == "BATCH_SUCCESS":
                    self.schedule_conversation_display(data)
                elif result_type == "BATCH_EMPTY":
                    self.add_message("システム", "応答が生成されませんでした", "system")
                self.finish_processing()
        except queue.Empty:
            pass
        
        try:
            while True:
                error_msg = self.error_queue.get_nowait()
                self.add_message("システム", f"エラー: {error_msg}", "system")
                self.finish_processing()
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queues)
    
    def add_message(self, sender, message, sender_type):
        """チャット履歴にメッセージを追加"""
        original_message = message.replace('\n', ' ')
        self.history_manager.add_message(sender, original_message, sender_type)
        self.history_manager.save_history()
        
        self.display_message_in_chat(sender, message, sender_type)
    
    def display_message_in_chat(self, sender, message, sender_type):
        """チャット画面にメッセージを表示"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        if sender_type == "user":
            self.chat_display.insert(tk.END, f"[{timestamp}] 【{sender}】\n", "user")
        elif sender_type == "ai":
            self.chat_display.insert(tk.END, f"[{timestamp}] 【{sender}】\n", "ai")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] 【{sender}】\n", "system")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

def main():
    root = tk.Tk()
    app = GeminiAutoModelChat(root)
    root.mainloop()

if __name__ == "__main__":
    main()
