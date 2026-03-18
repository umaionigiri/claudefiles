# Accenture Enterprise 管理設定 制約レポート

> remote-settings.json バージョン17（2026年3月9日施行）に基づく分析

## 概要

Accenture が `remote-settings.json` で企業レベルの管理設定を配信している。
managed settings はローカルの `settings.json` より**常に優先**されるため、ユーザー側で上書きできない制約が多数存在する。

---

## 1. パーミッションモードの制約

| 設定項目 | ローカル (settings.json) | managed (remote-settings.json) | 実際の動作 |
|----------|--------------------------|-------------------------------|------------|
| `defaultMode` | `dontAsk` | `default` | **managed 優先: 確認ダイアログが出る** |
| `disableBypassPermissionsMode` | — | `"disable"` | **bypass モード完全無効** |
| `skipDangerousModePermissionPrompt` | `true` | (上記で無効化) | **機能しない** |

**影響**: ユーザーが `dontAsk` や `bypassPermissions` を設定しても、実際には `default` モード（都度確認）が強制される。

---

## 2. Hook の制約

```json
"allowManagedHooksOnly": true
```

**ユーザー定義の hooks は全て無効化される。** managed settings から配信された hooks のみ実行可能。

### 無効化されるローカル hooks

| Hook | 内容 | 状態 |
|------|------|------|
| PreToolUse (Bash) | `rm -rf` / fork bomb ブロック | **無効** |
| PreToolUse (Bash) | `git push --force` ブロック | **無効** |
| PostToolUse (Write\|Edit) | Prettier 自動フォーマット | **無効** |
| PostToolUse (Write\|Edit) | auto-sync.sh (git自動push) | **無効** |
| SessionStart | git fetch + ブランチ状態表示 | **無効** |
| Stop | タスク完了通知 | **無効** |
| Notification | 通知メッセージ表示 | **無効** |

---

## 3. Deny リスト（絶対禁止 — ユーザー上書き不可）

### 認証情報・秘密鍵の読み取り禁止

| パターン | 対象 |
|----------|------|
| `Read(~/.aws/**)` | AWS認証情報 |
| `Read(%USERPROFILE%\.aws\**)` | AWS認証情報 (Windows) |
| `Read(~/.ssh/id_*)` | SSH秘密鍵全般 |
| `Read(~/.ssh/id_rsa)` | RSA鍵 |
| `Read(~/.ssh/id_ed25519)` | Ed25519鍵 |
| `Read(~/.ssh/id_ecdsa)` | ECDSA鍵 |
| `Read(~/.ssh/id_dsa)` | DSA鍵 |
| `Read(~/.kube/config)` | Kubernetes設定 |
| `Read(%APPDATA%\**\credentials*)` | Windowsアプリ認証情報 |
| `Read(**/privatekey*)` | 秘密鍵ファイル |
| `Read(**/*.pem)` | PEM証明書 |
| `Read(**/*.key)` | 鍵ファイル |
| `Read(**/*.p12)` | PKCS#12 |
| `Read(**/*.pfx)` | PFX証明書 |
| `Read(**/*.keystore)` | キーストア |
| `Read(~/.npmrc)` | npm設定 |
| `Read(~/.pypirc)` | PyPI設定 |
| `Read(~/.pip/pip.conf)` | pip設定 |
| `Read(~/.cargo/credentials)` | Cargo認証 |
| `Read(~/.dockercfg)` | Docker設定 |
| `Read(~/.docker/config.json)` | Docker設定 |
| `Read(**/.git/credentials)` | Git認証情報 |

### ブラウザプロファイルの読み取り禁止

| パターン | 対象 |
|----------|------|
| `Read(**/AppData/**/Google/Chrome/**)` | Chrome (Windows) |
| `Read(**/AppData/**/Mozilla/Firefox/**)` | Firefox (Windows) |
| `Read(**/AppData/**/Microsoft/Edge/**)` | Edge (Windows) |
| `Read(**/Library/Application Support/Google/Chrome/**)` | Chrome (macOS) |
| `Read(**/Library/Application Support/Firefox/**)` | Firefox (macOS) |
| `Read(**/Library/Application Support/Microsoft/Edge/**)` | Edge (macOS) |
| `Read(**/.mozilla/**)` | Firefox (Linux) |
| `Read(**/.config/google-chrome/**)` | Chrome (Linux) |
| `Read(**/.config/chromium/**)` | Chromium (Linux) |
| `Read(~/Library/Keychains/**)` | macOS Keychain |
| `Read(/System/Library/**/*.plist)` | macOS System plist |
| `Read(/Library/Keychains/**)` | macOS System Keychain |

### クラウドメタデータエンドポイントへの WebFetch 禁止

| パターン | 対象 |
|----------|------|
| `WebFetch(domain:169.254.169.254/**)` | AWS/Azure IMDS |
| `WebFetch(domain:169.254.170.2/**)` | AWS ECS メタデータ |
| `WebFetch(domain:[fd00:ec2::254]/**)` | AWS IMDSv2 IPv6 |
| `WebFetch(domain:metadata.google.internal/**)` | GCP メタデータ |
| `WebFetch(domain:metadata/**)` | メタデータ全般 |
| `WebFetch(domain:100.100.100.200/**)` | Alibaba Cloud |
| `WebFetch(domain:*.internal)` | 内部ドメイン |
| `WebFetch(domain:*.local)` | ローカルドメイン |
| `WebFetch(domain:*.corp)` | 企業内ドメイン |
| `WebFetch(domain:*.lan)` | LAN ドメイン |
| `WebFetch(domain:10.*)` | RFC1918 Class A |
| `WebFetch(domain:172.16.*)` 〜 `172.31.*` | RFC1918 Class B (16件) |
| `WebFetch(domain:192.168.*)` | RFC1918 Class C |
| `WebFetch(domain:169.254.*)` | リンクローカル |

### システムファイルの書き込み禁止

| パターン | 対象 |
|----------|------|
| `Write(**/authorized_keys)` | SSH authorized_keys |
| `Write(**/sudoers*)` | sudoers |
| `Write(**/shadow)` | パスワードハッシュ |
| `Write(**/passwd)` | ユーザーアカウント |
| `Write(**/group)` | グループ |
| `Write(**/hosts)` | hosts ファイル |
| `Write(**/hostname)` | ホスト名 |
| `Write(**/resolv.conf)` | DNS設定 |
| `Write(**/crontab)` | crontab |
| `Write(/etc/cron.d/**)` 等 | cron ディレクトリ (5件) |
| `Write(**/.bashrc)` | Bash設定 |
| `Write(**/.zshrc)` | Zsh設定 |
| `Write(**/.profile)` | プロファイル |
| `Write(**/.bash_profile)` | Bash プロファイル |
| `Write(**/.zprofile)` | Zsh プロファイル |
| `Write(**/.bash_login)` | Bash ログイン |
| `Write(**/known_hosts)` | SSH known_hosts |
| `Write(**/ssh_config)` | SSH設定 |
| `Write(/etc/ssh/**)` | システムSSH設定 |

---

## 4. Ask リスト（確認必須 — ローカル allow で上書き不可）

ユーザーが `settings.json` の allow リストに追加しても、managed の ask が優先される。

### 機密ファイルの読み取り

```
Read(**/.env*)          Read(**/secrets/**)
Read(**/*secret*)       Read(**/*password*)
Read(**/*token*)        Read(**/.git/config)
```

### Git 操作

```
Bash(git push:*)        Bash(git remote add:*)
Bash(git clone:*)       Bash(git pull:*)
Bash(git merge:*)       Bash(git rebase:*)
```

### クラウド・インフラ CLI

```
Bash(docker:*)          Bash(kubectl:*)
Bash(aws:*)             Bash(az:*)
Bash(gcloud:*)          Bash(terraform apply:*)
Bash(terraform destroy:*)
```

### パッケージインストール

```
Bash(npm install:*)     Bash(npm i:*)       Bash(npm publish:*)
Bash(pip install:*)     Bash(pip3 install:*) Bash(pipenv install:*)
Bash(poetry add:*)      Bash(go get:*)      Bash(go install:*)
Bash(yarn add:*)        Bash(yarn install:*) Bash(pnpm add:*)
Bash(bundle install:*)  Bash(cargo install:*) Bash(composer require:*)
Bash(composer install:*) Bash(mvn install:*) Bash(gradle install:*)
Bash(apt install:*)     Bash(apt-get install:*) Bash(yum install:*)
Bash(brew install:*)    Bash(choco install:*) Bash(gem install:*)
```

### ネットワーク・ダウンロード

```
Bash(curl:*)            Bash(wget:*)
```

### ビルド

```
Bash(cargo build:*)     Bash(make:*)        Bash(cmake:*)
```

### Dockerfile / CI/CD / スクリプト

```
Write(**/Dockerfile)    Edit(**/Dockerfile)
Write(**/.github/workflows/*)  Edit(**/.github/workflows/*)
Write(**/*.sh)          Edit(**/*.sh)
Write(**/*.bash)        Edit(**/*.bash)
Write(**/*.ps1)         Edit(**/*.ps1)
```

### ロックファイル・git 内部

```
Edit(**/package-lock.json)  Edit(**/yarn.lock)
Edit(**/pnpm-lock.yaml)    Edit(**/Gemfile.lock)
Edit(**/poetry.lock)        Edit(**/Pipfile.lock)
Edit(**/composer.lock)      Edit(**/Cargo.lock)
Edit(**/go.sum)             Edit(**/.git/**)
```

---

## 5. Allow リスト（managed 側で確認不要と許可済み）

### 読み取り・探索系

```
ls, cat, less, more, head, tail, grep, find,
pwd, which, whereis, file, stat, wc, echo
```

### Git 読み取り系

```
git status, git log, git diff, git show, git branch, git tag
```

### テスト実行

```
npm test, npm run test*, npm run lint*,
pytest, python -m pytest, go test, cargo test,
mvn test, gradle test, jest, mocha, rspec
```

### ビルド・フォーマット

```
npm run build*, tsc, webpack, vite build, rollup,
prettier, eslint, pylint, black, rustfmt, gofmt
```

---

## 6. MCP サーバー制限

`"enableAllProjectMcpServers": false` — プロジェクトの MCP サーバーは自動有効化されない。

### 許可済みサーバー (17件)

| サーバー名 | 用途 |
|------------|------|
| filesystem | ファイルシステム操作 |
| shell | シェル実行 |
| chrome-devtools-mcp | Chrome DevTools |
| asana | タスク管理 |
| context7 | ライブラリドキュメント |
| firebase | Firebase |
| github | GitHub操作 |
| gitlab | GitLab操作 |
| greptile | コード検索 |
| laravel-boost | Laravel開発 |
| linear | Linear プロジェクト管理 |
| playwright | ブラウザ自動化 |
| serena | コード解析 |
| slack | Slack連携 |
| stripe | Stripe決済 |
| supabase | Supabase |
| microsoft-learn | Microsoft ドキュメント |

### 許可リストに含まれないが使用中のサーバー

- `mcp__azure__*` — Azure MCP（allowlist 外）
- `mcp__o3__*` — O3 Chat（allowlist 外）

---

## 7. Marketplace 制限

`strictKnownMarketplaces` により、以下のリポジトリからのみスキル・プラグインをインストール可能:

| リポジトリ | 用途 |
|------------|------|
| `accenture-rde-labs/skills` | Accenture公式スキル |
| `accenture-rde-labs/plugins` | Accenture公式プラグイン |
| `accenture-rde-labs/tools` | Accenture公式ツール |
| `anthropics/skills` | Anthropic公式スキル |
| `anthropics/claude-plugins-official` | Anthropic公式プラグイン |
| `accenture-cio/2731_ClaudePlugins` | Accenture CIO部門プラグイン |
| `accenture-cio/2731_ClaudeSkills` | Accenture CIO部門スキル |
| `microsoftdocs/mcp` | Microsoft ドキュメント MCP |

---

## 8. その他の制約

| 設定 | 値 | 影響 |
|------|-----|------|
| `allow_remote_control` | `false` (policy-limits.json) | CI/CD等からの外部制御を禁止 |
| `enableAllProjectMcpServers` | `false` | プロジェクトMCPの自動有効化禁止 |
| `allowManagedHooksOnly` | `true` | ユーザーhooks無効化 |

---

## 9. ユーザーが自由に制御できる設定

| 設定 | 現在の値 | 備考 |
|------|----------|------|
| `model` | `opus[1m]` | モデル選択は自由 |
| `language` | `japanese` | 応答言語 |
| `includeCoAuthoredBy` | `false` | コミットの共著者表記 |
| `env` | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70` 等 | 環境変数 |
| MCP サーバー設定 | (許可リスト内のサーバーのみ) | 接続設定は自由 |
| allow リスト追加 | deny/ask と競合しない範囲のみ有効 | 限定的 |

---

## 10. 結論と対策

### managed settings で変更不可能なもの

- `defaultMode` は `default`（確認ダイアログ）が強制
- `bypassPermissions` モードは使用不可
- ユーザー定義 hooks は全て無効
- ask リストの操作は常に確認が必要

### 実用的な対策

1. **allow リスト**: deny/ask と競合しない操作（MCP ツール呼び出し、独自スクリプト等）は allow に追加可能
2. **hooks の代替**: `allowManagedHooksOnly` により hooks は使えないため、外部スクリプトやタスクランナーで代替する
3. **auto-sync**: hooks 経由では動かないため、手動 or 外部の cron/タスクスケジューラで実行する
4. **ask 操作**: 頻繁に使うコマンド（`git push`, `npm install` 等）は都度承認が必要だが、managed 設定を変更する権限がない限り回避不可
