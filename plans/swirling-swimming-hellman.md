# 合同会社あいのみ ホームページ開発プラン

## プロジェクト概要
産業ケアマネ事業を営む合同会社あいのみのコーポレートサイト開発

## 技術スタック
- **Framework**: Next.js 15 (App Router) + TypeScript + Turbopack
- **Styling**: Tailwind CSS v4
- **Deployment**: Vercel
- **Package Manager**: pnpm
- **Domain Registrar**: お名前.com / Google Domains / Cloudflare 等

> **Note**: `create-next-app@latest --yes` で TypeScript, Tailwind CSS, ESLint, App Router, Turbopack が自動有効化される

## ページ構成

### 必須ページ
1. **トップページ** (`/`)
   - ヒーローセクション
   - サービス概要
   - 特徴・強み
   - CTAセクション

2. **会社概要** (`/about`)
   - 会社名、所在地、代表者
   - 設立年月日
   - 事業内容
   - 経営理念

3. **サービス紹介** (`/services`)
   - 産業ケアマネとは
   - 企業向け両立支援サービス
   - 料金プラン（任意）

4. **重要事項説明** (`/legal/important-matters`)
   - 運営規程の概要
   - 事業の目的・運営方針
   - 従業者の職種・員数・職務内容
   - 営業日・営業時間
   - サービス内容・利用料
   - 通常の事業実施地域
   - 緊急時対応方法
   - 苦情処理体制
   - 虐待防止措置
   - 事故発生時対応

5. **お問い合わせ** (`/contact`)
   - お問い合わせフォーム

6. **プライバシーポリシー** (`/privacy`)

### 任意ページ
- お知らせ (`/news`)
- 採用情報 (`/careers`)

## ディレクトリ構造

```
care-inomi/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── about/
│   │   ├── services/
│   │   ├── legal/
│   │   │   └── important-matters/
│   │   ├── contact/
│   │   └── privacy/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── Footer.tsx
│   │   └── ui/
│   └── lib/
├── public/
│   └── images/
├── tailwind.config.ts
├── next.config.js
├── tsconfig.json
└── package.json
```

## 実装手順

1. **プロジェクト初期化**
   ```bash
   pnpm create next-app@latest . --yes
   # --yes で以下が自動設定:
   # - TypeScript
   # - Tailwind CSS v4
   # - ESLint
   # - App Router
   # - Turbopack
   ```

2. **共通コンポーネント作成**
   - Header/Footer
   - レイアウトコンポーネント

3. **各ページ実装**
   - トップページ
   - 会社概要
   - サービス紹介
   - 重要事項説明
   - お問い合わせ
   - プライバシーポリシー

4. **お問い合わせフォーム実装**
   - Server Actions または外部サービス連携

5. **SEO対応**
   - メタデータ設定
   - OGP設定

6. **ドメイン取得・DNS設定**
   - ドメイン取得（推奨: `ainomi.co.jp` または `care-ainomi.jp`）
   - Vercelプロジェクト作成・GitHub連携
   - Vercelでカスタムドメイン設定
   - DNS設定（Aレコード / CNAMEをレジストラ側で設定）
   - SSL証明書（Vercel自動発行）

## ドメイン取得手順

### 推奨レジストラ
| サービス | 特徴 |
|----------|------|
| **Cloudflare Registrar** | 原価販売、DNS高速、無料SSL |
| **Google Domains** | シンプルUI、Whois無料 |
| **お名前.com** | 日本語サポート、.jp取得可能 |

### Vercel連携手順
1. Vercelにプロジェクトをデプロイ
2. Settings > Domains でカスタムドメインを追加
3. 表示されるDNSレコード（A / CNAME）をレジストラ側で設定
4. SSL証明書は自動発行（数分〜数時間）

### 必要なDNSレコード例
```
# Apex domain (ainomi.co.jp)
# Vercel Settings > Domains で表示されるIPを使用
A     @     76.76.21.21

# Subdomain (www.ainomi.co.jp)
# プロジェクト固有のCNAME値がVercelで表示される
CNAME www   cname.vercel-dns.com
# または: d1d4fc829fe7bc7c.vercel-dns-017.com (プロジェクト固有)
```

> **TTL推奨値**: 60秒（Vercelデフォルト）〜3600秒

## ドキュメント構成

### README.md（一般向け・GitHub表示用）
- プロジェクト概要
- セットアップ手順
- 開発コマンド一覧
- デプロイ方法
- ライセンス

### CLAUDE.md（AI開発アシスタント向け）

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
pnpm dev          # localhost:3000 (Turbopack)
pnpm build        # Production build
pnpm lint         # ESLint

## Tech Stack
- Next.js 15 (App Router + Turbopack)
- TypeScript
- Tailwind CSS v4

## Architecture
- `src/app/` - App Router pages (file-based routing)
- `src/components/layout/` - Header, Footer
- `src/components/ui/` - Reusable UI components
- `src/lib/` - Utilities

## Domain Knowledge
- 産業ケアマネ = 企業向け仕事と介護の両立支援専門職
- `/legal/important-matters/` は介護保険法に基づく必須掲載ページ（運営規程、苦情処理体制、虐待防止措置等）
- 2024年度改定でWeb掲載が義務化されたため、このページの削除・省略は不可

## Styling
- Tailwind CSS v4 utility-first
- Mobile-first responsive design
- Color scheme defined in `tailwind.config.ts`
```

## 検証項目

### 開発環境
- [ ] `pnpm dev` でローカル起動確認
- [ ] 全ページの表示確認
- [ ] レスポンシブデザイン確認（モバイル/タブレット/PC）
- [ ] お問い合わせフォーム送信テスト

### 本番環境
- [ ] Vercelデプロイ成功
- [ ] カスタムドメインでアクセス可能
- [ ] HTTPS（SSL）有効
- [ ] OGP画像表示確認（SNSシェア時）
- [ ] Google Search Console登録
