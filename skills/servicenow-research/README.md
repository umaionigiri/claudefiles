# ServiceNow Research

ServiceNow の最新製品仕様・技術情報を **公式ソースのみ** から自動調査する Claude Code スキルです (バージョン 1.0.0)。

質問を自然文で投げるだけで、GitHub の ServiceNowDocs リポジトリと ServiceNow 公式 4 サイトを並列で同時調査し、**結論 → 理由 → 具体例 → 出典** の構造化された日本語回答を返します。

> 📊 **詳細ガイドは同梱の `servicenow-research_guide.pptx` (14 スライド) を参照してください。**
> アーキテクチャ・処理フロー・出力サンプル・トラブルシューティングを視覚的に確認できます。新規メンバーへのオンボーディングや、社内勉強会の資料としてご活用ください。

## 主な特徴

- **公式情報源限定**: 7 つの公式ドメインのみを参照、Qiita / Stack Overflow / 個人ブログ等を構造的に排除
- **5 並列調査**: GitHub をプライマリ (約 99% カバー) + ServiceNow 公式 4 サイト
- **構造化回答**: 結論 / 理由 / 具体例 / 出典 の 4 セクション Markdown 出力
- **URL 生存確認**: 引用 URL を出力前に HTTP HEAD で確認、死リンク排除
- **専門用語の自動補足**: 初出時に括弧で日本語補足を付与
- **「わかりません」回答**: 該当情報がない場合は捏造せず、検索内訳を開示
- **stdlib のみで動作**: 追加の pip パッケージ不要

## 前提環境

- Claude Code (最新版)
- Python 3.10 以上
- GitHub CLI (`gh`) 2.0 以上、scope `repo` を持つ認証済アカウント
- `github.com` と `*.servicenow.com` へのネットワーク接続

## 導入手順

```bash
# 1. zip を展開 (~/.claude/skills/ 直下に展開すること)
unzip servicenow-research-1.0.0.zip -d ~/.claude/skills/

# 2. GitHub CLI を認証 (未認証時のみ)
gh auth login

# 3. Claude Code を再起動 (または /reload-plugins)
```

導入後は、質問文に「ServiceNow」を含めるだけで自動発動します。

## 使い方

ServiceNow に関する自然文質問を Claude Code に投げてください。

```
GlideRecord で addQuery を OR 条件で書くには?
Yokohama で MID Server を構成する手順を教えて
Australia と Zurich で Workflow Studio に追加された機能の差分は?
```

リリース名 (Australia / Zurich / Yokohama / Xanadu) が指定されていない場合は、対話的に確認します。

## 対応リリース

| リリース   | 状態           |
| ---------- | -------------- |
| Australia  | ◎ 最新         |
| Zurich     | ○ 対応中       |
| Yokohama   | ○ 対応中       |
| Xanadu     | △ まもなく削除 |

Vancouver より古いリリース固有の情報は対応対象外です (ServiceNowDocs リポジトリから削除済)。

## 制約事項

- ServiceNow インスタンスの **実機操作** はしません
- 認証必須の **Now Support KB 本文** は取得不可
- **非公式情報源** からの引用なし (Qiita / Stack Overflow / 個人ブログ等は構造的に拒否)

## 連絡先

問題報告・改善要望は配布元の管理者までご連絡ください。
