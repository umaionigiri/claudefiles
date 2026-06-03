# ServiceNowDocs カテゴリ → パスマッピング

ServiceNowDocs リポジトリの `markdown/` 配下は **51カテゴリ** に分かれている。各カテゴリ名はディレクトリ名そのもの (空白あり)。`raw.githubusercontent.com` で取得する際は URL エンコードが必要。

## 主要カテゴリ (ファイル数順 上位15)

| # | カテゴリ | ファイル数 | パス例 |
|---|----------|----------|--------|
| 1 | Employee Service Management | 4,911 | `markdown/Employee Service Management/...` |
| 2 | ServiceNow Platform | 3,010 | `markdown/ServiceNow Platform/...` |
| 3 | IT Operations Management | 2,756 | `markdown/IT Operations Management/...` |
| 4 | Security Management | 2,711 | `markdown/Security Management/...` |
| 5 | IT Service Management | 2,631 | `markdown/IT Service Management/...` |
| 6 | Governance, Risk, Compliance | 2,230 | `markdown/Governance, Risk, Compliance/...` |
| 7 | Strategic Portfolio Management | 2,123 | `markdown/Strategic Portfolio Management/...` |
| 8 | Platform Administration | 2,120 | `markdown/Platform Administration/...` |
| 9 | Workflow Data Fabric | 2,103 | `markdown/Workflow Data Fabric/...` |
| 10 | Customer Service Management | 2,009 | `markdown/Customer Service Management/...` |
| 11 | IT Asset Management | ~1,800 | `markdown/IT Asset Management/...` |
| 12 | Field Service Management | ~1,500 | `markdown/Field Service Management/...` |
| 13 | Now Assist | ~1,200 | `markdown/Now Assist/...` (もしくは各機能側に分散) |
| 14 | Cloud Observability | ~1,000 | `markdown/Cloud Observability/...` |
| 15 | API Reference | ~900 | `markdown/API Reference/...` |

(残り36カテゴリは Healthcare / Financial Services / PSDS / Retail / Manufacturing / Mobile / Sales Order Management / Glossary など)

## 質問キーワード → カテゴリ推測

| キーワード | 候補カテゴリ |
|------------|-------------|
| インシデント / incident / リクエスト管理 | IT Service Management |
| Discovery / MID Server / イベント | IT Operations Management |
| CMDB / 構成管理 | ServiceNow Platform / IT Operations Management |
| ハードウェア・ソフトウェア資産 | IT Asset Management |
| ロール / ACL / セキュリティ | Platform Administration / Security Management |
| Now Assist / GenAI / LLM | Now Assist (横断的に各製品にも配置) |
| Workflow Studio / Flow Designer | Workflow Data Fabric / ServiceNow Platform |
| GlideRecord / Business Rule / Script Include | ServiceNow Platform / API Reference |
| Service Portal / UI Builder | ServiceNow Platform |
| HR / 従業員 / 人事 | Employee Service Management |
| 顧客対応 / Case 管理 | Customer Service Management |
| 現場作業 / 派遣 | Field Service Management |
| ライセンス / SAM | IT Asset Management |
| GRC / 監査 / リスク | Governance, Risk, Compliance |
| 投資 / プロジェクト管理 | Strategic Portfolio Management |
| 公共 | Public Sector Digital Services (PSDS) |
| 医療 | Healthcare |
| 金融 | Financial Services |
| モバイル / Now Mobile | Mobile |

## URL 構築の注意点

```python
from scripts.raw_fetch import build_raw_url
url = build_raw_url("markdown/IT Service Management/incident-management.md", "australia")
# urllib.parse.quote が空白を %20 にエスケープする
```

カテゴリ名に含まれる空白・カンマは URL エンコードされる:
- `Governance, Risk, Compliance` → `Governance%2C%20Risk%2C%20Compliance`
- `IT Service Management` → `IT%20Service%20Management`

`scripts/raw_fetch.build_raw_url` がこれを自動で行うので、呼び出し側は生のパスを渡せば良い。

## カテゴリ未知のときの戦略

質問のキーワードからカテゴリを特定できない場合:
1. `scripts/github_search.search(query)` で検索 → ヒットしたパスからカテゴリを逆引き
2. それでも当たらないなら Developer Portal にフォールバック (上位概念で索引化されているケースが多い)
