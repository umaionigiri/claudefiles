# Source Priority — 公式情報源の優先順位、取得手段、既知の制約

5層の公式ソースを順に当たり、最初にヒットしたものを主出典とする。下位ソースは補助証拠としてのみ採用する。**この一覧に無いソースは絶対に参照しない。**

## 優先順位と取得手段

| 順位 | ソース | URL prefix | 取得手段 | カバー率の現実 |
|------|--------|------------|----------|---------------|
| 1 | **GitHub ServiceNowDocs** | `raw.githubusercontent.com/ServiceNow/ServiceNowDocs/<branch>/...` | `gh search code` + `WebFetch raw URL` | **~99%** — 全製品×全カテゴリ網羅、リリース別ブランチ、frontmatter構造化済 |
| 2 | **Developer Portal** | `developer.servicenow.com` | `WebSearch(allowed_domains=...)` → `WebFetch` | **<10%** — SPA本体は不可。`to.do` / `blog.do` / `_escaped_fragment_` 形式のみSSR取得可能 |
| 3 | **Product Docs** | `docs.servicenow.com` | `WebSearch(allowed_domains=...)` → `WebFetch` | **<5%** — ほぼ全URLがSPA。Googleキャッシュ経由で偶然取れる程度 |
| 4 | **Community** | `community.servicenow.com` | `WebSearch(allowed_domains=...)` → `WebFetch` | **~30%** — Q&A (`?id=community_question&sys_id=...`) はSSR、本文取得可能 |
| 5 | **Now Support (KB)** | `support.servicenow.com` | `WebSearch` (試行のみ) | **~0%** — 認証壁。本文取得は実質不可 |

**現実的な期待値**: 質問の **9割以上は GitHub だけで答えが出る**。残り1割の補助に他の4ソースが乗る。「わかりません」が返るのは、Apache 2.0 ライセンスで GitHub から消された機能 / Early-Access 段階で未公開の機能 / 個人の運用Tipsのみが対象のときなどに限られる。

## 各ソースの取得方式 詳細

### 1. GitHub ServiceNowDocs (主検索)

```python
# Discover paths via gh CLI
hits = gh_search.search("Now Assist for ITSM")  # repo qualifier auto-added
# Fetch each path's body
for hit in hits:
    doc = raw_fetch.fetch(hit.path, branch="australia")
    # doc.title / doc.doc_type / doc.body 利用可能
```

**強み**: 構造化Markdown、frontmatterで `doc_type` フィルタ可、リリース別ブランチで時系列確認可。

### 2. Developer Portal (best-effort)

```python
# Researcher の中で:
WebSearch(query="GlideRecord addQuery", allowed_domains=["developer.servicenow.com"])
# → ヒットURL一覧
# 各 URL を WebFetch、ただし `#!/` を含む SPA URL は本文空なのでスキップ
# `to.do?u=...` / `blog.do?p=...` / `_escaped_fragment_=...` 形式のみ採用
```

**得意分野**: 公式ブログ記事、API リファレンスのチュートリアル、Learn コース、Now Creator 教材。
**苦手分野**: API クラスの詳細リファレンス (SPAのみ)。

### 3. Product Docs (best-effort)

```python
WebSearch(query="...", allowed_domains=["docs.servicenow.com"])
# 多くの URL は SPA、WebFetch で 8KB shell が返る → 採用しない
# 偶然 Google キャッシュ越しに取れた場合のみ採用
```

**得意分野**: ほとんど無い (GitHubの方がカバー率が高く、SPA壁もない)。
**苦手分野**: ほぼすべて。
**戦略**: docs.servicenow.com のヒットがあれば確認するが、空帰りが標準。

### 4. Community (best-effort)

```python
WebSearch(query="widget not loading", allowed_domains=["community.servicenow.com"])
# Q&A URL (`?id=community_question&sys_id=...`) は SSR
# WebFetch で本文取得可能
```

**得意分野**: 実務トラブルシューティング、エラーコード対処、運用Tips。
**苦手分野**: 公式仕様の確認 (回答の品質にばらつき)。回答品質を見極めるため、ベストアンサー (Solved マーク) を優先採用。

### 5. Now Support (実質無効)

```python
WebSearch(query="...", allowed_domains=["support.servicenow.com"])
# 一部の KB 抜粋が Google index されているケースもある
# WebFetch で SSO ログイン画面が返ったら採用しない
```

**得意分野**: 既知のバグ修正情報、リリースパッチ詳細。
**苦手分野**: 認証壁により大半取得不可。

## 各ソースの得意分野早見表 (参照優先順)

| 質問タイプ | 第一に当たるべきソース | 補助 |
|------------|---------------------|------|
| 機能の概要・コンセプト | GitHub (concept) | developer (blog) |
| API/メソッドの使い方 | GitHub (api-reference カテゴリ) | developer (`to.do` / `blog.do`) |
| 設定手順 / Step-by-step | GitHub (task) | community (Q&A) |
| リリース別差分 | GitHub (ブランチ切り替え) | (補助なし) |
| エラーコード対処 | community (Q&A) | GitHub のトラブル系ドキュメント |
| ベストプラクティス / 設計パターン | GitHub | developer (blog) / community |
| 日本語UI上の機能名 | GitHub (titleで照合) | (他ソースは英語メイン) |

## allowlist の運用

- `scripts/source_allowlist.py` の `ALLOWED_HOSTS` がコードレベルの強制リスト
- `Source(...)` 生成時に自動チェック → 違反は ValueError
- `WebSearch` は **必ず `allowed_domains` を渡す** こと (researcher.md のハードルール)
- LLM が判断で他ソースを混ぜようとしてもブロックされる

## 「公式以外の情報源で答えそうになった」場合の挙動

- `Source(...)` が ValueError → 当該ソースは破棄
- 全5ソースで何も見つからない場合は `format_response.render_unknown()` で「わかりません」を返す
- 個人ブログ・Qiita・Stack Overflow・Reddit・YouTube は **絶対に出典に含めない** (`allowed_domains` 経由でも来ないが、防御的に allowlist で再チェック)

## 取得失敗時のフォールバック順 (実装)

1. GitHub raw URL が 404 → `gh search code` で再検索 → ヒットなしなら次のソースへ
2. Developer Portal の WebSearch が空 → docs.servicenow.com へ
3. docs.servicenow.com も空 → community へ
4. community も空 → support 試行 (大半空)
5. **5ソース全空** → `render_unknown()` で正直回答

## 想定される「わかりません」率

- 一般的な ServiceNow 質問: **<5%** (GitHub で大半カバー)
- 個人運用ノウハウ系: **30〜50%** (community で補えれば残せる)
- 削除済みリリース固有 (Vancouver 以前): **~100%** (リポジトリから削除されているため不可)
- 架空の機能 / 誤読: **100%** ← これが「わかりません」を返す本来の役目
