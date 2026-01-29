# Vercelログからチャットセッション抽出計画

## 目的
`logs_result.json`からチャットボットの質問と応答をセッション単位でCSV形式に変換

## データ構造
- **総エントリ数**: 1000件
- **ユニークセッション数**: 62件
- **識別キー**: `requestId`
- **質問**: `message`内の`query: 'xxx'`
- **応答**: `message`内の`preview: 'xxx'`

## 出力形式（CSV）
| カラム | 説明 |
|--------|------|
| session_no | セッション番号 |
| timestamp | リクエスト時刻（UTC） |
| request_id | リクエストID |
| query | ユーザーの質問 |
| response_preview | AIの応答（プレビュー） |
| response_length | 応答文字数 |

## 実装手順

1. **jqでデータ抽出・整形**
   - requestIdでグループ化
   - 各セッションから必要フィールドを抽出
   - CSV形式に変換

2. **出力ファイル**
   - `/Users/so/Downloads/chat_sessions.csv`

## 検証方法
- CSVファイルをExcelで開いて確認
- 62セッション分のデータが含まれていることを確認
