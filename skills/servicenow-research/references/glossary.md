# ServiceNow Glossary — 初心者向け用語補足ガイド

## 目的

回答テンプレートの「結論 / 理由 / 具体例」セクションで ServiceNow 専門用語を使う際、**初出時のみ** インライン括弧で 1〜2 行の平易な日本語補足を入れる。

書き方:
```
... Business Rule(**レコード操作時に自動実行されるサーバサイドスクリプト**) を ...
```

## 必修語彙集 (頻出用語の補足例)

### プラットフォーム基盤

| 用語 | 補足文(コピペ可) |
|------|----------------|
| GlideRecord | **ServiceNow データベースのレコードを操作する標準的なJavaScript API** |
| GlideAjax | **クライアント側からサーバ側スクリプトを呼び出すための非同期通信機構** |
| Business Rule | **レコード操作 (insert/update/delete/query) 時に自動実行されるサーバサイドスクリプト** |
| Script Include | **複数の場所から呼び出せる、再利用可能なサーバサイドJavaScript関数群** |
| Client Script | **フォームの操作 (load/change/submit) 時にブラウザ側で動作するJavaScript** |
| UI Action | **フォームやリストに表示するボタン/メニュー項目の挙動を定義する仕組み** |
| ACL (Access Control List) | **テーブル単位・フィールド単位で読み書き権限を制御するルール** |
| Role | **ユーザに割り当てる権限のセット。複数ロールの組み合わせで細かく制御** |

### Workflow / 自動化

| 用語 | 補足文 |
|------|-------|
| Flow Designer | **ノーコード/ローコードでビジネスワークフローを組むビジュアルエディタ** |
| Workflow Studio | **Australia リリースで強化された統合ワークフロー開発環境** |
| Subflow | **再利用可能なフロー部品。他のフローから呼び出せる** |
| Action | **フロー内で実行する個別ステップ (REST呼び出し、レコード作成、メール送信など)** |
| Trigger | **フローを起動するきっかけ (レコード変更、スケジュール、外部イベントなど)** |

### IT Operations

| 用語 | 補足文 |
|------|-------|
| MID Server | **顧客環境とServiceNowクラウド間に配置するJavaエージェント。Discovery等を中継** |
| Discovery | **ネットワーク上のサーバ・ネットワーク機器を自動検出してCMDBに登録する機能** |
| CMDB (Configuration Management Database) | **IT資産・サービスの構成情報を一元管理するデータベース** |
| Event Management | **監視ツールからのイベントを集約・相関分析しアラート/インシデントを生成する機能** |
| Service Map | **CIs(構成アイテム) 間の依存関係を可視化したマップ** |

### IT Service Management

| 用語 | 補足文 |
|------|-------|
| Incident | **サービス停止や品質低下を記録・追跡するレコード。インシデント管理の中心** |
| Problem | **複数インシデントの根本原因を分析・解決するためのレコード** |
| Change Request | **本番環境への変更を申請・承認・実装するワークフローレコード** |
| Service Request | **ユーザがカタログ経由で申請するセルフサービス要求 (PCの追加発注など)** |
| Service Catalog | **ユーザが自分で利用申請できるサービス/商品のカタログ** |

### AI / Now Assist

| 用語 | 補足文 |
|------|-------|
| Now Assist | **ServiceNow の生成AI機能群。要約、分類、コード生成など** |
| Now Assist for ITSM | **インシデントの要約・解決提案・カテゴライズ等をAIで支援する機能** |
| Now Assist for Code | **GlideScript/JavaScript のコード生成・補完を行うAI機能** |
| Skill (Now Assist) | **特定タスク用のAIテンプレート。プロンプト+モデル+ガードレールがセット** |

### セキュリティ / GRC

| 用語 | 補足文 |
|------|-------|
| GRC (Governance, Risk, Compliance) | **企業ガバナンス・リスク管理・コンプライアンス対応を統合管理するモジュール群** |
| Vulnerability Response | **検出された脆弱性を優先順位付けし対応ワークフローを回す機能** |
| Threat Intelligence | **外部脅威情報を取り込みインシデントと相関させるセキュリティ機能** |

### その他重要

| 用語 | 補足文 |
|------|-------|
| Service Portal | **ユーザ向けのカスタマイズ可能なフロントエンド。AngularJSベース** |
| UI Builder | **新世代のフロントエンド構築ツール (Now Experience UI Framework ベース)** |
| Update Set | **開発成果物 (テーブル変更、スクリプト等) をパッケージ化してインスタンス間で移送する仕組み** |
| Scoped Application | **独立した名前空間とアクセス制御を持つアプリケーションパッケージ** |
| Application Studio | **Scoped Application を開発する統合IDE** |
| Performance Analytics | **時系列データを使ったKPI/ダッシュボード機能** |

### 一般技術用語 (ServiceNow に限らない用語の補足例)

ServiceNow 用語以外でも、技術名や英略語が出てきたら初出時に補足を入れる。

| 用語 | 補足文 (コピペ可) |
|------|-----------------|
| REST API | **HTTP 経由でデータをやり取りする仕組み** |
| GraphQL | **必要なデータだけを 1 回のリクエストで取得できる API 形式** |
| JSON | **キーと値の組で構造化されたテキスト形式のデータ** |
| OAuth | **パスワードを渡さずに別サービスへログインを許可する認証方式** |
| SPA (Single Page Application) | **ページ遷移なしで JS で画面更新するタイプの Web サイト** |
| SSR (Server-Side Rendering) | **サーバ側で HTML を組み立てて返す方式 (検索エンジンに見つかりやすい)** |
| WebFetch | **Claude が Web ページの中身を取り出すための道具** |
| WebSearch | **Claude が検索エンジンで Web を検索する道具** |
| SubAgent | **Claude が補助タスク用に並列起動する別プロセス** |
| TeamCreate | **複数の SubAgent をチームとして同時起動する仕組み** |
| allowlist | **明示的に許可されたものだけを通すリスト (それ以外は遮断)** |
| frontmatter | **Markdown ファイル先頭の `---` で囲まれたメタ情報部分** |
| staging | **本番反映前にデータを一時的に貯める領域** |
| coalesce | **既存レコードを更新するか新規作成するかを判定する仕組み** |
| YAML | **インデントで階層を表す設定ファイル形式 (例: 設定 / メタ情報)** |
| Markdown | **見出しや箇条書きを記号で書く軽量テキスト形式** |
| HEAD リクエスト | **ファイル本体は取らずに「存在するか」だけを確認する HTTP の方法** |
| HTTP 200 / 404 | **正常応答 / ページが見つからないエラー**|
| SSO (Single Sign-On) | **一度ログインすれば連携サービスにも入れる仕組み** |
| KB (Knowledge Base) | **ナレッジ記事を集めたデータベース** |
| CI (Configuration Item) | **CMDB に登録される構成要素 (サーバ・ソフトウェア等)** |
| ETL | **抽出 (Extract) → 変換 (Transform) → 投入 (Load) のデータ処理の流れ** |
| GA (General Availability) | **一般提供開始 (正式公開)** |

略語が文中に出てきたら、初出時に括弧で正式名 + 平易な説明を添える: 例「ITSM (**IT Service Management = IT サービス管理**) では...」

## 用語補足の判定ルール

- **初心者が読んでつまずく可能性 > 50%** と思える固有名詞 → 補足を入れる
- **括弧内補足は 1〜2行 / 50字以内** を目安。長くなるなら別段落に
- **同じ用語の2回目以降** は補足を繰り返さない
- **一般的なIT用語** (HTTP、JSON、API、JavaScript 等) には補足不要

## リリース固有用語の扱い

リリース名 (Australia, Zurich, Yokohama, Xanadu) や Patch リリース固有の機能名は **「<リリース名> リリースで導入された〜」** の形で前置すると分かりやすい:

```
Workflow Studio (**Australia リリースで導入された統合ワークフロー開発環境**) は ...
```
