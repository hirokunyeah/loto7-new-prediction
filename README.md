# ロト7 分析・予測システム

Flask ベースのロト7（日本の宝くじ）番号分析および予測システムです。

## 機能

### 1. 過去の抽選結果表示
- JSONファイルから過去のロト7抽選結果を読み込んで表示
- 視覚的なボール表示と番号分布バーで見やすく表示
- 本数字とボーナス数字を色分けして表示

### 2. 番号予測機能
- 統計的フィルターを使用した次回当選番号の予測
- 以下のフィルター条件を適用：
  - 連続番号の有無
  - ゾーン分布（3ゾーン、4ゾーン）
  - 奇数・偶数のバランス
  - 番号の合計値範囲
  - 下一桁の分布
  - 前回抽選との重複チェック

### 3. データ管理
- JSONファイルのアップロード機能
- データの検証と読み込み

## プロジェクト構成

```
loto7/
├── server.py              # アプリケーションエントリーポイント
├── config.py              # アプリケーション設定
├── requirements.txt       # Python依存パッケージ
├── app/                   # メインアプリケーションパッケージ
│   ├── __init__.py       # Flaskアプリケーションファクトリ
│   ├── models.py         # データモデル（Loto7Draw）
│   ├── api/              # APIエンドポイント
│   │   └── __init__.py   # API Blueprint
│   ├── main/             # メインルート
│   │   └── __init__.py   # メインページBlueprint
│   └── services/         # ビジネスロジック
│       ├── __init__.py
│       ├── data_service.py        # データ操作サービス
│       └── prediction_service.py  # 予測ロジックサービス
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

## API エンドポイント

### GET `/api/data`
過去の抽選結果を取得

**レスポンス:**
```json
{
  "success": true,
  "draws": [...],
  "count": 8
}
```

### POST `/api/predict`
番号予測を生成

**リクエスト:**
```json
{
  "count": 10,
  "start_draw_number": 650
}
```

**レスポンス:**
```json
{
  "success": true,
  "draws": [...],
  "count": 10,
  "message": "10件の予測を生成しました。"
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
統計情報を取得

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

## データフォーマット

### loto7_data.json

```json
{
  "draws": [
    {
      "id": "第649回",
      "date": "2024-10-25",
      "main": [12, 22, 23, 26, 33, 35, 37],
      "bonus": [2, 21]
    }
  ]
}
```

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
- テストスイートの追加
