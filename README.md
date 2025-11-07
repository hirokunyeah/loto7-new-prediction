# ロト7 分析・予測システム

Flask ベースのロト7（日本の宝くじ）番号分析および予測システムです。

## 機能

### 1. 過去の抽選結果表示
- JSONファイルから過去のロト7抽選結果を読み込んで表示
- 視覚的なボール表示と番号分布バーで見やすく表示
- 本数字とボーナス数字を色分けして表示
- **フィルタ評価表示**: 各当選番号が7つのフィルタ条件を満たしているか表示
- **データダウンロード**: 表示中のデータをJSON形式でダウンロード可能
- **古い順表示**: 過去データは古いものから新しいものの順に表示

### 2. 番号予測機能（統計分析・スコアリング強化版）
- 統計的フィルターを使用した次回当選番号の予測
- **同一回の複数候補表示**: 次回の回に対して複数の候補を生成（例：第651回 - 候補1、候補2...）
- **過去の当選番号も同時表示**: 予測生成時に、参考として過去5件の当選番号を表示
- 以下の7つのフィルター条件を適用：
  1. **連続番号**: 連続する番号の数をチェック
  2. **ゾーン3分布**: 1-12, 13-24, 25-37の3ゾーンへの分散
  3. **ゾーン4分布**: 1-9, 10-18, 19-27, 28-37の4ゾーンへの分散
  4. **奇数・偶数バランス**: 奇数と偶数の個数バランス
  5. **合計値範囲**: 7つの番号の合計値の範囲チェック
  6. **下一桁分布**: 下一桁（0-9）の重複チェック
  7. **前回引継**: 前回抽選との重複個数チェック
- **スコアリングシステム**: 各予測候補に0-100点のスコアを付与
  - 各フィルタの重み付け評価
  - 過去データに基づく頻度分析
  - ホット/コールド/期限切れ数字の総合評価
- **自動ランキング**: スコアに基づいて予測候補を自動的にランク付け
- **統計的インサイト**: ホット数字、コールド数字、期限切れ数字の分析
- **パターン分析**: 過去の抽選から傾向とパターンを識別
- **カスタマイズ可能なフィルタ**: フィルタの重みと閾値をカスタム設定可能
- **各候補の評価値表示**: 各予測候補が各フィルタで合格/不合格かを可視化
- **予測結果ダウンロード**: 生成した予測データをJSON形式でダウンロード可能

### 3. 統計分析機能
- **ホット数字分析**: 最近の抽選で頻繁に出現している数字
- **コールド数字分析**: 出現頻度が低い数字
- **期限切れ数字分析**: 長期間出現していない数字
- **時系列トレンド分析**: 過去N回の抽選における数字の出現傾向
- **パターン認識**: 連続数字、ゾーン分布、奇数/偶数比率のパターン
- **バランス分析**: 数字の分布とバランスの評価

### 4. データ管理
- JSONファイルのアップロード機能
- データの検証と読み込み
- 文字列形式（"01", "08"）と数値形式（1, 8）の両方に対応

## プロジェクト構成

```
loto7/
├── server.py              # アプリケーションエントリーポイント
├── config.py              # アプリケーション設定
├── requirements.txt       # Python依存パッケージ
├── pytest.ini             # pytest設定ファイル
├── conftest.py            # pytest共通フィクスチャ
├── app/                   # メインアプリケーションパッケージ
│   ├── __init__.py       # Flaskアプリケーションファクトリ
│   ├── models.py         # データモデル（Loto7Draw）
│   ├── api/              # APIエンドポイント
│   │   └── __init__.py   # API Blueprint
│   ├── main/             # メインルート
│   │   └── __init__.py   # メインページBlueprint
│   └── services/         # ビジネスロジック
│       ├── __init__.py
│       ├── data_service.py              # データ操作サービス
│       ├── prediction_service.py        # 予測ロジックサービス
│       └── statistical_analyzer.py      # 統計分析・スコアリングサービス
├── tests/                # テストスイート
│   ├── __init__.py
│   ├── test_models.py                 # データモデルのテスト
│   ├── test_data_service.py           # データサービスのテスト
│   ├── test_prediction_service.py     # 予測サービスのテスト（7フィルタ重点）
│   ├── test_statistical_analyzer.py   # 統計分析機能のテスト
│   ├── test_api.py                    # APIエンドポイントのテスト
│   └── test_api_enhanced.py           # 拡張API機能のテスト
├── templates/            # HTMLテンプレート
│   └── index.html       # メインページ
├── static/              # 静的ファイル
│   └── assets/
│       └── loto7_data.json  # 過去の抽選データ
└── archive/             # 旧ファイル（アーカイブ）
```

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. アプリケーションの起動

```bash
python server.py
```

サーバーは `http://0.0.0.0:5000` で起動します。

### 3. テストの実行

```bash
# 全てのテストを実行
pytest

# カバレッジレポート付きで実行
pytest --cov=app --cov-report=html

# ユニットテストのみ実行
pytest -m unit

# APIテストのみ実行
pytest -m api

# 統合テストのみ実行
pytest -m integration

# 詳細な出力で実行
pytest -v
```

HTMLカバレッジレポートは `htmlcov/index.html` で確認できます。

## API エンドポイント

### GET `/api/data`
過去の抽選結果を取得

**クエリパラメータ:**
- `evaluation` (optional): `true` を指定すると、各当選番号のフィルタ評価を含める

**レスポンス:**
```json
{
  "success": true,
  "draws": [
    {
      "id": "第650回",
      "date": "2024-10-31",
      "main": [1, 8, 10, 14, 25, 33, 35],
      "bonus": [12, 21],
      "evaluation": {
        "continuous": {"count": 0, "pass": true},
        "zone3": {"distribution": [2, 2, 3], "pass": true},
        "zone4": {"distribution": [2, 2, 2, 1], "pass": true},
        "odd_even": {"odd": 4, "even": 3, "pass": true},
        "sum": {"total": 126, "range": "91-175", "pass": true},
        "last_digits": {"distribution": {...}, "max_count": 2, "pass": true},
        "pull": {"count": 2, "valid_range": "1-3", "pass": true}
      }
    }
  ],
  "count": 8,
  "has_evaluation": true
}
```

### POST `/api/predict`
番号予測を生成（統計分析・スコアリング機能付き）

**リクエスト:**
```json
{
  "count": 10,
  "next_draw_number": 651,
  "include_scoring": true,
  "include_patterns": true,
  "filter_config": {
    "sum_min": 100,
    "sum_max": 170,
    "continuous_weight": 10.0,
    "zone3_weight": 15.0,
    "zone4_weight": 15.0,
    "odd_even_weight": 10.0,
    "sum_weight": 15.0,
    "last_digit_weight": 10.0,
    "pull_weight": 10.0,
    "frequency_weight": 15.0
  }
}
```

**パラメータ:**
- `count` (required): 生成する予測候補数（1-100）
- `next_draw_number` (optional): 次回の回数（自動計算可能）
- `include_scoring` (optional): スコアリングを有効化（デフォルト: true）
- `include_patterns` (optional): パターン分析を含める（デフォルト: false）
- `filter_config` (optional): カスタムフィルタ設定

**レスポンス:**
```json
{
  "success": true,
  "draws": [
    {
      "id": "第651回 候補1",
      "date": "2025-11-12",
      "main": [2, 5, 11, 19, 27, 31, 36],
      "bonus": [8, 15],
      "evaluation": {
        "continuous": {"count": 0, "pass": true},
        "zone3": {"distribution": [2, 2, 3], "pass": true},
        "zone4": {"distribution": [1, 2, 2, 2], "pass": true},
        "odd_even": {"odd": 4, "even": 3, "pass": true},
        "sum": {"total": 131, "range": "100-170", "pass": true},
        "last_digits": {"max_count": 2, "pass": true},
        "pull": {"count": 1, "pass": true},
        "scoring": {
          "final_score": 95.65,
          "scores": {
            "continuous": 100.0,
            "zone3": 100.0,
            "zone4": 100.0,
            "odd_even": 100.0,
            "sum": 100.0,
            "last_digits": 100.0,
            "pull": 100.0,
            "frequency": 71.02
          },
          "weights": {
            "continuous": 10.0,
            "zone3": 15.0,
            "zone4": 15.0,
            "odd_even": 10.0,
            "sum": 15.0,
            "last_digits": 10.0,
            "pull": 10.0,
            "frequency": 15.0
          }
        }
      }
    },
    {
      "id": "第651回 候補2",
      ...
    }
  ],
  "count": 10,
  "next_draw_number": 651,
  "message": "第651回の予測候補を10件生成しました。",
  "patterns": [
    {
      "type": "consecutive",
      "description": "Average 0.5 consecutive pairs in recent draws",
      "value": 0.5
    },
    {
      "type": "zone_distribution",
      "description": "Zone distribution in recent draws",
      "value": {"low": 31.4, "mid": 34.3, "high": 34.3}
    },
    {
      "type": "odd_even_ratio",
      "description": "Average 3.9 odd numbers in recent draws",
      "value": 3.9
    }
  ],
  "insights": {
    "hot_numbers": [
      {"number": 35, "score": 90.5, "frequency": 9},
      {"number": 33, "score": 85.2, "frequency": 7},
      ...
    ],
    "cold_numbers": [
      {"number": 6, "score": 100.0, "frequency": 0},
      {"number": 30, "score": 100.0, "frequency": 0},
      ...
    ],
    "overdue_numbers": [
      {"number": 6, "score": 100.0, "last_seen": "Never"},
      {"number": 30, "score": 95.5, "last_seen": 15},
      ...
    ]
  }
}
```

### POST `/api/upload`
JSONファイルをアップロードしてデータを読み込む

**リクエスト:** `multipart/form-data` で `file` フィールド

**レスポンス:**
```json
{
  "success": true,
  "draws": [...],
  "count": 8,
  "message": "8件のデータを読み込みました。"
}
```

### GET `/api/stats`
基本統計情報を取得

**レスポンス:**
```json
{
  "success": true,
  "stats": {
    "total_draws": 8,
    "most_common_main": [[35, 4], [12, 3], ...],
    "most_common_bonus": [[2, 2], [21, 1], ...],
    "latest_draw": {...}
  }
}
```

### GET `/api/insights`
高度な統計分析とインサイトを取得（新機能）

**レスポンス:**
```json
{
  "success": true,
  "insights": {
    "hot_numbers": [
      {"number": 35, "score": 90.5, "frequency": 9},
      {"number": 33, "score": 85.2, "frequency": 7},
      {"number": 1, "score": 78.3, "frequency": 6},
      ...
    ],
    "cold_numbers": [
      {"number": 6, "score": 100.0, "frequency": 0},
      {"number": 30, "score": 100.0, "frequency": 0},
      {"number": 2, "score": 55.95, "frequency": 1},
      ...
    ],
    "overdue_numbers": [
      {"number": 6, "score": 100.0, "last_seen": "Never"},
      {"number": 30, "score": 95.5, "last_seen": 15},
      {"number": 20, "score": 75.2, "last_seen": 8},
      ...
    ],
    "patterns": [
      {
        "type": "consecutive",
        "description": "Average 0.5 consecutive pairs in recent draws",
        "value": 0.5
      },
      {
        "type": "zone_distribution",
        "description": "Zone distribution in recent draws",
        "value": {"low": 31.4, "mid": 34.3, "high": 34.3}
      },
      {
        "type": "odd_even_ratio",
        "description": "Average 3.9 odd numbers in recent draws",
        "value": 3.9
      }
    ]
  },
  "patterns": [...],
  "total_draws_analyzed": 12
}
```

## データフォーマット

### loto7_data.json

```json
{
  "draws": [
    {
      "id": "第650回",
      "date": "2024-10-31",
      "main": [1, 8, 10, 14, 25, 33, 35],
      "bonus": [12, 21]
    },
    {
      "id": "第649回",
      "date": "2024-10-25",
      "main": [12, 22, 23, 26, 33, 35, 37],
      "bonus": [2, 21]
    }
  ]
}
```

**注意**: `main` と `bonus` は数値配列または文字列配列のどちらでも対応しています。
- 数値形式: `[1, 8, 10, 14, 25, 33, 35]`
- 文字列形式: `["01", "08", "10", "14", "25", "33", "35"]`

## アーキテクチャの特徴

### Flask Application Factory パターン
- `create_app()` 関数で環境に応じた設定が可能
- テスタビリティの向上

### Blueprint による機能分離
- `main` Blueprint: メインページ
- `api` Blueprint: APIエンドポイント

### サービス層の分離
- `DataService`: データの読み込み・保存・検証
- `PredictionService`: 予測ロジック

### データモデルの明確化
- `Loto7Draw` dataclass: 型安全性の確保
- バリデーション機能の統合
- 評価データの動的追加サポート
- 文字列・数値形式の自動変換

## 使い方

### 1. 過去の結果を表示
1. 「📊 過去の結果」タブを選択
2. （オプション）「フィルタ評価を表示する」にチェックを入れる
3. 「過去の結果を表示」ボタンをクリック
4. データをダウンロードする場合は「📥 JSONダウンロード」ボタンをクリック

### 2. 番号予測を生成
1. 「🔮 番号予測」タブを選択
2. 候補数（1-100）を入力
3. （オプション）次回の回数を指定（自動計算される）
4. 「予測を生成」ボタンをクリック
5. 過去5件の当選番号と予測候補が表示される
6. 各候補のフィルタ評価を確認できる
7. 予測データをダウンロードする場合は、予測結果ヘッダーの「📥 JSONダウンロード」ボタンをクリック

### 3. データファイルの読み込み
1. 「📁 ファイル読込」タブを選択
2. JSONファイルを選択
3. 「ファイルを読み込む」ボタンをクリック

## 環境設定

`config.py` で以下の環境を切り替え可能：

- `development`: 開発環境（デバッグモード有効）
- `production`: 本番環境（デバッグモード無効）

環境の指定:
```python
app = create_app('production')
```

## ライセンス

このプロジェクトは個人使用・学習目的で作成されています。

## 今後の拡張可能性

- データベースへの移行（SQLite、PostgreSQLなど）
- 機械学習モデルの統合
- ユーザー認証機能
- 予測精度の追跡と分析
- REST API の認証
- ~~フィルタ条件のカスタマイズ機能~~ ✅ 実装済み (v3.0.0)
- ~~統計分析の強化（出現頻度、相関分析など）~~ ✅ 実装済み (v3.0.0)
- グラフ表示機能（時系列、分布図など）
- WebSocket によるリアルタイム更新
- 複数予測戦略の比較機能
- エクスポート機能の拡張（CSV、Excel）

## 技術スタック

- **バックエンド**: Flask 3.0.0
- **フロントエンド**: HTML5, CSS3, JavaScript (Vanilla)
- **データ形式**: JSON
- **Python**: 3.12+
- **テストフレームワーク**: pytest 7.4.3, pytest-flask 1.3.0
- **カバレッジツール**: pytest-cov 4.1.0
- **アーキテクチャ**: Application Factory パターン, Blueprint, サービス層分離

## テスト戦略

### テストアプローチ
1. **一時JSONファイル作成**: `tempfile`を使用した実ファイルベースのテスト
2. **完全モック**: `unittest.mock`によるファイルI/Oの完全モック化
3. **重要機能重点テスト**: 7つのフィルタロジックと主要APIエンドポイントに集中

### テストカバレッジ
- **全体カバレッジ**: 95%
- **総テストケース数**: 121件
  - データモデル（Loto7Draw）: 11件
  - データサービス: 19件
  - 予測サービス（7フィルタ含む）: 39件
  - 統計分析サービス: 16件（新規）
  - APIエンドポイント: 24件
  - 拡張API機能: 10件（新規）
  - 統合テスト: 2件

### テストマーカー
- `@pytest.mark.unit`: ユニットテスト（85件）
- `@pytest.mark.api`: APIエンドポイントテスト（34件）
- `@pytest.mark.integration`: 統合テスト（2件）

## 変更履歴

### v3.0.0 (2025-11-05) - 統計分析・スコアリングシステム
- ✨ 統計分析システムを追加
  - ホット/コールド/期限切れ数字分析
  - 時系列トレンド分析
  - パターン認識（連続数字、ゾーン分布、奇数/偶数比率）
- ✨ スコアリングシステムを実装
  - 0-100点スケールでの予測評価
  - 各フィルタの重み付け評価
  - 過去データに基づく頻度分析
- ✨ 自動ランキング機能
  - スコアに基づく予測候補の自動ランク付け
- ✨ カスタマイズ可能なフィルタ設定
  - フィルタの重みと閾値を API 経由でカスタマイズ可能
- ✨ 新しい `/api/insights` エンドポイントを追加
  - 統計インサイトの取得
  - パターン分析結果の取得
- 🔧 `/api/predict` エンドポイントを拡張
  - スコアリング機能の統合
  - パターン分析の組み込み
  - カスタムフィルタ設定のサポート
- ✅ 26件の新しいテストを追加（統計分析: 16件、API: 10件）
- ✅ 95%のコードカバレッジを達成

### v2.1.0 (2025-11-05)
- ✅ 包括的なunitテストスイートを追加（95テストケース）
- ✅ pytest、pytest-flask、pytest-covを導入
- ✅ 94%のコードカバレッジを達成
- ✅ 7つのフィルタロジックの詳細なテスト
- ✅ API エンドポイントの完全なテストカバレッジ
- ✅ 一時ファイルとモックを使用したテスト戦略
- ✅ HTMLカバレッジレポート生成機能

### v2.0.0 (2025-10-31)
- ✨ フィルタ評価表示機能を追加
- ✨ データダウンロード機能を追加（過去データ・予測データ）
- ✨ 予測生成時に過去5件の当選番号も表示
- 🔧 予測ロジックを「次回の複数候補」方式に変更
- 🔧 データ表示順序を古い順に統一
- 🐛 文字列形式と数値形式の混在データに対応
- 💄 UIデザインの改善（グラデーション、レイアウト）

### v1.0.0 (初期版)
- 基本的な過去データ表示機能
- 番号予測機能
- ファイルアップロード機能
