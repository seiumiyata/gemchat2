#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini CLI 多人格チャットアプリケーション - 完全版
MBTI・ビッグ5理論統合・動的AIプロンプトシステム・全機能搭載
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import subprocess
import json
import threading
import time
import random
import re
import logging
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
import queue
from collections import Counter, defaultdict

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('chat_app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class PersonaDefinitions:
    """ペルソナ定義管理クラス - MBTI・ビッグ5・裏設定統合版"""
    
    PERSONAS = {
        # === 既存ペルソナ（MBTI・ビッグ5・裏設定統合） ===
        "みゆき": {
            "age": 25, "gender": "女性", "occupation": "IT企業営業",
            "personality": "明るく社交的、トレンド敏感",
            "family": "両親と同居、恋人あり", "hometown": "東京都渋谷区",
            "backstory": "大学時代はサークル活動に熱中。SNSインフルエンサーとしても活動中",
            "traits": ["テクノロジー好き", "SNS活用", "新しいもの好き", "コミュニケーション上手"],
            "keywords": ["IT", "テクノロジー", "SNS", "トレンド", "営業", "デジタル", "スマホ", "アプリ", "インフルエンサー", "マーケティング"],
            "speaking_style": "フレンドリーで親しみやすく、絵文字や流行語を使う",
            "color": "#FF69B4",
            "mbti": "ENFP",  # 運動家タイプ
            "big5": {"openness": 85, "conscientiousness": 60, "extraversion": 90, "agreeableness": 75, "neuroticism": 40},
            "hidden_traits": ["見栄っ張り"],  # SNSでの「盛り」が激しい
            "interest_topics": ["テクノロジー", "SNS", "マーケティング", "トレンド", "ファッション"],
            "conversation_patterns": {
                "high_interest": "詳細で熱心、多くの具体例と経験談を交える",
                "medium_interest": "適度に参加、基本的な意見を述べる", 
                "low_interest": "短めの反応、話題転換を試みる"
            }
        },
        "さやか": {
            "age": 30, "gender": "女性", "occupation": "マーケティング担当",
            "personality": "クリエイティブで積極的",
            "family": "独身、猫2匹と暮らす", "hometown": "神奈川県横浜市",
            "backstory": "美大卒業後、広告代理店を経て現職。アート展巡りが趣味",
            "traits": ["アイデア豊富", "戦略的思考", "チャレンジ精神", "分析好き"],
            "keywords": ["マーケティング", "ブランディング", "戦略", "クリエイティブ", "広告", "分析", "企画", "アート", "デザイン", "統計"],
            "speaking_style": "論理的で説得力があり、データを重視した発言",
            "color": "#32CD32",
            "mbti": "ENTJ",  # 指揮官タイプ
            "big5": {"openness": 80, "conscientiousness": 85, "extraversion": 70, "agreeableness": 55, "neuroticism": 30},
            "hidden_traits": [],
            "interest_topics": ["マーケティング", "ビジネス戦略", "データ分析", "アート", "デザイン"],
            "conversation_patterns": {
                "high_interest": "データと事例を豊富に用いて論理的に深掘り",
                "medium_interest": "戦略的視点から適切なアドバイス",
                "low_interest": "簡潔な意見、専門的観点のみ"
            }
        },
        "健太郎": {
            "age": 32, "gender": "男性", "occupation": "内科医",
            "personality": "真面目で責任感が強い",
            "family": "妻と長女（3歳）", "hometown": "京都府京都市",
            "backstory": "医学部時代は合気道部。研修医時代の激務で体調を崩した経験あり",
            "traits": ["医学知識豊富", "患者思い", "勉強熱心", "倫理観強い"],
            "keywords": ["医療", "健康", "病気", "治療", "予防", "薬", "症状", "診断", "科学", "研究"],
            "speaking_style": "丁寧で専門的、医学的根拠に基づいた説明",
            "color": "#4169E1",
            "mbti": "ISTJ",  # 実務家タイプ
            "big5": {"openness": 65, "conscientiousness": 95, "extraversion": 40, "agreeableness": 80, "neuroticism": 35},
            "hidden_traits": ["短気"],  # 忙しいとイライラしやすい
            "interest_topics": ["医療", "健康", "科学", "研究", "病気予防"],
            "conversation_patterns": {
                "high_interest": "医学的根拠と詳細な説明、専門用語を交えて",
                "medium_interest": "基本的な医学知識で回答",
                "low_interest": "短く専門的見解のみ、時々イライラが見える"
            }
        },
        "美香": {
            "age": 43, "gender": "女性", "occupation": "主婦兼パート店員",
            "personality": "温かく家族思い",
            "family": "夫、長男（高1）、長女（中2）", "hometown": "埼玉県川口市",
            "backstory": "元銀行員。結婚後専業主婦、子育て落ち着き後パート開始",
            "traits": ["家事上手", "節約術", "子育て経験豊富", "地域密着"],
            "keywords": ["家族", "子育て", "料理", "家事", "節約", "買い物", "地域", "学校", "PTA", "主婦"],
            "speaking_style": "親しみやすく母親らしい、実用的なアドバイス",
            "color": "#FF6347",
            "mbti": "ESFJ",  # 領事タイプ
            "big5": {"openness": 50, "conscientiousness": 80, "extraversion": 65, "agreeableness": 90, "neuroticism": 45},
            "hidden_traits": [],
            "interest_topics": ["子育て", "家族", "料理", "節約", "教育", "地域活動"],
            "conversation_patterns": {
                "high_interest": "豊富な経験談と具体的なアドバイス、母親目線で",
                "medium_interest": "親しみやすく共感的な反応",
                "low_interest": "優しく短めの反応、家族の話題に転換"
            }
        },
        "正一": {
            "age": 48, "gender": "男性", "occupation": "製造業部長",
            "personality": "経験豊富で論理的",
            "family": "妻、長男（大2）、次男（高3）", "hometown": "愛知県名古屋市",
            "backstory": "高卒で製造業に就職、現場から管理職へ。職人気質で品質にこだわる",
            "traits": ["リーダーシップ", "現場経験豊富", "品質重視", "効率化思考"],
            "keywords": ["製造", "品質", "効率", "管理", "改善", "技術", "生産", "コスト", "現場", "ものづくり"],
            "speaking_style": "落ち着いて論理的、実務的で具体的",
            "color": "#8B4513",
            "mbti": "ESTJ",  # 幹部タイプ
            "big5": {"openness": 45, "conscientiousness": 90, "extraversion": 60, "agreeableness": 70, "neuroticism": 25},
            "hidden_traits": ["粘着気質"],  # 仕事の話になると止まらない
            "interest_topics": ["製造業", "品質管理", "効率化", "技術革新", "管理手法"],
            "conversation_patterns": {
                "high_interest": "現場経験と改善事例を詳細に語る、止まらなくなる",
                "medium_interest": "実務的で具体的なアドバイス",
                "low_interest": "短く実用的な観点のみ"
            }
        },
        "花子": {
            "age": 64, "gender": "女性", "occupation": "元小学校教師",
            "personality": "知的で優しい",
            "family": "夫、長女家族と同居", "hometown": "長野県松本市",
            "backstory": "40年間小学校教師。退職後は読書サークルや地域ボランティア活動",
            "traits": ["教育熱心", "読書好き", "文化的教養", "子供好き"],
            "keywords": ["教育", "学習", "読書", "文化", "歴史", "子供", "成長", "知識", "文学", "古典"],
            "speaking_style": "教育者らしく丁寧で、知識豊富な発言",
            "color": "#9370DB",
            "mbti": "INFJ",  # 提唱者タイプ
            "big5": {"openness": 85, "conscientiousness": 80, "extraversion": 45, "agreeableness": 85, "neuroticism": 30},
            "hidden_traits": [],
            "interest_topics": ["教育", "文学", "歴史", "文化", "子供の成長", "読書"],
            "conversation_patterns": {
                "high_interest": "教育的観点から深く考察、歴史的背景も交える",
                "medium_interest": "知的で温かい助言",
                "low_interest": "短く優しい反応、教育的な視点を軽く"
            }
        },
        "翔太": {
            "age": 18, "gender": "男性", "occupation": "大学1年生",
            "personality": "好奇心旺盛で元気",
            "family": "両親、姉（大3）", "hometown": "福岡県福岡市",
            "backstory": "高校時代はサッカー部キャプテン。大学では軽音楽部とバイトを掛け持ち",
            "traits": ["エネルギッシュ", "新しいこと好き", "スポーツ好き", "友達思い"],
            "keywords": ["大学", "勉強", "スポーツ", "友達", "ゲーム", "音楽", "バイト", "将来", "サッカー", "青春"],
            "speaking_style": "元気で親しみやすく、若者らしい表現",
            "color": "#FF4500",
            "mbti": "ESFP",  # エンターテイナータイプ
            "big5": {"openness": 75, "conscientiousness": 45, "extraversion": 85, "agreeableness": 80, "neuroticism": 55},
            "hidden_traits": ["卑屈"],  # 周りと比較して落ち込みやすい
            "interest_topics": ["スポーツ", "音楽", "ゲーム", "大学生活", "友達関係"],
            "conversation_patterns": {
                "high_interest": "めちゃくちゃ熱く語る、経験談と感情豊か",
                "medium_interest": "元気よく参加、友達感覚で",
                "low_interest": "ちょっと卑屈になって短く、話題変えたがる"
            }
        },
        "りな": {
            "age": 16, "gender": "女性", "occupation": "高校生",
            "personality": "明るく活発、努力家",
            "family": "両親、弟（中1）", "hometown": "大阪府大阪市",
            "backstory": "中学時代は生徒会長。高校では演劇部に所属し、将来は声優志望",
            "traits": ["勉強熱心", "部活動好き", "友達大切", "夢追い"],
            "keywords": ["高校", "勉強", "部活", "友達", "進路", "夢", "恋愛", "ファッション", "演劇", "声優"],
            "speaking_style": "明るく元気で、高校生らしい表現",
            "color": "#FF1493",
            "mbti": "ENFJ",  # 主人公タイプ
            "big5": {"openness": 80, "conscientiousness": 75, "extraversion": 80, "agreeableness": 85, "neuroticism": 40},
            "hidden_traits": [],
            "interest_topics": ["演劇", "声優", "勉強", "友達", "将来の夢", "恋愛"],
            "conversation_patterns": {
                "high_interest": "キラキラした感じで夢を語る、具体的な目標も",
                "medium_interest": "明るく前向きに参加",
                "low_interest": "短めだけど明るく、友達の話にシフト"
            }
        },
        
        # === 新規追加ペルソナ（10名） ===
        "玲奈": {
            "age": 28, "gender": "女性", "occupation": "UXデザイナー",
            "personality": "共感重視で軽快、国際感覚豊富",
            "family": "独身、一人暮らし", "hometown": "東京都目黒区",
            "backstory": "芸大卒業後イタリア留学。帰国後IT企業でUI/UX担当、海外クライアント多数",
            "traits": ["デザイン感覚", "ユーザー視点", "国際感覚", "完璧主義"],
            "keywords": ["デザイン", "UI", "UX", "ユーザ体験", "海外", "アート", "イタリア", "美学", "創造性"],
            "speaking_style": "英語混じりで洒落た表現、デザイン用語多用",
            "color": "#00CED1",
            "mbti": "INFP",  # 仲介者タイプ
            "big5": {"openness": 95, "conscientiousness": 70, "extraversion": 55, "agreeableness": 85, "neuroticism": 45},
            "hidden_traits": ["八方美人"],  # クライアントに合わせすぎる
            "interest_topics": ["デザイン", "アート", "UX", "海外文化", "美学", "創造性"],
            "conversation_patterns": {
                "high_interest": "美学と創造性について情熱的に、海外事例も豊富",
                "medium_interest": "デザイナー視点で的確な意見",
                "low_interest": "八方美人的に当たり障りなく、すぐ話題転換"
            }
        },
        "明弘": {
            "age": 35, "gender": "男性", "occupation": "地方公務員",
            "personality": "丁寧で堅実、地域愛強い",
            "family": "妻、長女（3歳）", "hometown": "石川県金沢市",
            "backstory": "中学まで野球部、県庁職員として地方創生に取り組む。故郷を愛する",
            "traits": ["責任感", "地域愛", "調整能力", "慎重派"],
            "keywords": ["地方創生", "行政", "防災", "地域", "公務", "政策", "金沢", "伝統", "観光"],
            "speaking_style": "丁寧語多用、方言少々、真面目な口調",
            "color": "#228B22",
            "mbti": "ISFJ",  # 擁護者タイプ
            "big5": {"openness": 40, "conscientiousness": 90, "extraversion": 35, "agreeableness": 80, "neuroticism": 50},
            "hidden_traits": ["卑屈"],  # 都市部に劣等感を持つ
            "interest_topics": ["地方創生", "行政", "地域活性化", "伝統文化", "防災"],
            "conversation_patterns": {
                "high_interest": "地方の現状と課題を詳しく、でも少し都市部への劣等感も",
                "medium_interest": "真面目で慎重な意見",
                "low_interest": "卑屈になって短く、地方の良さをちょっとアピール"
            }
        },
        "ジュリア": {
            "age": 42, "gender": "女性", "occupation": "イタリア料理シェフ",
            "personality": "陽気で食材愛が強い、情熱的",
            "family": "夫（日本人）、犬1匹", "hometown": "ミラノ→東京",
            "backstory": "ミラノ生まれの日伊ハーフ、東京で料理店経営。食材への情熱は人一倍",
            "traits": ["料理の腕", "陽気さ", "食へのこだわり", "家族愛"],
            "keywords": ["レシピ", "ワイン", "地中海", "イタリア", "食材", "料理", "パスタ", "オリーブオイル"],
            "speaking_style": "明るく情熱的、イタリア語混じり",
            "color": "#DC143C",
            "mbti": "ESFP",  # エンターテイナータイプ
            "big5": {"openness": 80, "conscientiousness": 60, "extraversion": 90, "agreeableness": 75, "neuroticism": 35},
            "hidden_traits": [],
            "interest_topics": ["料理", "イタリア文化", "食材", "ワイン", "レストラン経営"],
            "conversation_patterns": {
                "high_interest": "情熱的に料理論を展開、イタリア語も混じる",
                "medium_interest": "陽気に食文化について",
                "low_interest": "短めだけど陽気、食べ物の話に持っていく"
            }
        },
        "達也": {
            "age": 27, "gender": "男性", "occupation": "eSportsコーチ",
            "personality": "熱血でゲーム愛強い、負けず嫌い",
            "family": "未婚、シェアハウス暮らし", "hometown": "東京都秋葉原",
            "backstory": "元プロゲーマー、現在は若手育成に専念。ゲームへの情熱は冷めない",
            "traits": ["ゲーム技術", "戦略思考", "指導力", "負けず嫌い"],
            "keywords": ["FPS", "戦略", "反射神経", "チーム", "練習", "大会", "eスポーツ", "ゲーミング"],
            "speaking_style": "熱血、ゲーム用語多用、仲間意識強い",
            "color": "#FF8C00",
            "mbti": "ENTJ",  # 指揮官タイプ
            "big5": {"openness": 70, "conscientiousness": 80, "extraversion": 75, "agreeableness": 50, "neuroticism": 60},
            "hidden_traits": ["短気", "粘着気質"],  # 負けるとキレやすく、勝負にこだわりすぎ
            "interest_topics": ["ゲーム", "eスポーツ", "戦略", "チーム戦術", "技術向上"],
            "conversation_patterns": {
                "high_interest": "めちゃくちゃ熱く戦略論、止まらなくなって専門用語連発",
                "medium_interest": "チーム論や戦略的視点で",
                "low_interest": "短気になって短く、ゲームの話に持っていきたがる"
            }
        },
        "夏海": {
            "age": 21, "gender": "女性", "occupation": "大学生（心理学専攻）",
            "personality": "前向きでSNS慣れ、トレンド敏感",
            "family": "実家暮らし（両親、祖母）", "hometown": "千葉県船橋市",
            "backstory": "SNSインフルエンサーとして活動、心理学で人間関係を研究中",
            "traits": ["SNS感覚", "心理分析", "トレンド感度", "共感力"],
            "keywords": ["心理", "Z世代", "SNS", "トレンド", "恋愛", "友達", "インスタ", "TikTok"],
            "speaking_style": "スラング混じり、前向きで親しみやすい",
            "color": "#FF69B4",
            "mbti": "ENFP",  # 運動家タイプ
            "big5": {"openness": 85, "conscientiousness": 55, "extraversion": 80, "agreeableness": 75, "neuroticism": 45},
            "hidden_traits": ["見栄っ張り"],  # SNSでの「盛り」が激しい
            "interest_topics": ["心理学", "SNS", "恋愛", "友達関係", "トレンド", "Z世代文化"],
            "conversation_patterns": {
                "high_interest": "心理学的分析を交えて詳しく、SNS事例も豊富",
                "medium_interest": "前向きで共感的に",
                "low_interest": "見栄を張って短く、インスタ映えしそうな話に"
            }
        },
        "真琴": {
            "age": 54, "gender": "男性", "occupation": "中学校校長",
            "personality": "落ち着きがあり教訓多め、教育哲学持つ",
            "family": "妻、息子（独立済み）", "hometown": "広島県広島市",
            "backstory": "元数学教師、生徒指導に長年従事、現在は学校運営に専念",
            "traits": ["教育哲学", "数学的思考", "人間観察", "忍耐力"],
            "keywords": ["教育改革", "数学", "部活", "生徒指導", "学校運営", "人格形成", "道徳"],
            "speaking_style": "落ち着きのある口調、教訓や格言を好む",
            "color": "#4682B4",
            "mbti": "INTJ",  # 建築家タイプ
            "big5": {"openness": 70, "conscientiousness": 90, "extraversion": 40, "agreeableness": 70, "neuroticism": 25},
            "hidden_traits": ["粘着気質"],  # 教育論になると長くなる
            "interest_topics": ["教育", "数学", "生徒指導", "学校経営", "人格形成"],
            "conversation_patterns": {
                "high_interest": "教育論を深く語る、数学的論理と経験談で止まらない",
                "medium_interest": "教育者らしい落ち着いた意見",
                "low_interest": "短く格言的に、教育に絡めようとする"
            }
        },
        "エリック": {
            "age": 47, "gender": "男性", "occupation": "外資系コンサルタント",
            "personality": "論理的で英語混じり、効率重視",
            "family": "妻（日本人）、双子（7歳）", "hometown": "ニューヨーク→東京",
            "backstory": "NY出身、東京駐在10年、日本企業のDX支援に従事",
            "traits": ["論理思考", "国際経験", "データ分析", "効率重視"],
            "keywords": ["KPI", "戦略", "DX", "コンサル", "データ", "効率", "ROI", "グローバル"],
            "speaking_style": "論理的で簡潔、英語交じりのビジネス用語",
            "color": "#708090",
            "mbti": "ENTJ",  # 指揮官タイプ
            "big5": {"openness": 75, "conscientiousness": 85, "extraversion": 70, "agreeableness": 50, "neuroticism": 30},
            "hidden_traits": ["見栄っ張り"],  # 経歴や実績を誇張しがち
            "interest_topics": ["ビジネス戦略", "DX", "データ分析", "グローバル経済", "効率化"],
            "conversation_patterns": {
                "high_interest": "データと事例で論理的に、英語も交えて詳細分析",
                "medium_interest": "効率的で戦略的な観点",
                "low_interest": "見栄を張って実績アピール、英語多めで短く"
            }
        },
        "美鈴": {
            "age": 33, "gender": "女性", "occupation": "看護師",
            "personality": "優しく思いやりがある、現場慣れ",
            "family": "夫（医師）、長男（1歳）", "hometown": "北海道札幌市",
            "backstory": "ICU勤務5年、出産後は外来勤務、医療現場の人間関係に詳しい",
            "traits": ["医療知識", "思いやり", "体力", "協調性"],
            "keywords": ["医療", "育児", "健康", "看護", "患者", "病院", "チーム医療", "ケア"],
            "speaking_style": "優しく丁寧、医療用語を分かりやすく説明",
            "color": "#20B2AA",
            "mbti": "ISFJ",  # 擁護者タイプ
            "big5": {"openness": 60, "conscientiousness": 85, "extraversion": 50, "agreeableness": 90, "neuroticism": 40},
            "hidden_traits": ["八方美人"],  # 患者や医師の間で板挟みになりがち
            "interest_topics": ["医療", "看護", "育児", "健康管理", "患者ケア"],
            "conversation_patterns": {
                "high_interest": "看護師としての経験と母親目線で詳しく、優しく",
                "medium_interest": "思いやりのある実用的アドバイス",
                "low_interest": "八方美人的に当たり障りなく、医療健康の話に"
            }
        },
        "龍之介": {
            "age": 40, "gender": "男性", "occupation": "物流ドライバー",
            "personality": "ざっくばらんで音楽好き、自由気質",
            "family": "独身", "hometown": "大阪府大阪市",
            "backstory": "元ミュージシャン志望、今は長距離ドライバーとして全国を回る",
            "traits": ["運転技術", "地理知識", "音楽愛", "自由気質"],
            "keywords": ["物流", "道路事情", "音楽", "トラック", "運転", "全国", "バンド", "ライブ"],
            "speaking_style": "関西弁、ざっくばらん、音楽の話になると熱くなる",
            "color": "#CD853F",
            "mbti": "ISFP",  # 冒険家タイプ
            "big5": {"openness": 75, "conscientiousness": 45, "extraversion": 60, "agreeableness": 65, "neuroticism": 55},
            "hidden_traits": ["卑屈"],  # 夢を諦めた後悔がある
            "interest_topics": ["音楽", "バンド", "ライブ", "物流業界", "ドライブ"],
            "conversation_patterns": {
                "high_interest": "音楽愛を熱く語る、でも夢を諦めた後悔も混じる",
                "medium_interest": "関西弁でざっくばらんに",
                "low_interest": "卑屈になって短く、音楽の話に逃げる"
            }
        },
        "アヤ": {
            "age": 13, "gender": "女性", "occupation": "中学2年生",
            "personality": "元気で可愛い語尾、想像力豊か",
            "family": "両親、弟（小5）", "hometown": "神奈川県横浜市",
            "backstory": "漫画研究部所属、将来は漫画家志望、SNSで作品発表も。家族はみんな元気で、特にお父さんお母さんは私の漫画を応援してくれてる！この前も新しいペンタブを買ってくれた",
            "traits": ["絵の才能", "想像力", "素直さ", "好奇心"],
            "keywords": ["勉強", "推し", "SNS", "漫画", "絵", "中学校", "創作", "アニメ"],
            "speaking_style": "元気で可愛らしい、「〜だよ！」「〜なの」多用",
            "color": "#FFB6C1",
            "mbti": "ENFP",  # 運動家タイプ
            "big5": {"openness": 90, "conscientiousness": 50, "extraversion": 75, "agreeableness": 80, "neuroticism": 35},
            "hidden_traits": ["粘着気質"],  # 好きなことに異常に集中する
            "interest_topics": ["漫画", "アニメ", "絵", "創作", "推し活", "中学生活"],
            "conversation_patterns": {
                "high_interest": "めちゃくちゃ興奮して長文、創作論とか推し語りが止まらない",
                "medium_interest": "元気よく中学生らしく",
                "low_interest": "短めでも可愛く、すぐ好きな話題に持っていく"
            }
        }
    }

class DynamicPromptGenerator:
    """動的AIプロンプト生成クラス"""
    
    def __init__(self):
        self.conversation_context = []
        self.topic_keywords = defaultdict(int)
        
    def analyze_interest_level(self, persona_name, message_content):
        """ペルソナの興味レベルを分析"""
        persona = PersonaDefinitions.PERSONAS[persona_name]
        interest_topics = persona["interest_topics"]
        
        # キーワードマッチング分析
        matches = 0
        for topic in interest_topics:
            if topic.lower() in message_content.lower():
                matches += 1
                
        # 興味レベル判定
        if matches >= 2:
            return "high_interest"
        elif matches >= 1:
            return "medium_interest"
        else:
            return "low_interest"
    
    def generate_dynamic_prompt(self, persona_name, user_message, context, interest_level):
        """動的プロンプト生成 - 心理学理論統合"""
        persona = PersonaDefinitions.PERSONAS[persona_name]
        mbti = persona["mbti"]
        big5 = persona["big5"]
        conversation_pattern = persona["conversation_patterns"][interest_level]
        hidden_traits = persona.get("hidden_traits", [])
        
        # MBTI特性による会話調整
        mbti_modifiers = self._get_mbti_modifiers(mbti)
        
        # ビッグ5による詳細調整
        big5_modifiers = self._get_big5_modifiers(big5)
        
        # 興味レベル別の詳細度設定
        detail_settings = {
            "high_interest": {
                "response_length": "3-5文で詳細に",
                "examples": "具体例や経験談を2-3個含める",
                "emotion": "情熱的で詳しく語る"
            },
            "medium_interest": {
                "response_length": "2-3文で適度に",
                "examples": "1つの具体例を含める",
                "emotion": "普通の関心を示す"
            },
            "low_interest": {
                "response_length": "1-2文で簡潔に",
                "examples": "簡単な例のみ、または無し",
                "emotion": "控えめで短めに"
            }
        }
        
        detail = detail_settings[interest_level]
        
        # 裏設定による調整
        hidden_modifiers = ""
        if hidden_traits:
            hidden_modifiers = f"裏設定として{', '.join(hidden_traits)}な特徴を発言に反映させてください。"
        
        prompt = f"""
あなたは{persona_name}（{persona['age']}歳、{persona['occupation']}）として会話してください。

【基本設定】
- 性格: {persona['personality']}
- 話し方: {persona['speaking_style']}
- 生い立ち: {persona['backstory']}
- MBTI: {mbti}

【心理特性による会話調整】
{mbti_modifiers}
{big5_modifiers}

【今回の興味レベル】: {interest_level}
- 会話パターン: {conversation_pattern}
- 返答の長さ: {detail['response_length']}
- 具体例: {detail['examples']}
- 感情表現: {detail['emotion']}

【前の会話履歴】
{context}

【ユーザーメッセージ】
{user_message}

【特別指示】
{hidden_modifiers}

【重要】このペルソナの興味分野（{', '.join(persona['interest_topics'])}）に関する話題かどうかで反応の熱量を調整してください。
興味のある話題なら詳しく語り、そうでなければ適度に対応してください。

必ず{persona_name}らしい個性的で人間らしい発言をしてください。
"""
        return prompt
    
    def _get_mbti_modifiers(self, mbti):
        """MBTI特性による会話修正子を生成"""
        modifiers = []
        
        # 外向性/内向性
        if mbti[0] == 'E':
            modifiers.append("外向的：積極的に発言し、他者との交流を楽しむ")
        else:
            modifiers.append("内向的：慎重に考えてから発言し、深い内容を好む")
            
        # 感覚/直観
        if mbti[1] == 'S':
            modifiers.append("感覚型：具体的な事実やデータを重視し、現実的")
        else:
            modifiers.append("直観型：可能性や未来志向、抽象的な概念を好む")
            
        # 思考/感情
        if mbti[2] == 'T':
            modifiers.append("思考型：論理的で客観的、事実を重視した判断")
        else:
            modifiers.append("感情型：共感的で人間関係を重視、感情を大切にする")
            
        # 判断/知覚
        if mbti[3] == 'J':
            modifiers.append("判断型：計画的で組織的、決断が早い")
        else:
            modifiers.append("知覚型：柔軟で適応的、可能性を探る")
            
        return "- " + "\n- ".join(modifiers)
    
    def _get_big5_modifiers(self, big5_scores):
        """ビッグ5特性による会話修正子を生成"""
        modifiers = []
        
        # 開放性
        if big5_scores["openness"] > 70:
            modifiers.append("創造的で新しいアイデアに興味深い")
        elif big5_scores["openness"] < 40:
            modifiers.append("伝統的で現実的なアプローチを好む")
            
        # 誠実性  
        if big5_scores["conscientiousness"] > 70:
            modifiers.append("責任感が強く計画的で詳細にこだわる")
        elif big5_scores["conscientiousness"] < 40:
            modifiers.append("自由奔放で衝動的な傾向")
            
        # 外向性
        if big5_scores["extraversion"] > 70:
            modifiers.append("エネルギッシュで社交的")
        elif big5_scores["extraversion"] < 40:
            modifiers.append("内省的で静かな環境を好む")
            
        # 協調性
        if big5_scores["agreeableness"] > 70:
            modifiers.append("他者への思いやりが深く協力的")
        elif big5_scores["agreeableness"] < 40:
            modifiers.append("競争的で自己主張が強い")
            
        # 神経症的傾向
        if big5_scores["neuroticism"] > 60:
            modifiers.append("感情の起伏があり、ストレスに敏感")
        elif big5_scores["neuroticism"] < 30:
            modifiers.append("感情が安定しており冷静")
            
        return "- " + "\n- ".join(modifiers) if modifiers else ""

class GeminiModelManager:
    """Gemini モデル管理・切り替えクラス"""
    
    MODELS = [
        "gemini-2.5-flash",
        "gemini-1.5-flash", 
        "gemini-2.5-pro",
        "gemini-1.5-pro"
    ]
    
    def __init__(self):
        self.current_model = self.MODELS[0]
        self.error_counts = {model: 0 for model in self.MODELS}
        logger.info(f"GeminiModelManager初期化: 初期モデル={self.current_model}")
        
    def get_next_model(self):
        """エラー時の次のモデルを取得"""
        current_index = self.MODELS.index(self.current_model)
        next_index = (current_index + 1) % len(self.MODELS)
        old_model = self.current_model
        self.current_model = self.MODELS[next_index]
        self.error_counts[old_model] += 1
        logger.warning(f"モデル切り替え: {old_model} -> {self.current_model}")
        return self.current_model
        
    def reset_model(self):
        """モデルを初期化"""
        self.current_model = self.MODELS[0]
        logger.info(f"モデルリセット: {self.current_model}")

class ChatHistoryManager:
    """会話履歴の保存・読み込み管理クラス"""
    
    def __init__(self, filename="chat_history.json"):
        self.filename = filename
        self.max_length = 4000
        logger.info(f"ChatHistoryManager初期化: ファイル={filename}")
        
    def save_history(self, history):
        """履歴をJSONファイルに保存"""
        try:
            total_length = sum(len(str(msg)) for msg in history)
            if total_length > self.max_length:
                history = self._summarize_history(history)
                logger.info(f"履歴要約実行: {total_length} -> {sum(len(str(msg)) for msg in history)}")
            
            serializable_history = []
            for msg in history:
                if isinstance(msg.get('timestamp'), datetime):
                    msg['timestamp'] = msg['timestamp'].isoformat()
                serializable_history.append(msg)
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_history, f, ensure_ascii=False, indent=2)
            logger.debug(f"履歴保存完了: {len(history)}件")
        except Exception as e:
            logger.error(f"履歴保存エラー: {e}")
            
    def load_history(self):
        """JSONファイルから履歴を読み込み"""
        try:
            if Path(self.filename).exists():
                with open(self.filename, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    for msg in history:
                        if isinstance(msg.get('timestamp'), str):
                            try:
                                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
                            except:
                                msg['timestamp'] = datetime.now()
                    logger.info(f"履歴読み込み完了: {len(history)}件")
                    return history
        except Exception as e:
            logger.error(f"履歴読み込みエラー: {e}")
        return []
        
    def _summarize_history(self, history):
        """履歴を要約（簡易版：最新の50%を保持）"""
        return history[len(history)//2:]
        
    def clear_history(self):
        """履歴をクリア"""
        try:
            if Path(self.filename).exists():
                Path(self.filename).unlink()
            logger.info("履歴クリア完了")
        except Exception as e:
            logger.error(f"履歴クリアエラー: {e}")

class BatchConversationProcessor:
    """バッチ処理制御クラス - 動的プロンプト対応"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.processing = False
        self.prompt_generator = DynamicPromptGenerator()
        logger.info("BatchConversationProcessor初期化完了")
        
    def generate_batch_conversation(self, context, user_message, active_personas):
        """動的プロンプトによるバッチ会話生成"""
        if self.processing:
            logger.warning("既に処理中のため、バッチ会話生成をスキップ")
            return []
            
        self.processing = True
        logger.info(f"動的バッチ会話生成開始: ユーザーメッセージ='{user_message[:50]}...'")
        
        try:
            # 名前呼びかけチェック
            mentioned_personas = self._check_name_mentions(user_message, active_personas)
            
            # 各ペルソナの興味レベル分析と動的選択
            final_personas = self._dynamic_persona_selection(
                user_message, active_personas, mentioned_personas
            )
            
            # 動的プロンプトで個別応答生成
            conversations = []
            for persona_name in final_personas:
                try:
                    # 興味レベル分析
                    interest_level = self.prompt_generator.analyze_interest_level(
                        persona_name, user_message
                    )
                    
                    # 動的プロンプト生成
                    dynamic_prompt = self.prompt_generator.generate_dynamic_prompt(
                        persona_name, user_message, context, interest_level
                    )
                    
                    # AI応答生成
                    response = self._call_gemini_cli(dynamic_prompt)
                    
                    conversations.append({
                        'persona': persona_name,
                        'message': response.strip(),
                        'timestamp': datetime.now(),
                        'interest_level': interest_level
                    })
                    
                    logger.debug(f"動的応答生成: {persona_name} ({interest_level})")
                    
                    # 人間らしい間隔
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    logger.error(f"個別応答生成エラー ({persona_name}): {e}")
                    
            logger.info(f"動的バッチ会話生成完了: {len(conversations)}件の応答")
            return conversations
            
        except Exception as e:
            logger.error(f"動的バッチ会話生成エラー: {e}")
            return []
        finally:
            self.processing = False
    
    def _dynamic_persona_selection(self, user_message, all_personas, mentioned_personas):
        """動的ペルソナ選択 - 興味度ベース"""
        selected = set(mentioned_personas)  # 呼びかけられたペルソナは必ず参加
        
        # 各ペルソナの興味度を計算
        interest_scores = {}
        for persona_name in all_personas:
            if persona_name not in selected:
                interest_level = self.prompt_generator.analyze_interest_level(
                    persona_name, user_message
                )
                
                # 興味度による参加確率
                participation_probability = {
                    "high_interest": 0.8,   # 高い興味：80%で参加
                    "medium_interest": 0.4,  # 普通の興味：40%で参加  
                    "low_interest": 0.1     # 低い興味：10%で参加
                }
                
                if random.random() < participation_probability[interest_level]:
                    selected.add(persona_name)
                    interest_scores[persona_name] = interest_level
        
        # 最大5名に制限
        if len(selected) > 5:
            # 高い興味のペルソナを優先
            high_interest = [p for p, level in interest_scores.items() if level == "high_interest"]
            medium_interest = [p for p, level in interest_scores.items() if level == "medium_interest"]
            
            final_selected = set(mentioned_personas)  # 呼びかけられたペルソナは保持
            remaining_slots = 5 - len(final_selected)
            
            # 優先順位に従って追加
            for persona_list in [high_interest, medium_interest]:
                while remaining_slots > 0 and persona_list:
                    final_selected.add(persona_list.pop(0))
                    remaining_slots -= 1
                    
            selected = final_selected
        
        return list(selected)
        
    def _check_name_mentions(self, message, personas):
        """メッセージ内の名前呼びかけをチェック"""
        mentioned = []
        for name in personas:
            if name in message or f"@{name}" in message:
                mentioned.append(name)
                logger.debug(f"名前呼びかけ検出: {name}")
        return mentioned
        
    def _call_gemini_cli(self, prompt):
        """Gemini CLIを呼び出し"""
        max_retries = len(self.model_manager.MODELS)
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Gemini CLI呼び出し開始: モデル={self.model_manager.current_model}, 試行={attempt+1}")
                
                process = subprocess.run([
                    'gemini', '--prompt', prompt, 
                    '--model', self.model_manager.current_model
                ], capture_output=True, text=True, timeout=30, encoding='utf-8')
                
                if process.returncode == 0:
                    logger.info(f"Gemini CLI成功: レスポンス長={len(process.stdout)}")
                    return process.stdout.strip()
                else:
                    error_msg = process.stderr.strip()
                    logger.warning(f"Gemini CLIエラー (試行{attempt+1}): {error_msg}")
                    
                    if "429" in error_msg or "quota" in error_msg.lower():
                        logger.warning("API制限エラー: 次のモデルに切り替え")
                        self.model_manager.get_next_model()
                    else:
                        break
                        
            except subprocess.TimeoutExpired:
                logger.warning(f"Gemini CLIタイムアウト (試行{attempt+1})")
                if attempt < max_retries - 1:
                    self.model_manager.get_next_model()
            except Exception as e:
                logger.error(f"Gemini CLI例外エラー (試行{attempt+1}): {e}")
                if attempt < max_retries - 1:
                    self.model_manager.get_next_model()
                    
        logger.error("全てのモデルで失敗")
        return "申し訳ありません。現在システムに問題が発生しています。"

class ChatFormatter:
    """メッセージ表示フォーマットクラス"""
    
    @staticmethod
    def format_message(persona_name, message, timestamp=None, interest_level=None):
        """メッセージをフォーマット - 興味度表示付き"""
        if timestamp is None:
            timestamp = datetime.now()
        time_str = timestamp.strftime("%H:%M:%S")
        
        persona_info = PersonaDefinitions.PERSONAS.get(persona_name, {})
        color = persona_info.get('color', '#FFFFFF')
        
        # 興味度アイコン
        interest_icon = ""
        if interest_level:
            icons = {
                "high_interest": "🔥",
                "medium_interest": "💭", 
                "low_interest": "😐"
            }
            interest_icon = icons.get(interest_level, "")
        
        return {
            'text': f"[{time_str}] {interest_icon}{persona_name}: {message}",
            'color': color,
            'timestamp': timestamp,
            'persona': persona_name
        }
        
    @staticmethod
    def format_user_message(message, timestamp=None):
        """ユーザーメッセージをフォーマット"""
        if timestamp is None:
            timestamp = datetime.now()
        time_str = timestamp.strftime("%H:%M:%S")
        
        return {
            'text': f"[{time_str}] 🙋あなた: {message}",
            'color': '#FFFF00',
            'timestamp': timestamp,
            'persona': 'user'
        }

class ThemeManager:
    """UIテーマ管理クラス"""
    
    THEMES = {
        'dos_green': {
            'bg': '#000000', 'fg': '#00FF00', 'select_bg': '#004000',
            'select_fg': '#00FF00', 'button_bg': '#004000', 'button_fg': '#00FF00',
            'entry_bg': '#001100', 'entry_fg': '#00FF00'
        },
        'dos_amber': {
            'bg': '#000000', 'fg': '#FFBF00', 'select_bg': '#404000',
            'select_fg': '#FFBF00', 'button_bg': '#404000', 'button_fg': '#FFBF00',
            'entry_bg': '#111100', 'entry_fg': '#FFBF00'
        },
        'dos_cyan': {
            'bg': '#000000', 'fg': '#00FFFF', 'select_bg': '#004040',
            'select_fg': '#00FFFF', 'button_bg': '#004040', 'button_fg': '#00FFFF',
            'entry_bg': '#001111', 'entry_fg': '#00FFFF'
        }
    }
    
    def __init__(self):
        self.current_theme = 'dos_green'
        
    def get_theme(self):
        return self.THEMES[self.current_theme]
        
    def set_theme(self, theme_name):
        if theme_name in self.THEMES:
            self.current_theme = theme_name

class GeminiAutoModelChat:
    """メインアプリケーション制御クラス - 完全版"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gemini CLI 多人格チャット - 完全版（18名・MBTI・ビッグ5・裏設定対応）")
        
        # DPI認識設定
        self.setup_dpi_awareness()
        
        # 画面サイズ最適化
        self.setup_optimal_window_size()
        
        logger.info("アプリケーション初期化開始")
        
        # 各種マネージャーの初期化
        self.model_manager = GeminiModelManager()
        self.history_manager = ChatHistoryManager()
        self.batch_processor = BatchConversationProcessor(self.model_manager)
        self.theme_manager = ThemeManager()
        
        # GUI状態管理
        self.font_size = 11
        self.auto_chat_active = False
        self.processing = False
        self.conversation_queue = queue.Queue()
        self.message_counter = 0
        self.typing_speed = 40
        
        # 会話履歴
        self.chat_history = self.history_manager.load_history()
        self.active_personas = list(PersonaDefinitions.PERSONAS.keys())
        
        # キーワード分析用
        self.recent_keywords = []
        
        # GUI構築
        self.setup_gui()
        self.apply_theme()
        self.load_history_to_display()
        
        # 自動会話スレッド開始
        self.start_auto_chat_thread()
        self.check_conversation_queue()
        
        logger.info("アプリケーション初期化完了")
    
    def setup_dpi_awareness(self):
        """DPI認識設定"""
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            logger.info("DPI認識設定完了")
        except Exception as e:
            logger.warning(f"DPI認識設定失敗: {e}")
    
    def setup_optimal_window_size(self):
        """画面解像度に基づく最適ウィンドウサイズ設定"""
        try:
            # 画面解像度取得
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # 画面の75%程度のサイズに調整
            app_width = min(1000, int(screen_width * 0.75))
            app_height = min(700, int(screen_height * 0.75))
            
            # 最小制限
            app_width = max(800, app_width)
            app_height = max(550, app_height)
            
            # 画面中央に配置
            x = (screen_width - app_width) // 2
            y = (screen_height - app_height) // 2
            
            self.root.geometry(f"{app_width}x{app_height}+{x}+{y}")
            self.root.minsize(800, 550)
            self.root.resizable(True, True)
            
            logger.info(f"画面サイズ最適化: {app_width}x{app_height} (画面解像度: {screen_width}x{screen_height})")
            
        except Exception as e:
            self.root.geometry("1000x700+100+100")
            self.root.minsize(800, 550)
            logger.warning(f"画面サイズ自動調整失敗、デフォルト使用: {e}")
        
    def setup_gui(self):
        """GUI要素の設定"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_toolbar()
        self.setup_center_area()
        self.setup_input_area()
        self.setup_status_bar()
        
    def setup_toolbar(self):
        """ツールバーの設定"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # テーマ選択
        ttk.Label(toolbar, text="テーマ:").pack(side=tk.LEFT, padx=(0, 5))
        self.theme_var = tk.StringVar(value=self.theme_manager.current_theme)
        theme_combo = ttk.Combobox(toolbar, textvariable=self.theme_var,
                                   values=list(self.theme_manager.THEMES.keys()),
                                   state="readonly", width=15)
        theme_combo.pack(side=tk.LEFT, padx=(0, 10))
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)
        
        # フォントサイズ
        ttk.Label(toolbar, text="フォントサイズ:").pack(side=tk.LEFT, padx=(0, 5))
        self.font_size_var = tk.StringVar(value=str(self.font_size))
        font_combo = ttk.Combobox(toolbar, textvariable=self.font_size_var,
                                  values=[str(i) for i in range(8, 25)],
                                  state="readonly", width=5)
        font_combo.pack(side=tk.LEFT, padx=(0, 10))
        font_combo.bind('<<ComboboxSelected>>', self.on_font_size_change)
        
        # 自動会話トグル
        self.auto_chat_var = tk.BooleanVar(value=self.auto_chat_active)
        auto_chat_btn = ttk.Checkbutton(toolbar, text="自動会話モード",
                                        variable=self.auto_chat_var,
                                        command=self.toggle_auto_chat)
        auto_chat_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 議論モードボタン
        discussion_btn = ttk.Button(toolbar, text="📢 議論開始", command=self.start_discussion)
        discussion_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 履歴クリア
        clear_btn = ttk.Button(toolbar, text="🗑️ 履歴クリア", command=self.clear_history)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # モデル表示
        self.model_label = ttk.Label(toolbar, text=f"🤖 モデル: {self.model_manager.current_model}")
        self.model_label.pack(side=tk.RIGHT)
        
    def setup_center_area(self):
        """中央エリアの設定"""
        center_frame = ttk.Frame(self.main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左側：チャット表示
        chat_frame = ttk.Frame(center_frame)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(chat_frame, text="💬 チャット（18名のペルソナ・MBTI・ビッグ5対応）").pack(anchor=tk.W)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state=tk.DISABLED,
            font=('Courier New', self.font_size),
            bg='#000000', fg='#00FF00', insertbackground='#00FF00',
            selectbackground='#004000'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # 右側：ペルソナ一覧
        persona_frame = ttk.Frame(center_frame)
        persona_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(persona_frame, text="👥 参加者一覧（18名・心理特性付き）").pack(anchor=tk.W)
        
        # 画面サイズに応じたリストボックスサイズ
        list_width = 28 if self.root.winfo_screenwidth() > 1366 else 25
        list_height = 22 if self.root.winfo_screenheight() > 768 else 20
        
        self.persona_listbox = tk.Listbox(
            persona_frame, width=list_width, height=list_height,
            font=('Courier New', self.font_size - 1),
            bg='#000000', fg='#00FF00', selectbackground='#004000'
        )
        self.persona_listbox.pack(fill=tk.BOTH, expand=True)
        
        # ペルソナ一覧を初期化（詳細情報付き）
        for name, persona in PersonaDefinitions.PERSONAS.items():
            hidden_traits = persona.get("hidden_traits", [])
            hidden_mark = "⚠️" if hidden_traits else ""
            mbti = persona.get("mbti", "----")
            status = f"{hidden_mark}{name}({persona['age']}) {mbti} - {persona['occupation']}"
            self.persona_listbox.insert(tk.END, status)
            
    def setup_input_area(self):
        """入力エリアの設定"""
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        # メッセージ入力
        self.message_entry = tk.Text(
            input_frame, height=3,
            font=('Courier New', self.font_size),
            bg='#001100', fg='#00FF00', insertbackground='#00FF00',
            wrap=tk.WORD
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', self.on_enter_key)
        self.message_entry.bind('<Control-Return>', self.send_message)
        
        # ボタンフレーム
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT)
        
        self.send_button = tk.Button(
            button_frame, text="📤 送信\n(Ctrl+Enter)", command=self.send_message,
            font=('Courier New', self.font_size - 2),
            bg='#004000', fg='#00FF00', activebackground='#006000',
            activeforeground='#00FF00'
        )
        self.send_button.pack()
        
    def setup_status_bar(self):
        """ステータスバーの設定"""
        self.status_bar = ttk.Label(
            self.main_frame, text="🚀 準備完了 - 18名のペルソナ（MBTI・ビッグ5・裏設定付き）が待機中",
            relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
        
    def apply_theme(self):
        """テーマを適用"""
        theme = self.theme_manager.get_theme()
        
        self.root.configure(bg=theme['bg'])
        self.chat_display.configure(
            bg=theme['bg'], fg=theme['fg'], insertbackground=theme['fg'],
            selectbackground=theme['select_bg']
        )
        self.persona_listbox.configure(
            bg=theme['bg'], fg=theme['fg'], selectbackground=theme['select_bg']
        )
        self.message_entry.configure(
            bg=theme['entry_bg'], fg=theme['entry_fg'], insertbackground=theme['entry_fg']
        )
        self.send_button.configure(
            bg=theme['button_bg'], fg=theme['button_fg'],
            activebackground=theme['select_bg'], activeforeground=theme['select_fg']
        )
        
    def on_theme_change(self, event=None):
        """テーマ変更時の処理"""
        self.theme_manager.set_theme(self.theme_var.get())
        self.apply_theme()
        logger.info(f"テーマ変更: {self.theme_var.get()}")
        
    def on_font_size_change(self, event=None):
        """フォントサイズ変更時の処理"""
        try:
            new_size = int(self.font_size_var.get())
            self.font_size = new_size
            
            self.chat_display.configure(font=('Courier New', self.font_size))
            self.persona_listbox.configure(font=('Courier New', self.font_size - 1))
            self.message_entry.configure(font=('Courier New', self.font_size))
            self.send_button.configure(font=('Courier New', self.font_size - 2))
            logger.info(f"フォントサイズ変更: {new_size}")
        except ValueError:
            pass
            
    def on_enter_key(self, event):
        """Enterキー処理"""
        if event.state & 0x4:  # Ctrl+Enter
            self.send_message()
            return 'break'
            
    def send_message(self, event=None):
        """メッセージ送信処理"""
        if self.processing:
            logger.warning("処理中のため送信をスキップ")
            return
            
        message = self.message_entry.get('1.0', tk.END).strip()
        if not message:
            return
            
        logger.info(f"ユーザーメッセージ送信: '{message[:50]}...'")
        
        # ユーザーメッセージを表示
        self.add_message_to_display(ChatFormatter.format_user_message(message))
        
        # 入力欄をクリア
        self.message_entry.delete('1.0', tk.END)
        
        # 履歴に追加
        self.chat_history.append({
            'type': 'user', 'message': message, 'timestamp': datetime.now()
        })
        
        # キーワード分析
        self._analyze_keywords(message)
        
        # 動的バッチ処理でAI応答生成
        self.process_ai_responses(message)
        
    def _analyze_keywords(self, message):
        """キーワード分析"""
        words = re.findall(r'[一-龠ぁ-んァ-ンa-zA-Z]{2,}', message)
        self.recent_keywords.extend(words)
        if len(self.recent_keywords) > 50:
            self.recent_keywords = self.recent_keywords[-50:]
        logger.debug(f"キーワード更新: {words}")
        
    def start_discussion(self):
        """議論モード開始"""
        message = self.message_entry.get('1.0', tk.END).strip()
        if not message:
            messagebox.showwarning("警告", "議論テーマを入力してください")
            return
            
        logger.info(f"動的議論モード開始: テーマ='{message}'")
        self.message_entry.delete('1.0', tk.END)
        
        # テーマメッセージを表示
        theme_msg = f"📢 議論テーマ: {message}"
        self.add_message_to_display({
            'text': f"[{datetime.now().strftime('%H:%M:%S')}] 🤖システム: {theme_msg}",
            'color': '#FFFF00', 'timestamp': datetime.now(), 'persona': 'system'
        })
        
        # 動的議論開始
        threading.Thread(target=self._dynamic_discussion_thread, args=(message,), daemon=True).start()
        
    def _dynamic_discussion_thread(self, topic):
        """動的議論スレッド処理"""
        try:
            logger.info(f"動的議論スレッド開始: {topic}")
            context = self.create_context()
            
            # 全ペルソナの議論参加を動的決定
            discussions = []
            for persona_name in self.active_personas:
                try:
                    # 興味レベル分析
                    interest_level = self.batch_processor.prompt_generator.analyze_interest_level(
                        persona_name, topic
                    )
                    
                    # 動的議論プロンプト生成
                    prompt = self.batch_processor.prompt_generator.generate_dynamic_prompt(
                        persona_name, f"議論テーマ: {topic}", context, interest_level
                    )
                    
                    # 特別な議論用指示を追加
                    discussion_prompt = f"""
{prompt}

【特別指示】これは全員参加の議論セッションです。
テーマ「{topic}」について、あなたの立場から意見を述べてください。
興味レベル（{interest_level}）に応じて発言の詳しさを調整してください。
"""
                    
                    response = self.batch_processor._call_gemini_cli(discussion_prompt)
                    
                    discussions.append({
                        'persona': persona_name,
                        'message': response.strip(),
                        'timestamp': datetime.now(),
                        'interest_level': interest_level
                    })
                    
                    logger.debug(f"動的議論応答生成: {persona_name} ({interest_level})")
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    logger.error(f"動的議論応答生成エラー ({persona_name}): {e}")
                    
            # 興味度順でソート（高い興味のペルソナから発言）
            discussions.sort(key=lambda x: {"high_interest": 3, "medium_interest": 2, "low_interest": 1}[x['interest_level']], reverse=True)
            
            # 応答を時間差で表示
            for i, discussion in enumerate(discussions):
                delay = random.uniform(1.0, 3.0) * (i + 1)
                self.root.after(int(delay * 1000), 
                               lambda d=discussion: self.conversation_queue.put(d))
                               
        except Exception as e:
            logger.error(f"動的議論スレッドエラー: {e}")
            
    def process_ai_responses(self, user_message):
        """AI応答を動的バッチ処理"""
        if self.processing:
            return
            
        self.processing = True
        self.update_status("🧠 AI応答を動的生成中...")
        
        def generate_responses():
            try:
                context = self.create_context()
                conversations = self.batch_processor.generate_batch_conversation(
                    context, user_message, self.active_personas
                )
                
                # 興味度に応じた時間差表示
                for i, conv in enumerate(conversations):
                    # 興味度による表示間隔調整
                    base_delay = {
                        "high_interest": 2.0,   # 興味があると早めに反応
                        "medium_interest": 4.0,  # 普通
                        "low_interest": 6.0     # 興味がないと遅め
                    }
                    
                    interest_level = conv.get('interest_level', 'medium_interest')
                    delay = base_delay[interest_level] + random.uniform(0.5, 1.5) * i
                    
                    self.root.after(int(delay * 1000), 
                                   lambda c=conv: self.conversation_queue.put(c))
                    
            except Exception as e:
                logger.error(f"動的AI応答生成エラー: {e}")
                self.root.after(0, lambda: self.update_status("❌ エラーが発生しました"))
            finally:
                self.root.after(0, lambda: setattr(self, 'processing', False))
                
        threading.Thread(target=generate_responses, daemon=True).start()
        
    def create_context(self):
        """会話コンテキストを作成"""
        recent_history = self.chat_history[-10:]
        context_lines = []
        
        for item in recent_history:
            if item['type'] == 'user':
                context_lines.append(f"ユーザー: {item['message']}")
            elif item['type'] == 'ai':
                context_lines.append(f"{item['persona']}: {item['message']}")
                
        return '\n'.join(context_lines)
        
    def check_conversation_queue(self):
        """会話キューをチェックして表示"""
        try:
            while True:
                conversation = self.conversation_queue.get_nowait()
                self.display_ai_response(conversation)
        except queue.Empty:
            pass
            
        self.root.after(100, self.check_conversation_queue)
        
    def display_ai_response(self, conversation):
        """AI応答を表示 - 興味度対応タイピングエフェクト"""
        interest_level = conversation.get('interest_level', 'medium_interest')
        
        formatted = ChatFormatter.format_message(
            conversation['persona'], conversation['message'], 
            conversation['timestamp'], interest_level
        )
        
        # 興味度に応じたタイピング速度
        typing_speeds = {
            "high_interest": 25,    # 速い（興奮している）
            "medium_interest": 40,  # 普通
            "low_interest": 70      # 遅い（あまり乗り気でない）
        }
        
        original_speed = self.typing_speed
        self.typing_speed = typing_speeds[interest_level]
        
        self.add_message_to_display_with_typing(formatted)
        
        # 元の速度に戻す
        self.typing_speed = original_speed
        
        # 履歴に追加
        self.chat_history.append({
            'type': 'ai', 'persona': conversation['persona'],
            'message': conversation['message'], 'timestamp': conversation['timestamp'],
            'interest_level': interest_level
        })
        
        self.history_manager.save_history(self.chat_history)
        self.update_status("✅ 準備完了")
        
    def add_message_to_display_with_typing(self, formatted_message):
        """タイピングエフェクト付きメッセージ表示"""
        text = formatted_message['text']
        wrapped_text = self.wrap_text(text, 50)
        color = formatted_message['color']
        
        self.message_counter += 1
        tag_name = f"msg_{self.message_counter}_{formatted_message.get('persona', 'user')}"
        
        # タイピングエフェクト開始
        self._typing_effect_safe(wrapped_text, tag_name, color)
        
    def _typing_effect_safe(self, text, tag_name, color):
        """安全なタイピングエフェクト実装 - 文字化け修正版"""
        self.chat_display.configure(state=tk.NORMAL)
        
        # Unicode正規化で文字化け防止
        safe_text = unicodedata.normalize('NFC', text)
        
        # 開始位置を記録
        start_pos = self.chat_display.index("end-1c")
        
        def type_char(index=0):
            if index < len(safe_text):
                try:
                    char = safe_text[index]
                    
                    # 安全な文字挿入
                    self.chat_display.insert("end", char)
                    
                    # 初回でタグ設定
                    if index == 0:
                        self.chat_display.tag_add(tag_name, start_pos, "end-1c")
                        self.chat_display.tag_config(tag_name, foreground=color)
                    
                    # 文字に応じた待機時間
                    delay = self.typing_speed
                    if char in '。！？\n':
                        delay *= 3
                    elif char in '、':
                        delay *= 2
                    
                    self.chat_display.after(delay, lambda: type_char(index + 1))
                    self.chat_display.see("end")
                    
                except Exception as e:
                    logger.error(f"文字挿入エラー: {e}, char: {repr(char) if 'char' in locals() else 'unknown'}")
                    self.chat_display.after(self.typing_speed, lambda: type_char(index + 1))
            else:
                # タイピング完了（2行改行で読みやすく）
                self.chat_display.insert("end", '\n\n')
                self.chat_display.configure(state=tk.DISABLED)
                
        type_char()
        
    def add_message_to_display(self, formatted_message):
        """通常のメッセージ表示（即座）"""
        self.chat_display.configure(state=tk.NORMAL)
        
        text = formatted_message['text']
        wrapped_text = self.wrap_text(text, 50)
        
        # Unicode正規化
        safe_text = unicodedata.normalize('NFC', wrapped_text)
        
        start_pos = self.chat_display.index("end-1c")
        self.chat_display.insert("end", safe_text + '\n\n')  # 2行改行
        end_pos = self.chat_display.index("end-2c")
        
        self.message_counter += 1
        tag_name = f"msg_{self.message_counter}_{formatted_message.get('persona', 'user')}"
        
        self.chat_display.tag_add(tag_name, start_pos, end_pos)
        self.chat_display.tag_config(tag_name, foreground=formatted_message['color'])
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see("end")
        
    def wrap_text(self, text, width):
        """テキストを指定幅で自動改行"""
        if len(text) <= width:
            return text
            
        lines = []
        current_line = ""
        
        for char in text:
            current_line += char
            if len(current_line) >= width:
                # 改行位置を調整
                break_pos = len(current_line)
                for i in range(len(current_line) - 1, -1, -1):
                    if current_line[i] in ' 、。！？）】':
                        break_pos = i + 1
                        break
                        
                lines.append(current_line[:break_pos])
                current_line = current_line[break_pos:]
                
        if current_line:
            lines.append(current_line)
            
        return '\n'.join(lines)
        
    def load_history_to_display(self):
        """保存された履歴をチャット表示に読み込み"""
        for item in self.chat_history:
            if item['type'] == 'user':
                formatted = ChatFormatter.format_user_message(
                    item['message'], item.get('timestamp')
                )
            elif item['type'] == 'ai':
                formatted = ChatFormatter.format_message(
                    item['persona'], item['message'], item.get('timestamp'),
                    item.get('interest_level')
                )
            else:
                continue
                
            self.add_message_to_display(formatted)
            
    def toggle_auto_chat(self):
        """自動会話モードの切り替え"""
        self.auto_chat_active = self.auto_chat_var.get()
        status = "有効" if self.auto_chat_active else "無効"
        self.update_status(f"🤖 自動会話モード: {status}")
        logger.info(f"自動会話モード: {status}")
        
    def start_auto_chat_thread(self):
        """自動会話スレッドを開始 - 動的プロンプト版"""
        def auto_chat_loop():
            while True:
                try:
                    if self.auto_chat_active and not self.processing:
                        if random.random() < 0.3:  # 30%でキーワード深掘り
                            self.generate_dynamic_keyword_drill()
                        else:
                            self.generate_dynamic_auto_conversation()
                        
                    time.sleep(random.randint(15, 30))
                except Exception as e:
                    logger.error(f"自動会話ループエラー: {e}")
                    time.sleep(60)
                
        threading.Thread(target=auto_chat_loop, daemon=True).start()
        
    def generate_dynamic_keyword_drill(self):
        """動的キーワード深掘り会話を生成"""
        if not self.recent_keywords:
            return
            
        try:
            # 頻出キーワードを選択
            keyword_counts = Counter(self.recent_keywords)
            if not keyword_counts:
                return
                
            keyword = keyword_counts.most_common(1)[0][0]
            
            # キーワードに最も興味を持ちそうなペルソナを選択
            interested_personas = []
            for name, persona in PersonaDefinitions.PERSONAS.items():
                if any(kw in persona["keywords"] for kw in [keyword]):
                    interested_personas.append(name)
                    
            if not interested_personas:
                interested_personas = random.sample(self.active_personas, 2)
            else:
                interested_personas = random.sample(interested_personas, 
                                                   min(2, len(interested_personas)))
                
            # 深掘り会話生成
            asker = interested_personas[0]
            responder = interested_personas[1] if len(interested_personas) > 1 else random.choice(self.active_personas)
            
            # 質問者の動的プロンプト
            context = self.create_context()
            question_prompt = self.batch_processor.prompt_generator.generate_dynamic_prompt(
                asker, f"最近話題になった「{keyword}」について", context, "high_interest"
            )
            
            question_prompt += f"\n\n【特別指示】「{keyword}」について、{responder}さんに質問してください。自然な会話として。"
            
            question_response = self.batch_processor._call_gemini_cli(question_prompt)
            
            # 回答者の動的プロンプト
            answer_prompt = self.batch_processor.prompt_generator.generate_dynamic_prompt(
                responder, f"{asker}からの質問: {question_response}", context, "high_interest"
            )
            
            answer_response = self.batch_processor._call_gemini_cli(answer_prompt)
            
            # 時間差で表示
            conversations = [
                {
                    'persona': asker,
                    'message': question_response.strip(),
                    'timestamp': datetime.now(),
                    'interest_level': 'high_interest'
                },
                {
                    'persona': responder,
                    'message': answer_response.strip(),
                    'timestamp': datetime.now(),
                    'interest_level': 'high_interest'
                }
            ]
            
            for i, conv in enumerate(conversations):
                delay = (i + 1) * 3000  # 3秒間隔
                self.root.after(delay, lambda c=conv: self.conversation_queue.put(c))
            
            logger.info(f"動的キーワード深掘り生成: {keyword} ({asker} -> {responder})")
            
        except Exception as e:
            logger.error(f"動的キーワード深掘りエラー: {e}")
            
    def generate_dynamic_auto_conversation(self):
        """動的自動会話を生成"""
        try:
            topics = [
                "最近の天気について", "今日のニュース", "おすすめの映画",
                "健康について", "仕事の話", "趣味について", "最近読んだ本",
                "料理のレシピ", "旅行の思い出", "将来の夢", "テクノロジーの進歩",
                "音楽の話", "スポーツ", "アニメ・漫画"
            ]
            topic = random.choice(topics)
            
            # 興味度に基づく参加者選択
            participants = []
            for persona_name in self.active_personas:
                interest_level = self.batch_processor.prompt_generator.analyze_interest_level(
                    persona_name, topic
                )
                
                participation_probability = {
                    "high_interest": 0.6,
                    "medium_interest": 0.3,
                    "low_interest": 0.1
                }
                
                if random.random() < participation_probability[interest_level]:
                    participants.append((persona_name, interest_level))
            
            # 最低1名、最大3名に調整
            if not participants:
                random_persona = random.choice(self.active_personas)
                participants = [(random_persona, "medium_interest")]
            elif len(participants) > 3:
                participants = participants[:3]
                
            # 各参加者の発言生成
            conversations = []
            context = self.create_context()
            
            for persona_name, interest_level in participants:
                try:
                    prompt = self.batch_processor.prompt_generator.generate_dynamic_prompt(
                        persona_name, f"自由話題: {topic}", context, interest_level
                    )
                    
                    prompt += f"\n\n【特別指示】「{topic}」について自発的に発言してください。自然な会話として。"
                    
                    response = self.batch_processor._call_gemini_cli(prompt)
                    
                    conversations.append({
                        'persona': persona_name,
                        'message': response.strip(),
                        'timestamp': datetime.now(),
                        'interest_level': interest_level
                    })
                    
                except Exception as e:
                    logger.error(f"動的自動会話生成エラー ({persona_name}): {e}")
                    
            # 興味度順で時間差表示
            conversations.sort(key=lambda x: {"high_interest": 3, "medium_interest": 2, "low_interest": 1}[x['interest_level']], reverse=True)
            
            for i, conv in enumerate(conversations):
                delay = random.uniform(2.0, 5.0) * (i + 1)
                self.root.after(int(delay * 1000), 
                               lambda c=conv: self.conversation_queue.put(c))
                               
            logger.info(f"動的自動会話生成: {topic} ({[c['persona'] for c in conversations]})")
            
        except Exception as e:
            logger.error(f"動的自動会話生成エラー: {e}")
            
    def clear_history(self):
        """履歴をクリア"""
        if messagebox.askyesno("確認", "会話履歴をクリアしますか？"):
            self.chat_history.clear()
            self.history_manager.clear_history()
            self.recent_keywords.clear()
            
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.delete('1.0', tk.END)
            self.chat_display.configure(state=tk.DISABLED)
            
            self.update_status("🗑️ 履歴をクリアしました")
            logger.info("履歴クリア実行")
            
    def update_status(self, message):
        """ステータスバーを更新"""
        self.status_bar.configure(text=message)
        self.model_label.configure(text=f"🤖 モデル: {self.model_manager.current_model}")
        
    def run(self):
        """アプリケーション実行"""
        try:
            logger.info("アプリケーション開始")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("アプリケーション中断")
        finally:
            self.history_manager.save_history(self.chat_history)
            logger.info("アプリケーション終了")

def main():
    """メイン関数"""
    try:
        # Gemini CLIの存在確認
        result = subprocess.run(['gemini', '--version'], 
                              capture_output=True, check=True)
        logger.info(f"Gemini CLI確認成功: {result.stdout.decode().strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        error_msg = "エラー: Gemini CLIがインストールされていません。\n" \
                   "インストール方法: npm install -g @google/gemini-cli"
        logger.error(error_msg)
        print(error_msg)
        sys.exit(1)
        
    # アプリケーション実行
    app = GeminiAutoModelChat()
    app.run()

if __name__ == "__main__":
    main()
