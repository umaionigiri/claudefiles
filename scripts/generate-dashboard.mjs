#!/usr/bin/env node

// Dashboard generator for Claude Code settings
// Reads config files and generates a single-file HTML dashboard
// Node.js standard APIs only — no external dependencies

import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = join(import.meta.dirname, '..');
const OUTPUT = join(ROOT, 'claudesettings-CLAUDE設定.html');

// --- Helpers ---

function readFile(path) {
  try { return readFileSync(path, 'utf-8'); } catch { return null; }
}

function readJson(path) {
  const raw = readFile(path);
  return raw ? JSON.parse(raw) : null;
}

function esc(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/** Convert simple Markdown content to HTML (tables, lists, bold, code, paragraphs) */
function mdToHtml(md) {
  const lines = md.split('\n');
  let html = '';
  let i = 0;
  let inList = false;

  while (i < lines.length) {
    const line = lines[i];

    // Markdown table
    if (line.match(/^\|.+\|$/)) {
      const tableLines = [];
      while (i < lines.length && lines[i].match(/^\|.+\|$/)) {
        tableLines.push(lines[i]);
        i++;
      }
      if (tableLines.length >= 2) {
        // Close any open list
        if (inList) { html += '</ul>'; inList = false; }
        html += '<table>';
        const headerCells = tableLines[0].split('|').filter(c => c.trim()).map(c => c.trim());
        html += '<tr>' + headerCells.map(c => `<th>${renderInline(esc(c))}</th>`).join('') + '</tr>';
        // Skip separator row (index 1)
        for (let r = 2; r < tableLines.length; r++) {
          const cells = tableLines[r].split('|').filter(c => c.trim()).map(c => c.trim());
          html += '<tr>' + cells.map(c => `<td>${renderInline(esc(c))}</td>`).join('') + '</tr>';
        }
        html += '</table>';
      }
      continue;
    }

    // List items
    if (line.match(/^[-*]\s+/)) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += `<li>${renderInline(esc(line.replace(/^[-*]\s+/, '')))}</li>`;
      i++;
      continue;
    }
    if (line.match(/^\d+\.\s+/)) {
      if (!inList) { html += '<ol>'; inList = true; }
      html += `<li>${renderInline(esc(line.replace(/^\d+\.\s+/, '')))}</li>`;
      i++;
      continue;
    }

    // End list if non-list line
    if (inList && line.trim() !== '') {
      html += inList === true ? '</ul>' : '</ol>';
      inList = false;
    }

    // Empty line
    if (line.trim() === '') { i++; continue; }

    // Regular paragraph
    html += `<p>${renderInline(esc(line))}</p>`;
    i++;
  }

  if (inList) html += '</ul>';
  return html;
}

/** Render inline Markdown: **bold**, `code`, [link](url) */
function renderInline(str) {
  return str
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>');
}

/** Convert Japanese body text to HTML with proper lists and paragraphs */
function jaBodyToHtml(text) {
  const lines = text.split('\n');
  let html = '';
  let inUl = false;
  let inOl = false;

  for (const line of lines) {
    const trimmed = line.trim();

    // Bullet list item (• or ・)
    if (trimmed.match(/^[•・]\s*/)) {
      if (inOl) { html += '</ol>'; inOl = false; }
      if (!inUl) { html += '<ul>'; inUl = true; }
      html += `<li>${esc(trimmed.replace(/^[•・]\s*/, ''))}</li>`;
      continue;
    }

    // Ordered list item (1. 2. etc)
    if (trimmed.match(/^\d+\.\s+/)) {
      if (inUl) { html += '</ul>'; inUl = false; }
      if (!inOl) { html += '<ol>'; inOl = true; }
      html += `<li>${esc(trimmed.replace(/^\d+\.\s+/, ''))}</li>`;
      continue;
    }

    // Close open lists
    if (inUl) { html += '</ul>'; inUl = false; }
    if (inOl) { html += '</ol>'; inOl = false; }

    // Empty line = paragraph break
    if (trimmed === '') {
      continue;
    }

    // Heading-like line with 【】
    if (trimmed.match(/^【.+?】/)) {
      html += `<p><strong>${esc(trimmed.match(/^【.+?】/)[0])}</strong>${esc(trimmed.replace(/^【.+?】/, ''))}</p>`;
      continue;
    }

    // Regular paragraph
    html += `<p>${esc(trimmed)}</p>`;
  }

  if (inUl) html += '</ul>';
  if (inOl) html += '</ol>';
  return html;
}

function extractFrontmatter(md) {
  const match = md.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!match) return { meta: {}, body: md };
  const meta = {};
  let currentKey = null;
  for (const line of match[1].split('\n')) {
    const kv = line.match(/^(\w[\w-]*):\s*(.*)$/);
    if (kv) {
      currentKey = kv[1];
      meta[currentKey] = kv[2].replace(/^\|$/, '').trim();
    } else if (currentKey && line.match(/^\s/)) {
      meta[currentKey] = ((meta[currentKey] || '') + '\n' + line.trim()).trim();
    }
  }
  return { meta, body: match[2] };
}

function extractSections(md) {
  const sections = [];
  let current = null;
  for (const line of md.split('\n')) {
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      if (current) sections.push(current);
      current = { level: heading[1].length, title: heading[2], content: '' };
    } else if (current) {
      current.content += line + '\n';
    }
  }
  if (current) sections.push(current);
  return sections;
}

// --- Data Collection ---

function getDirectoryTree(dir, prefix = '', depth = 0) {
  if (depth > 3) return '';
  let result = '';
  const ignoreList = ['.git', '.playwright-mcp', 'node_modules', 'projects', 'debug', 'sessions',
    'file-history', 'session-env', 'shell-snapshots', 'downloads', 'telemetry', 'paste-cache',
    'backups', 'ide', 'todos', 'tasks', 'plans', 'data', 'statsig', 'cache'];
  try {
    const entries = readdirSync(dir, { withFileTypes: true })
      .filter(e => !ignoreList.includes(e.name) && !e.name.startsWith('.DS_Store'))
      .sort((a, b) => {
        if (a.isDirectory() && !b.isDirectory()) return -1;
        if (!a.isDirectory() && b.isDirectory()) return 1;
        return a.name.localeCompare(b.name);
      });
    entries.forEach((entry, i) => {
      const isLast = i === entries.length - 1;
      const connector = isLast ? '└── ' : '├── ';
      const childPrefix = isLast ? '    ' : '│   ';
      if (entry.isDirectory()) {
        result += `${prefix}${connector}${entry.name}/\n`;
        result += getDirectoryTree(join(dir, entry.name), prefix + childPrefix, depth + 1);
      } else {
        result += `${prefix}${connector}${entry.name}\n`;
      }
    });
  } catch { /* skip */ }
  return result;
}

// Agent full Japanese descriptions
const agentFullJa = {
  'code-reviewer': {
    summary: 'コードレビューエージェント',
    body: `コード変更を体系的にレビューし、品質を確保する。

【レビュー手順】
1. git diff で変更内容を確認
2. 各ファイルを詳細レビュー
3. 指摘事項をリスト化
4. 重大度でソート

【レビューチェックリスト】

【セキュリティ】
• SQLインジェクション対策
• XSS対策
• 認証・認可の適切な実装
• ハードコードされた秘密情報がないか
• 入力バリデーション

【パフォーマンス】
• N+1クエリ
• 不要なループ・再計算
• メモリリーク
• インデックスの適切な使用

【コード品質】
• 命名規則の遵守
• 関数の単一責務
• DRY原則
• エラーハンドリング

【テスト】
• テストカバレッジ
• エッジケーステスト
• モックの適切な使用

【重大度レベル】
• 🔴 Critical — セキュリティ脆弱性、データ破損リスク
• 🟠 Major — バグ、パフォーマンス問題
• 🟡 Minor — コード品質、可読性
• 🔵 Suggestion — ベストプラクティス推奨

【出力フォーマット】
Code Review: [PR/変更サマリ] → サマリ（変更ファイル数、追加/削除行数）→ 指摘事項（重大度別）→ 判定（Approve / Request changes / Comment only）`
  },
  'devops-problem-solver': {
    summary: 'DevOps 問題解決エージェント',
    body: `システム障害・DevOps問題を体系的に診断・解決する。

【6フェーズ問題解決】
1. 情報収集 — エラーメッセージ、発生時刻・頻度、影響範囲、直近の変更履歴
2. 症状分析 — エラーパターン特定、正常状態との差分、影響コンポーネント
3. 仮説立案 — 原因候補のリスト化、可能性順にランク付け
4. 検証 — 仮説を一つずつテスト、結果を記録
5. 解決 — 修正実施、ロールバック計画の準備、変更を記録
6. 振り返り — 根本原因の文書化、再発防止策

【よくある問題と確認ポイント】

【アプリケーションエラー】
• 500エラー — 確認: tail -f error.log — 原因: 例外、設定ミス
• タイムアウト — 確認: curl -w "%{time_total}" — 原因: DB遅延、外部API
• メモリ不足 — 確認: free -m, top — 原因: メモリリーク

【データベース問題】
• 接続エラー — 確認: pg_isready — 対応: コネクション数確認
• スロークエリ — 確認: EXPLAIN ANALYZE — 対応: インデックス追加
• ロック待ち — 確認: pg_stat_activity — 対応: トランザクション確認

【CI/CDパイプライン】
• ビルド失敗 — 確認: 依存関係、環境変数
• テスト失敗 — 確認: テスト環境、Flakyテスト
• デプロイ失敗 — 確認: 権限、リソース制限

【出力フォーマット】
インシデントレポート: サマリ（発生日時・影響・重大度）→ 症状 → 根本原因分析（仮説・検証結果）→ 根本原因 → 実施した対応 → 再発防止策 → タイムライン`
  },
  'estimation-agent': {
    summary: '見積りエージェント',
    body: `ソフトウェア開発プロジェクトの見積りを標準化し、社内向け・顧客向け見積書を作成する。

【単価ルール】
• 時間単価: ¥15,000
• 利益率: 1.5倍
• 消費税: 10%
• 計算式: 原価（工数 × ¥15,000）→ 税抜（× 1.5）→ 税込（× 1.1）

【見積りカテゴリ】
1. 要件定義 — ヒアリング、分析、仕様書
2. 設計 — 基本設計、詳細設計、UI/UX
3. インフラ — 基盤設計、環境構築、CI/CD
4. 開発 — 実装、コードレビュー、バグ修正
5. テスト — 単体/結合/E2E/UAT/負荷
6. 移行・リリース — データ移行、デプロイ、切替
7. 運用設計 — 監視、障害対応、保守計画
8. ドキュメント — 技術文書、運用手順書、API仕様
9. 研修 — ユーザー研修、管理者研修
10. PM工数 — 会議、進捗管理、リスク管理（全体の15-20%）

【工数比率ガイドライン】
• 要件定義: 10-15%
• 設計: 15-20%
• 開発: 30-40%
• テスト: 20-25%
• その他: 10-15%

【出力テンプレート】

【社内向け見積り】
見積書（社内）: 案件名、作成日、有効期限（30日）→ 最終金額（税抜・消費税・合計）→ カテゴリ別内訳（カテゴリ・工数・単価・原価・税抜・税込）→ 社内メモ（利益率・総原価・粗利）

【顧客向け見積り】
御見積書: 案件名、作成日、有効期限（30日）→ 金額（小計・消費税・合計）→ 明細（項目・税抜・税込）

【ワークフロー】
1. 要件収集 — プロジェクト概要、機能一覧、制約事項
2. 工数見積り — カテゴリ別に作業を洗い出し、PM工数を加算
3. 費用計算 — 原価 → 税抜 → 税込
4. 文書作成 — 社内向け・顧客向けの2種類を作成
5. レビュー — 漏れの確認、金額の検算`
  },
  'senior-consultant-reviewer': {
    summary: 'シニアコンサルタントレビューエージェント',
    body: `要件・設計・見積り・プロジェクト計画を、シニアコンサルタント/PM視点でレビューする。

【レビュー対象】
1. 要件定義書
2. 設計書
3. 見積書
4. プロジェクト計画

【レビュー観点】

【要件レビュー】
• ビジネス整合 — 事業目標との整合、ROI妥当性
• 完全性 — 機能/非機能要件の網羅性
• 明確性 — 曖昧な表現がないか、定量的基準
• スコープ — 境界の明確化、除外事項の明記
• 実現可能性 — 技術制約、リソース整合
• 優先度 — 優先順位設定（MoSCoW等）

【設計レビュー】
• アーキテクチャ — 要件との整合、拡張性、保守性
• 技術選定 — 技術的妥当性、チームスキルとの適合
• セキュリティ — OWASP Top 10、認証・認可設計
• パフォーマンス — レスポンス要件、スループット要件
• 可用性 — SLA、耐障害性、冗長構成

【見積りレビュー】
• 工数妥当性 — 類似プロジェクトとの比較、業界標準
• 完全性 — 全カテゴリの網羅（PM工数含む）
• リスクバッファ — 不確実性に対するバッファ（10-30%）
• 前提条件 — 前提の明記、リスクの文書化

【プロジェクト計画レビュー】
• マイルストーン — 達成可能性、依存関係管理
• リソース配分 — スキルマッチ、過負荷回避
• リスク管理 — リスク特定、軽減計画
• 品質管理 — テスト計画、受入基準

【重大度レベル】
• 🔴 Critical — プロジェクト失敗リスク → 即時対応必要、却下検討
• 🟠 Major — 深刻な問題に発展する可能性 → 対応後に再レビュー
• 🟡 Minor — 品質向上の提案 → 対応推奨
• 🔵 Info — 参考情報、ベストプラクティス → 任意

【出力テンプレート】
レビュー結果: 対象・日付 → サマリ（総合評価・指摘件数）→ 指摘事項（箇所・問題・リスク・推奨）→ 承認判定（✅承認 / ⚠️条件付き承認 / ❌却下）`
  },
  'task-decomposer': {
    summary: 'タスク分解エージェント',
    body: `複雑なプロジェクトを詳細で実行可能なタスクに分解する。

【分解原則】
1. MECE — 漏れなく、ダブりなく
2. 適切な粒度 — 1タスク = 1〜4時間
3. 依存関係の明確化 — 順序と並列化の可能性
4. 検証可能 — 各タスクに完了基準を設定

【出力フォーマット】
タスク分解: [プロジェクト名] → 概要（1-2文）→ タスク一覧（Phase別）→ 各タスク: タスク名(Xh)・内容・依存・完了基準 → 工数サマリ（Phase別・合計）

【分解プロセス】
1. 要件理解 — 目標と制約の明確化
2. 大分類 — 主要フェーズへの分割
3. 詳細化 — 各フェーズをタスクに分解
4. 依存関係 — 順序と並列化を特定
5. 見積り — 各タスクの工数見積り
6. 完了基準 — 各タスクの検証条件を定義

【タスクサイズ目安】
• XS — ~30分 — 設定変更、ドキュメント更新
• S — 30分〜1時間 — 単一関数、バグ修正
• M — 1〜2時間 — 機能追加、コンポーネント作成
• L — 2〜4時間 — 複数ファイル変更、API実装
• XL — 4時間+ — さらなる分解が必要`
  },
  'test-runner': {
    summary: 'テストランナーエージェント',
    body: `テスト実行・検証・カバレッジ分析の専門エージェント。

【対応範囲】
• ユニットテスト / 結合テスト / E2Eテスト（Playwright）
• カバレッジ分析
• TDDサイクル支援（Red → Green → Refactor）

【実行手順】
1. プロジェクトのテストフレームワークを特定（package.json, pytest.ini 等）
2. 対象スコープに応じたテストコマンドを実行
3. 失敗テストがあれば原因を分析・報告
4. カバレッジレポートを生成（要求時）

【コミット前チェック】
テスト → リント → 型チェック → ビルド
npm test && npm run lint && npm run type-check && npm run build

【プッシュ前チェック】
カバレッジ → E2E → デバッグコード検出
npm test -- --coverage
npm run test:e2e
git diff --staged | grep -E "console\\.(log|debug)"

【TDDコミット規約】
• Red — test: add failing test for <feature>
• Green — feat: implement <feature>
• Refactor — refactor: improve <feature>`
  },
  'workflow-recorder': {
    summary: 'ワークフロー記録エージェント',
    body: `タスク実行時に構造化ワークフロートレースを自動記録する。

【出力ファイル】
• workflow_trace.json — 常時上書き（最新のトレース）
• workflow_trace_<timestamp>.json — タイムスタンプ付きアーカイブ

【記録内容】
• メタデータ — タスク概要、開始/終了時刻、ツール一覧
• ステップ配列 — 各ステップの入力・出力・判断ポイント
• エラー回復 — 失敗時の対応記録
• パターン検出 — 再利用可能なパターンの特定
• 効率ノート — 最適化の余地

【各ステップの判定】
• decision_point — 判断が必要だったか
• generalizable — 他のタスクに一般化可能か
• 理由記載 — なぜその判断をしたか

【完了時レトロスペクティブ】
1. 効率監査 — 冗長なステップ、最適化の余地
2. 決定点監査 — 判断の妥当性、代替案の検討

【ユースケース】
• "record this" — ワークフロー記録を開始
• "trace this" — トレース記録を開始
• "skillify this" — 記録したワークフローをスキル化`
  },
};

// Skill full Japanese descriptions
const skillFullJa = {
  'development-rules': {
    summary: '開発ルール',
    body: `【Step 1: Context7 リサーチ（必須）】

実装前に必ず最新のAPI・パターンを確認する:
• mcp__context7__resolve-library-id({ libraryName: "フレームワーク名" })
• mcp__context7__query-docs({ libraryId: "/lib/xxx", topic: "実装パターン" })

【Step 2: 設計検討】
• 要件の明確化
• 既存コードとの整合性確認（Grep/Glob で既存パターン検索）
• 影響範囲の特定
• 依存関係なしのタスクは Task tool で並列実行

【Step 3: コード品質基準】
• 命名 — 意味のある名前、プロジェクト規約に従う
• エラー処理 — 適切なハンドリング
• コメント — 「なぜ」を説明（「何」ではない）
• マジックナンバー — 定数化
• 補足説明 — 日本語コメント可

【検証チェックリスト】

実装前:
• Context7 でリサーチ済み
• 既存コードのパターンを確認済み
• 影響範囲を特定済み

実装後:
• 各関数/クラスは単一責務か
• 不要な機能を追加していないか
• 重複コードはないか
• 最もシンプルな解か
• テストの有無・カバレッジ
• セキュリティリスクの有無`
  },
  'document-converter': {
    summary: 'ドキュメント変換スキル',
    body: `【サポート形式】
• Markdown → DOCX — pandoc + python-docx
• Markdown → XLSX — Python (openpyxl)
• Markdown → PDF — pandoc + LaTeX
• JSON → XLSX — Python (openpyxl)
• CSV → XLSX — Python (openpyxl)

【標準スタイル】
• 見出し1 — Meiryo UI, 14pt
• 見出し2-4 — Meiryo UI, 12pt
• 本文 — Meiryo UI, 10.5pt
• 表 — Meiryo UI, 10pt
• ヘッダー行 — 背景色 #F0F0F0

【変換手順】

Markdown → DOCX:
pandoc input.md -o output.docx --from markdown+pipe_tables+yaml_metadata_block
python3 scripts/format_docx.py output.docx

Markdown → XLSX:
python3 scripts/md_to_xlsx.py input.md output.xlsx

JSON → XLSX:
python3 scripts/json_to_xlsx.py input.json output.xlsx

Markdown → PDF:
pandoc input.md -o output.pdf --pdf-engine=xelatex -V mainfont="Hiragino Kaku Gothic Pro"

【依存関係】
• pandoc — brew install pandoc
• python-docx — pip install python-docx
• openpyxl — pip install openpyxl
• LaTeX — brew install --cask mactex

【スクリプト】
• scripts/format_docx.py — DOCX フォーマット適用
• scripts/md_to_xlsx.py — Markdown テーブル → Excel
• scripts/json_to_xlsx.py — JSON → Excel

【トラブルシューティング】
• 日本語文字化け — フォント未指定 → Meiryo UI を明示的に指定
• 表が崩れる — pipe_tables 未有効 → +pipe_tables を追加
• PDF で日本語不可 — 日本語フォント未指定 → xelatex + 日本語フォント指定
• Excel セルが空 — パース失敗 → Markdown 形式を確認

【詳細ルール参照】
• DOCX — @docx-rules.md
• XLSX — @xlsx-rules.md

【検証チェックリスト】

変換前:
• 入力ファイルが存在し、形式がサポートされている
• 必要な依存関係がインストール済み

変換後:
• 出力ファイルが生成された（0バイトでない）
• テキスト欠落なし、テーブル正しく変換
• フォント・見出しサイズ・表スタイルが適用済み`
  },
  'gemini-research': {
    summary: 'Gemini リサーチスキル',
    body: `【いつ使うか】
• 既知の基本情報 — 内部知識で回答（Gemini 不要）
• 最新情報が必要 — Gemini でリサーチ
• 比較検討が必要 — Gemini でリサーチ
• ベストプラクティス — Gemini でリサーチ

【リサーチ実行】
mcp__gemini__task({ task: "具体的なリサーチ内容", cwd: "/path/to/project" })

【ユースケース別プロンプト例】
• 技術選定 — Compare X vs Y for [use case]. Consider: performance, learning curve, ecosystem
• 設計パターン — Best practices for [pattern] in [language/framework]. Include code examples
• セキュリティ — Security considerations for [implementation]. Include OWASP guidelines
• パフォーマンス — Performance optimization for [scenario]. Include benchmarks if available
• アーキテクチャ — Architecture patterns for [requirement]. Compare trade-offs

【効果的なプロンプト構成】
• 目的 — 何を知りたいか（Compare..., Best practices for...）
• コンテキスト — 技術スタック（in TypeScript, for React app）
• 制約 — 条件・要件（for high-traffic, with limited budget）
• 観点 — 評価軸（Consider: X, Y, Z）
• 出力形式 — 期待する形式（Include code examples, with pros/cons table）

【検証チェックリスト】

リサーチ前:
• 質問が具体的で、コンテキスト・評価軸が明確

リサーチ後:
• 結果をプロジェクトに適用可能か評価
• 推奨事項が明確
• 追加調査の必要性を判断`
  },
  'git-workflow': {
    summary: 'Git ワークフロー',
    body: `【Step 1: Worktree 作成（必須）】
git worktree add .worktrees/<branch-name> -b <branch-name>
cd .worktrees/<branch-name>

【Step 2: ブランチ命名】
• Feature — feature/<name>（例: feature/user-auth）
• Bugfix — fix/<name>（例: fix/login-error）
• Test — test/<name>（例: test/api-coverage）
• Refactor — refactor/<name>（例: refactor/cleanup）

【Step 3: コミット（Conventional Commits）】
• feat — 新機能
• fix — バグ修正
• refactor — リファクタリング
• test — テスト追加・修正
• docs — ドキュメント
• chore — その他

【Step 4: PR 作成（GitHub MCP 使用）】
mcp__github__create_pull_request({ owner, repo, title, body, head, base: "main" })

【Step 5: マージ後クリーンアップ】
git worktree remove .worktrees/<branch-name>
git branch -d <branch-name>

【禁止事項】
• main/master 直接プッシュ — レビューなしの変更を防ぐ
• git push --force — 履歴破壊を防ぐ
• git reset --hard — 作業内容の消失を防ぐ
例外: ユーザーが明示的に許可した場合のみ

【検証チェックリスト】

コミット前:
• テスト全通過・Lint・型チェック・ビルド成功
• 意図した変更のみステージング
• 機密情報を含まない

PR 作成前:
• ローカルでテスト通過
• CI が通過してからマージ`
  },
  'rough-estimate': {
    summary: '概算見積り作成スキル',
    body: `【サイビット会社情報】
• 会社名: 合同会社サイビット（Scibit LLC）
• 時間単価: ¥15,000/時間（税抜き）
• 日額: ¥120,000（8時間）
• 月額: ¥2,400,000（20日）
• 連絡先: contact@scibit.ai

【単価表示オプション】
• 詳細モード — 工数・単価・金額を表示（社内レビュー、透明性重視の顧客）
• シンプルモード — 工数・金額のみ（一般的な顧客向け）
• 金額のみモード — 金額のみ（エグゼクティブサマリー）
検算: 常に 工数 × ¥15,000 = 金額 で内部検証すること

【見積り作成手順】

Step 1: プロジェクト情報確認
1. 顧客名
2. 案件名
3. 種別: システム開発 / コンサルティング / 保守 / 研修
4. 概要: 何を達成するか
5. 希望時期（あれば）
6. 予算感（あれば）
7. 特記事項: 制約条件等

Step 2: 見積り種別選定
• システム開発 — フェーズ別工数、アーキテクチャ比較
• コンサルティング — 期間・成果物ベース
• 保守 — 月額、SLA定義
• 研修 — 人数・回数ベース

Step 3: ドキュメント構成
必須セクション: ヘッダー情報、概算見積り注意書き、エグゼクティブサマリー、概算費用、含まれるもの/含まれないもの、注意事項・免責事項、お問い合わせ先
任意セクション: 現状分析、ソリューション概要、アーキテクチャ選択肢、導入ロードマップ（Gantt）、ROI分析、リスクと対策、役割分担表、価値提案表、次のステップ

Step 4: 工数・費用算出
フェーズ別工数比率（MVP開発）:
• PM・顧客調整: 10-12%
• 要件定義・設計: 12-16%
• 環境構築: 10-14%
• データ移行: 15-20%
• コア開発: 20-25%
• UI開発: 10-14%
• テスト・調整: 10-12%
• 引き渡し: 5-6%
• バッファ: 4-5%

Step 5: 内部用見積書の同時作成（必須）
ファイル命名規則:
• クライアント向け: {案件名}_概算見積-{見積タイトル}_{YYYYMMDD}.md
• 内部用: {案件名}_（内部）概算見積-{見積タイトル}_{YYYYMMDD}.md

内部用見積書の必須セクション:
1. 社内限定注記（クライアント共有禁止の明示）
2. 単価設定（販売単価・原価単価・利益率）
3. パターン/オプション別の工数内訳（販売金額・原価・粗利）
4. 工数の妥当性分析
5. 既存見積との対応表（該当する場合）
6. 収益分析サマリー

計算ルール:
• 販売金額: 工数 × 販売単価（¥10,000単位に丸め）
• 原価: 工数 × 原価単価（端数そのまま）
• 粗利: 販売金額 - 原価
• 利益率: (販売金額 - 原価) / 販売金額 × 100
• デフォルト販売単価: ¥180,000/人日（= ¥22,500/h、原価の1.5倍）

Step 6: 計算検証（必須）
クライアント向け:
1. 各行の金額が整合している
2. 小計の合算が合計と一致
3. 月額 × 12 = 年額（ランニングコスト）
4. ROI の前提と結果が整合
5. 比較表の各オプションが同一ロジック
6. 単価保護違反がないこと

内部用:
1. 各行: 工数 × 販売単価 ≈ 販売金額（¥10,000丸め許容）
2. 各行: 工数 × 原価単価 = 原価（完全一致）
3. 各行: 販売金額 - 原価 = 粗利
4. クライアント向けと内部用の販売金額が完全一致

Step 7: 免責事項
常に明記: 概算見積りである旨、税抜き表記、有効期限（通常1ヶ月）、含まれるもの/含まれないもの、変動要因

【重要事項】
1. 見積り文書は日本語で出力
2. 概算見積りであることを必ず明記
3. 税抜き表記
4. 有効期限を設定（通常1ヶ月）
5. 含まれないものを明記（インフラ、ライセンス等）
6. 変動要因を説明
7. 概算精度（ROM ±25〜50%）を免責事項に明記
8. 内部用見積書を必ず同時作成（工数・原価・粗利の見積根拠を記録）`
  },
  'acnpptx': {
    summary: 'Accenture PowerPoint 生成スキル',
    body: `Accenture ブランド準拠の PowerPoint プレゼンテーションを自動生成・編集・再スタイルする。

【対応機能】
• 新規デッキ作成 — カバー、アジェンダ、コンテンツスライド
• 既存デッキ編集 — コンテンツ更新、スライド追加/削除
• 再スタイル — テーマ変更、ブランドアセット適用
• リテーマ — カラーパレット変更、フォント変更

【スライドパターン】
• 40+ のコンテンツパターン（A〜AN）
• チャート、アイコングリッド、テーブル、図解
• カバー/アジェンダ/セクション区切り

【ブランドアセット】
• Accenture ロゴ、Greater Than シンボル
• Graphik / Meiryo UI フォント
• 公式カラーパレット・スライドマスター

【技術スタック】
• python-pptx による生成
• ブランドガイドライン準拠チェック
• アウトライン検証機能`
  },
  'claude-assist': {
    summary: 'マルチライン入力GUI スキル',
    body: `複数行入力 GUI を起動して Claude のチャット欄に送信する入力支援ツール。

【機能】
• customtkinter による GUI ウィンドウ起動
• 長文の指示入力に対応
• テンプレート活用
• ファイル参照付き指示の作成

【実行方法】
• uv run で起動
• 初回実行時は依存パッケージのインストールが必要

【ユースケース】
• 複雑な指示を整形して送信
• テンプレートベースのプロンプト作成
• 複数ファイルを参照する指示の組み立て`
  },
  'login-eso': {
    summary: 'Accenture SSO 認証スキル',
    body: `Accenture 社内システム（ESO/SSO）への認証を自動化する基盤ライブラリ。

【認証フロー】
1. Edge のプロファイルを一時コピー
2. Playwright で msedge チャンネルとして起動
3. マネージドデバイス認証を通過
4. 認証済みセッションを返却

【特徴】
• 他スキルから import して使用可能（基盤認証）
• セッションタイムアウト時はブラウザでログイン継続可能
• マネージドデバイス認証対応

【使用スキル】
• reserve-space — 会議室予約時の認証
• その他の社内システム連携スキル`
  },
  'reserve-space': {
    summary: 'Accenture Places スペース予約スキル',
    body: `Accenture Places（support-places.accenture.com/places）の会議室・作業席を自動予約する。

【対応スペース】
• Meeting Room — 会議室
• Open Workspace — 作業席・グループワーク席

【予約フロー】
1. login-eso で SSO 認証
2. Playwright で Places サイトを操作
3. 自然言語の指示をパース（日時、場所、人数等）
4. 条件に合うスペースを検索
5. AI ビジョンスクリーニング（オフィスチェア判定等）
6. 予約実行

【対応条件】
• 複数ビル・フロア対応
• 設備指定（モニター、ホワイトボード等）
• 日時・人数指定`
  },
  'skill-maker': {
    summary: 'スキル自動構築・改善スキル',
    body: `スキルの作成・改善・テスト・ベンチマークを自動化する。

【自動ループ（Phase 0〜5）】
• Phase 0 — 要件収集・分析
• Phase 1 — スキル骨格生成
• Phase 2 — ルール・チェックリスト定義
• Phase 3 — eval テスト作成
• Phase 4 — 実行・評価サイクル
• Phase 5 — 品質チェック・セキュリティレビュー

【機能】
• 新スキルの一貫構築
• 既存スキルの改善
• 参照出力からの勾配ベース整列
• eval サイクル実行・ベンチマーク
• マニュアルモード対応

【ユースケース】
• "build a skill from scratch" — 新規スキル作成
• "improve this skill" — 既存スキル改善
• "run evals" — 評価サイクル実行
• "skillify this" — ワークフローをスキル化`
  },
  'serena-codebase': {
    summary: 'Serena コードベース分析スキル',
    body: `【Step 1: セッション初期化】
mcp__serena__check_onboarding_performed()
mcp__serena__list_memories()
mcp__serena__list_dir({ relative_path: ".", recursive: false })

【Step 2: 概要把握】
mcp__serena__get_symbols_overview({ relative_path: "src" })

【Step 3: シンボル検索（優先）】
mcp__serena__find_symbol({ symbol_name: "ClassName", include_body: false, depth: 1 })

【Step 4: 詳細取得】
mcp__serena__find_symbol({ symbol_name: "ClassName/methodName", include_body: true })

【Step 5: 参照検索】
mcp__serena__find_referencing_symbols({ symbol_name: "targetSymbol" })

【Step 6: シンボル編集（必要時）】
mcp__serena__replace_symbol_body({ symbol_name: "ClassName/methodName", new_body: "..." })

【検索優先度】
1. find_symbol — シンボル名が分かる場合
2. find_file — ファイル名が分かる場合
3. search_for_pattern — 上記で見つからない場合（最終手段）

【トークン最適化】
• 検索パスを絞る — src/services/ > src/
• include_body: false 先行 — 概要把握後に詳細取得
• 500行以上のファイルは分割取得 — 必要部分のみ取得
• 目標: 2000トークン以下/検索 — 大量結果を回避

【シンボル操作一覧】
• 概要取得 — get_symbols_overview
• シンボル検索 — find_symbol
• 参照検索 — find_referencing_symbols
• 本体置換 — replace_symbol_body
• 前に挿入 — insert_before_symbol
• 後に挿入 — insert_after_symbol
• リネーム — rename_symbol

【name_path パターン】
• ClassName — クラス全体
• ClassName/method — クラス内メソッド
• ClassName/__init__ — コンストラクタ（Python）
• function_name — トップレベル関数

【検証チェックリスト】
• オンボーディング完了確認
• メモリに関連情報がないか確認
• シンボル検索を優先している
• 編集前に参照シンボルを確認（後方互換性）`
  },
  'testing-rules': {
    summary: 'テストルール',
    body: `【TDD サイクル】
1. RED: 失敗するテストを書く → テスト失敗を確認
2. GREEN: テストを通す最小限の実装
3. REFACTOR: テストが通る状態を維持しつつコード改善

【テスト命名規則】
• should + 期待動作 — should return user when id exists
• when + 条件 — when input is empty, should throw error
• given/when/then — given valid input, when submitted, then saves data

【カバレッジ目標】
• Statements: 80%
• Branches: 75%
• Functions: 80%
• Lines: 80%

【モック使用基準】
• 外部API — モックする
• データベース — モックする（ユニットテスト）
• 時間 — モックする（Date.now 等）
• 内部ロジック — モックしない

【検証チェックリスト】

テストコード品質:
• テスト名が振る舞いを説明している
• 1テスト = 1アサーション（原則）
• AAA パターン（Arrange-Act-Assert）に従っている
• 実装ではなく振る舞いをテスト
• テストが独立している（順序依存なし）

プッシュ前:
• 全テスト通過
• カバレッジ目標達成
• Lint エラーなし
• 型チェック通過
• ビルド成功`
  },
};

function collectAgents() {
  const dir = join(ROOT, 'agents');
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter(f => f.endsWith('.md')).map(f => {
    const content = readFile(join(dir, f));
    const { meta, body } = extractFrontmatter(content);
    const name = meta.name || f.replace('.md', '');
    return {
      name,
      description: agentFullJa[name]?.summary || name,
      tools: meta.tools || '',
      color: meta.color || 'gray',
      bodySections: extractSections(body)
    };
  });
}

function collectSkills() {
  const dir = join(ROOT, 'skills');
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter(e => e.isDirectory())
    .map(e => {
      const skillFile = join(dir, e.name, 'SKILL.md');
      const content = readFile(skillFile);
      if (!content) return null;
      const { meta, body } = extractFrontmatter(content);
      const name = meta.name || e.name;
      const triggers = (meta.description || '').split('\n')
        .find(l => l.startsWith('トリガー'));
      const triggerList = triggers
        ? triggers.replace(/^トリガー:\s*/, '').split(/[「」]/).filter(t => t.trim() && t !== ' ')
        : [];
      return {
        name,
        description: skillFullJa[name]?.summary || name,
        triggers: triggerList,
        bodySections: extractSections(body)
      };
    })
    .filter(Boolean);
}

function collectRules() {
  const dir = join(ROOT, 'rules');
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter(f => f.endsWith('.md')).map(f => {
    const content = readFile(join(dir, f));
    if (!content) return null;
    const sections = extractSections(content);
    const title = sections[0]?.title || f.replace('.md', '');
    const desc = sections[0]?.content?.trim().split('\n')[0] || '';
    return { name: f.replace('.md', ''), filename: f, title, description: desc, bodySections: sections };
  }).filter(Boolean);
}

// Rule Japanese descriptions
const ruleDescJa = {
  'security': 'シークレット禁止、入力バリデーション、認証・認可のセキュリティルール',
  'code-quality': '命名規則、関数設計、エラー処理、コメントのコード品質ルール',
  'pre-commit': 'コミット前に確認すべきチェックリスト',
  'naming': 'ディレクトリ・ファイルの命名規則（docs は English_日本語 形式）',
  'task-dispatch': 'プロンプト解析→実行モード選択（Direct / SubAgent / Agent Teams）の判断基準とパターン',
  'version-check': 'セッション開始時に Claude Code の最新バージョンを確認し、新機能の設定取り込みを評価',
};

function collectCommands() {
  const dir = join(ROOT, 'commands');
  if (!existsSync(dir)) return [];
  const results = [];
  function scan(d, prefix = '') {
    for (const entry of readdirSync(d, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        scan(join(d, entry.name), prefix + entry.name + '/');
      } else if (entry.name.endsWith('.md')) {
        const name = prefix + entry.name.replace('.md', '');
        const content = readFile(join(d, entry.name));
        const { body } = content ? extractFrontmatter(content) : { body: '' };
        results.push({ name, bodySections: extractSections(body) });
      }
    }
  }
  scan(dir);
  return results;
}

// Command Japanese descriptions
const commandDescJa = {
  'slash-guide': 'Claude Code の全スラッシュコマンド（/help, /compact, /fork, /clear 等）を日本語で解説するガイド。組み込みコマンドの使い方、オプション、ユースケースを網羅。',
  'kiro/spec-init': '仕様駆動開発の開始点。プロジェクト説明を入力すると、仕様ディレクトリ（.kiro/specs/）を初期化し、要件・設計・タスクの骨格を作成する。',
  'kiro/spec-requirements': 'プロジェクトの包括的な要件定義を生成。機能要件・非機能要件・制約条件・受入基準を構造化して出力。',
  'kiro/spec-design': '要件に基づいた技術設計を作成。アーキテクチャ、データモデル、API 設計、技術選定の根拠を文書化。',
  'kiro/spec-tasks': '技術設計から実装タスクを自動生成。依存関係、優先順位、見積り時間を含むタスクリストを作成。',
  'kiro/spec-impl': 'TDD（テスト駆動開発）に基づいてタスクを実装。Red → Green → Refactor のサイクルで進行。',
  'kiro/spec-status': '仕様全体の進捗状況を表示。要件・設計・タスクの完了率、未着手・進行中・完了の内訳を確認。',
  'kiro/steering': '.kiro/steering/ ディレクトリに永続的なプロジェクト知識を管理。コーディング規約、アーキテクチャ決定、チーム合意事項を記録。',
  'kiro/steering-custom': '特定のプロジェクトコンテキストに特化したステアリングドキュメントを作成。フレームワーク固有のルールや業界固有の制約を定義。',
  'kiro/validate-design': '技術設計の品質をインタラクティブにレビュー。整合性、拡張性、セキュリティ、パフォーマンスの観点から評価。',
  'kiro/validate-gap': '要件定義と既存コードベースのギャップを分析。未実装の要件、乖離している実装、不足しているテストを特定。',
  'kiro/validate-impl': '実装が要件・設計・タスクと整合しているか検証。コード品質、テストカバレッジ、設計準拠を確認。',
};

function parseGitignore() {
  const content = readFile(join(ROOT, '.gitignore'));
  if (!content) return { ignored: [], tracked: [] };
  const ignored = [];
  const tracked = [];
  let inTracked = false;
  for (const line of content.split('\n')) {
    if (line.includes('Tracked files')) { inTracked = true; continue; }
    if (line.startsWith('#') || !line.trim()) continue;
    if (inTracked) tracked.push(line.replace(/^#\s*/, '').trim());
    else ignored.push(line.trim());
  }
  return { ignored, tracked };
}

// CLAUDE.md section Japanese descriptions (summary + full)
const sectionFullJa = {
  'Global Claude Code Settings': { summary: 'グローバル Claude Code 設定', body: '' },
  'Language': { summary: '言語設定',
    body: `• 常に日本語で応答する（明示的に英語を指定された場合を除く）
• コード・コメント・ドキュメントは英語で記述
• 技術用語は原語のまま使用（例: API, Docker, Kubernetes）` },
  'Response Style': { summary: '応答スタイル',
    body: `• 結論ファースト: 解決策を最初に提示し、詳細は後から
• コード重複を避ける: ユーザー提供のコードは不必要に再表示しない
• 簡潔でカジュアル: 過度な丁寧語や長い導入は省略
• コード参照: file_path:line_number 形式で記載` },
  'Pre-Implementation Steps': { summary: '実装前の必須ステップ',
    body: `1. Context7 で最新 API 確認: フレームワーク/ライブラリ使用時は resolve-library-id → query-docs を実行
2. 既存パターン確認: Grep/Glob でプロジェクト内の既存実装パターンを確認
3. 影響範囲の特定: 変更が及ぶファイル・モジュールを事前に洗い出す` },
  'Pre-Commit Checklist': { summary: 'コミット前チェック',
    body: `• テスト通過（npm test / pytest / プロジェクト固有コマンド）
• Lint/型チェック通過
• git diff --staged で意図した変更のみか確認
• 機密情報（.env, credentials）が含まれていないか確認` },
  'MCP Tool Selection': { summary: 'MCP ツール使い分け',
    body: `• ライブラリ API 確認 → Context7（実装前の最新ドキュメント参照）
• 外部リサーチ → Gemini（ベストプラクティス・技術比較・トレンド調査）
• コード解析 → Serena（シンボル検索・依存関係・リファクタ影響調査）
• GitHub 操作 → GitHub MCP（PR作成・Issue管理・コード検索）
• Azure 操作 → Azure MCP（リソース管理・ドキュメント参照）
• ブラウザ操作 → Playwright（E2Eテスト・Webスクレイピング）` },
  'Workflow Principles': { summary: 'ワークフロー原則',
    body: `• main ブランチ直接作業禁止: 全ての変更はフィーチャー/トピックブランチで行い、承認済み PR のマージ時のみ main を更新する
• Worktree 必須: ブランチ作業は git worktree add で分離。作成先は .git/worktrees/ 配下とする（例: git worktree add .git/worktrees/<name> <branch>）
• 過剰設計禁止: 依頼された内容のみ実装、「念のため」機能は作らない
• 既存パターン尊重: プロジェクトのコードスタイル・アーキテクチャに従う
• 破壊的操作は確認: force push, reset --hard 等は必ずユーザー確認` },
  'Context Management': { summary: 'コンテキスト管理',
    body: `タスク開始前にリクエストを分析し、最適な戦略を提案する:

• 大規模探索（多数ファイル） → サブエージェントに委譲。親コンテキストにはサマリのみ入る
• 複数アプローチを試す → /fork でセッションを分岐し、結果を比較
• 長い実装 → /compact <focus> を約60%で事前実行。Plan Mode を先行
• 簡単な修正/小さな変更 → 直接実行、特別な管理不要
• コードレビュー/調査 → 読み取り専用ツールのサブエージェント
• 無関係なフォローアップタスク → /clear で新規開始

テクニック:
• サブエージェント委譲: リサーチ/探索を分離されたコンテキストで実行。親はサマリのみ受け取る
• /compact <focus>: 明示的な保持指示付きの事前圧縮
• /rewind（Esc×2）: 「会話のみ」はコードを保持してコンテキストをリセット。「ここからまとめる」は部分的なコンパクション
• /fork: メインセッションを汚さずに代替アプローチを分岐
• /btw: コンテキストコストゼロの質問（履歴に保存されない）
• Plan Mode（Shift+Tab×2）: 実装前の読み取り専用探索
• /context: トークン使用量を定期的に監視` },
  'Session Naming': { summary: 'セッション命名',
    body: `• /rename でタスクを反映した名前（15〜20文字）を付ける
• タスクの進行に合わせて名前を更新する
• 形式: <アクション>-<対象>（例: 「設定最適化-CLAUDE.md」「API実装-認証機能」）
• リネームするタイミング: セッション開始時、大きなタスク変更時、スコープが明確になった時` },
  'Compact Instructions': { summary: 'コンパクション指示',
    body: `コンパクション時に保持すること:
• 現在のタスク目標と進捗状況
• 変更済みファイルのパスと変更内容の要約
• 未解決の問題・ブロッカー
• ユーザーの明示的な好み
• アーキテクチャ決定とその理由` },
  'Important Reminders': { summary: '重要なリマインダー',
    body: `• 明示的に依頼されない限り、ファイル作成やドキュメント生成は行わない
• テストは振る舞いをテストする。実装詳細はテストしない
• エラー発生時は根本原因を調査する。安易なリトライやバイパスは避ける` },
};

// Hook description mapping (Japanese)
const hookDescJa = {
  'PreToolUse': 'ツール実行前のセーフティチェック',
  'PostToolUse': 'ファイル保存後の自動処理',
  'Stop': 'タスク完了時の通知',
  'Notification': 'デスクトップ通知',
};

const hookDetailJa = {
  'rm -rf': '破壊的コマンド（rm -rf 等）をブロック',
  'git push': 'force push をブロック',
  'prettier': 'JS/TS ファイルを prettier で自動整形',
  'generate-dashboard': '設定ファイル変更時にダッシュボード HTML を再生成',
  'Task complete': 'タスク完了メッセージを出力',
  'terminal-notifier': 'macOS デスクトップ通知を送信',
};

/** Generate annotated directory tree with Japanese comments */
function generateAnnotatedTree(agents, skills, commands) {
  // File/directory comment mapping
  const comments = {
    '.gitignore': 'ランタイムデータの除外ルール',
    'CLAUDE.md': '全プロジェクト共通のグローバル指示',
    'README.md': 'リポジトリの説明・セットアップ手順',
    'settings.json': '権限・Hook・環境変数・MCP 設定',
    'agents/': 'カスタムエージェント定義（7種）',
    'commands/': 'スラッシュコマンド定義',
    'skills/': 'カスタムスキル定義（13種）',
    'scripts/': '自動化スクリプト',
    'plugins/': 'プラグイン管理',
    // Agents
    'code-reviewer.md': 'コード品質・セキュリティレビュー',
    'devops-problem-solver.md': 'システム障害の診断・解決',
    'estimation-agent.md': 'プロジェクト見積り・見積書作成',
    'senior-consultant-reviewer.md': '要件・設計・見積りのレビュー',
    'task-decomposer.md': 'タスク分解・計画作成',
    'test-runner.md': 'テスト実行・カバレッジ分析',
    'workflow-recorder.md': 'ワークフロートレース自動記録',
    // Commands
    'kiro/': '仕様駆動開発ワークフロー（11コマンド）',
    'slash-guide.md': '全スラッシュコマンドの日本語解説',
    // Skills directories
    'acnpptx/': 'Accenture ブランド PowerPoint 生成',
    'claude-assist/': 'マルチライン入力 GUI 支援',
    'development-rules/': 'Context7 リサーチ必須の開発ルール',
    'document-converter/': 'Markdown → Word/Excel/PDF 変換',
    'gemini-research/': 'Gemini MCP による外部リサーチ',
    'git-workflow/': 'Worktree 必須のブランチ管理',
    'login-eso/': 'Accenture SSO 認証（基盤ライブラリ）',
    'metacognition-skill/': 'メタ認知スキル',
    'reserve-space/': 'Accenture Places スペース自動予約',
    'rough-estimate/': '概算見積書作成（Scibit LLC）',
    'serena-codebase/': 'Serena MCP によるコード解析',
    'skill-maker/': 'スキル自動構築・改善・評価',
    'testing-rules/': 'TDD サイクルに基づくテストルール',
    // Scripts
    'generate-dashboard.mjs': '設定ダッシュボード HTML 生成',
    // Skill sub-files
    'SKILL.md': 'スキル定義ファイル',
    // Kiro commands
    'spec-init.md': '仕様の初期化',
    'spec-requirements.md': '要件定義の生成',
    'spec-design.md': '技術設計の作成',
    'spec-tasks.md': '実装タスクの生成',
    'spec-impl.md': 'TDD による実装実行',
    'spec-status.md': '仕様の進捗確認',
    'steering.md': 'プロジェクト知識の管理',
    'steering-custom.md': 'カスタムステアリング作成',
    'validate-design.md': '技術設計の品質レビュー',
    'validate-gap.md': '要件と実装のギャップ分析',
    'validate-impl.md': '実装の検証',
    // Other files
    'known_marketplaces.json': '公式マーケットプレイス定義',
    'installed_plugins.json': 'インストール済みプラグイン',
  };

  function buildTree(dir, depth = 0) {
    if (depth > 2) return [];
    const ignoreList = ['.git', '.playwright-mcp', 'node_modules', 'projects', 'debug', 'sessions',
      'file-history', 'session-env', 'shell-snapshots', 'downloads', 'telemetry', 'paste-cache',
      'backups', 'ide', 'todos', 'tasks', 'plans', 'data', 'statsig', 'cache',
      'history.jsonl', 'mcp-needs-auth-cache.json', 'stats-cache.json', 'settings.local.json',
      'blocklist.json', 'marketplaces'];
    try {
      const entries = readdirSync(dir, { withFileTypes: true })
        .filter(e => !ignoreList.includes(e.name) && !e.name.startsWith('.DS_Store')
          && !e.name.startsWith('blocklist.json.') && !e.name.startsWith('.'))
        .sort((a, b) => {
          if (a.isDirectory() && !b.isDirectory()) return -1;
          if (!a.isDirectory() && b.isDirectory()) return 1;
          return a.name.localeCompare(b.name);
        });
      return entries.map(e => ({
        name: e.name,
        isDir: e.isDirectory(),
        comment: comments[e.name + (e.isDirectory() ? '/' : '')] || comments[e.name] || '',
        children: e.isDirectory() ? buildTree(join(dir, e.name), depth + 1) : []
      }));
    } catch { return []; }
  }

  function renderTree(nodes, prefix = '') {
    return nodes.map((node, i) => {
      const isLast = i === nodes.length - 1;
      const connector = isLast ? '└── ' : '├── ';
      const childPrefix = isLast ? '    ' : '│   ';
      const name = node.isDir ? node.name + '/' : node.name;
      const comment = node.comment ? `  <span class="tree-comment"># ${esc(node.comment)}</span>` : '';
      let line = `<span class="tree-line">${esc(prefix + connector)}<span class="tree-name${node.isDir ? ' tree-dir' : ''}">${esc(name)}</span>${comment}</span>\n`;
      if (node.isDir && node.children.length > 0) {
        line += renderTree(node.children, prefix + childPrefix);
      }
      return line;
    }).join('');
  }

  const tree = buildTree(ROOT);
  return `<div class="tree-block"><pre class="tree-pre">${renderTree(tree)}</pre></div>`;
}

// --- HTML Generation ---

function generateHtml() {
  const claudeMd = readFile(join(ROOT, 'CLAUDE.md')) || '';
  const settings = readJson(join(ROOT, 'settings.json')) || {};
  const agents = collectAgents();
  const skills = collectSkills();
  const commands = collectCommands();
  const rules = collectRules();
  const gitignore = parseGitignore();
  const tree = getDirectoryTree(ROOT);
  const claudeSections = extractSections(claudeMd);
  const now = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });

  const colorMap = {
    red: '#ef4444', orange: '#f97316', green: '#22c55e', blue: '#3b82f6',
    purple: '#a855f7', cyan: '#06b6d4', gray: '#6b7280'
  };

  const mcpServers = [
    { name: 'Azure', desc: 'Azure リソース操作・ドキュメント参照', icon: '☁️' },
    { name: 'Context7', desc: 'ライブラリの最新ドキュメント検索', icon: '📚' },
    { name: 'o3', desc: 'OpenAI o3 モデル連携', icon: '🧠' },
    { name: 'Serena', desc: 'セマンティックコード解析', icon: '🔍' },
    { name: 'Playwright', desc: 'ブラウザ自動操作・E2E テスト', icon: '🎭' },
    { name: 'GitHub', desc: 'PR・Issue・コード検索', icon: '🐙' },
    { name: 'Notion', desc: 'Notion ページ・DB 操作', icon: '📝' },
    { name: 'Gemini', desc: 'Google Gemini による外部リサーチ', icon: '✨' }
  ];

  // Categorize permissions
  const perms = settings.permissions?.allow || [];
  const permCategories = {
    'Git 操作': { items: perms.filter(p => p.includes('git')), desc: 'Git の読み取り系コマンドを許可' },
    'パッケージ管理': { items: perms.filter(p => p.match(/npm|pnpm/)), desc: 'npm / pnpm の実行を許可' },
    'MCP ツール': { items: perms.filter(p => p.startsWith('mcp__')), desc: '各 MCP サーバーのツール呼び出しを許可' },
    'CLI ツール': { items: perms.filter(p => p.match(/Bash\((node|python3|curl|az |azd|gh |npx|wc)/)), desc: 'Node.js, Python, Azure CLI 等のコマンドを許可' },
    'ファイル読み取り': { items: perms.filter(p => p.startsWith('Read(') || p.includes('filesystem')), desc: '指定ディレクトリ配下のファイル読み取りを許可' },
    'Web アクセス': { items: perms.filter(p => p.startsWith('WebFetch')), desc: '指定ドメインへの Web アクセスを許可' },
  };

  const hooks = settings.hooks || {};

  // Tab definitions matching file structure
  const tabs = [
    { id: 'overview', label: '概要', icon: '📋' },
    { id: 'claude-md', label: 'CLAUDE.md', icon: '📄' },
    { id: 'settings', label: 'settings.json', icon: '⚙️' },
    { id: 'agents', label: 'agents/', icon: '🤖' },
    { id: 'skills', label: 'skills/', icon: '🛠️' },
    { id: 'commands', label: 'commands/', icon: '⌨️' },
    { id: 'rules', label: 'rules/', icon: '📏' },
    { id: 'mcp', label: 'MCP 連携', icon: '🔌' },
  ];

  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code 設定ダッシュボード</title>
<style>
:root {
  --bg: #ffffff; --surface: #f8fafc; --surface2: #e2e8f0;
  --border: #cbd5e1; --text: #1e293b; --text2: #475569; --text3: #94a3b8;
  --accent: #2563eb; --accent2: #7c3aed; --accent-dim: rgba(37,99,235,.06);
  --red: #dc2626; --orange: #ea580c; --green: #16a34a;
  --blue: #2563eb; --purple: #7c3aed; --cyan: #0891b2;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; line-height: 1.6; }

/* Layout — sidebar tabs + content */
.container { max-width: 1200px; margin: 0 auto; padding: 1.5rem; }
.layout { display: flex; gap: 0; min-height: calc(100vh - 8rem); }
header { text-align: center; padding: 1.5rem 0 1rem; border-bottom: 1px solid var(--surface2); margin-bottom: 1.5rem; }
header h1 { font-size: 1.6rem; color: var(--accent); margin-bottom: .125rem; }
header .sub { color: var(--text2); font-size: .8rem; }
header .sub a { color: var(--accent); text-decoration: none; }

/* Sidebar tabs */
.tabs { display: flex; flex-direction: column; width: 180px; flex-shrink: 0; border-right: 1px solid var(--surface2); padding-right: 0; position: sticky; top: 1rem; align-self: flex-start; }
.tab { padding: .625rem 1rem; cursor: pointer; color: var(--text2); font-size: .8rem; font-weight: 500; border-right: 3px solid transparent; white-space: nowrap; transition: all .15s; user-select: none; display: flex; align-items: center; gap: .4rem; border-radius: .375rem 0 0 .375rem; }
.tab:hover { color: var(--text); background: var(--accent-dim); }
.tab.active { color: var(--accent); border-right-color: var(--accent); background: var(--accent-dim); font-weight: 600; }
.tab-icon { font-size: .9rem; }
.content-area { flex: 1; min-width: 0; }
.tab-panel { display: none; padding-left: 1.5rem; }
.tab-panel.active { display: block; }

/* Section */
h2 { font-size: 1.3rem; color: var(--accent); margin: 0 0 .5rem; }
h3 { font-size: 1rem; color: var(--text); margin: 1.25rem 0 .5rem; }
.section-desc { color: var(--text2); font-size: .85rem; margin-bottom: 1rem; }
.sep { border-top: 1px solid var(--surface2); margin: 1.5rem 0; }

/* Cards */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: .75rem; }
.card { background: var(--bg); border: 1px solid var(--surface2); border-radius: .625rem; padding: 1rem; transition: border-color .15s, box-shadow .15s; }
.card:hover { border-color: var(--border); box-shadow: 0 2px 8px rgba(0,0,0,.06); }
.card-head { display: flex; align-items: center; gap: .625rem; margin-bottom: .5rem; }
.card-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.card-name { font-weight: 600; font-size: .95rem; }
.card-desc { color: var(--text2); font-size: .8rem; line-height: 1.5; }
.card-tags { margin-top: .625rem; display: flex; flex-wrap: wrap; gap: .25rem; }
.tag { background: var(--surface2); color: var(--text3); padding: .125rem .5rem; border-radius: .25rem; font-size: .7rem; font-family: 'SF Mono', Menlo, monospace; }
.card-detail { margin-top: .5rem; }
.card-detail summary { color: var(--text2); font-size: .75rem; cursor: pointer; user-select: none; }
.card-detail-body { margin-top: .375rem; padding: .5rem .75rem; background: var(--surface); border-radius: .375rem; font-size: .75rem; color: var(--text2); border: 1px solid var(--surface2); }

/* Code / Pre */
pre { background: var(--surface); border: 1px solid var(--surface2); border-radius: .5rem; padding: .875rem; overflow-x: auto; font-size: .75rem; line-height: 1.6; color: var(--text2); font-family: 'SF Mono', Menlo, monospace; }
code { font-family: 'SF Mono', Menlo, monospace; font-size: .78rem; background: var(--surface); border: 1px solid var(--surface2); padding: .1rem .35rem; border-radius: .2rem; color: var(--accent); }

/* Table */
table { width: 100%; border-collapse: collapse; font-size: .8rem; border: 1px solid var(--surface2); border-radius: .375rem; overflow: hidden; }
th { background: var(--surface); color: var(--text); padding: .5rem .75rem; text-align: left; font-weight: 600; font-size: .75rem; letter-spacing: .03em; border-bottom: 2px solid var(--surface2); }
td { padding: .5rem .75rem; border-bottom: 1px solid var(--surface2); color: var(--text2); }
tr:hover td { background: var(--accent-dim); }

/* Chips */
.chip-list { display: flex; flex-wrap: wrap; gap: .375rem; }
.chip { background: var(--surface); color: var(--text2); padding: .25rem .625rem; border-radius: .375rem; font-size: .7rem; font-family: 'SF Mono', Menlo, monospace; border: 1px solid var(--surface2); }
.chip-accent { background: var(--accent-dim); color: var(--accent); border: 1px solid rgba(37,99,235,.15); }

/* Perm group */
.perm-group { margin-bottom: 1rem; }
.perm-head { display: flex; align-items: baseline; gap: .5rem; margin-bottom: .375rem; }
.perm-label { font-weight: 600; font-size: .85rem; }
.perm-sub { color: var(--text3); font-size: .75rem; }

/* Hook */
.hook-card { background: var(--bg); border: 1px solid var(--surface2); border-radius: .5rem; padding: .875rem; margin-bottom: .625rem; }
.hook-head { display: flex; align-items: center; gap: .5rem; margin-bottom: .375rem; }
.hook-type { font-weight: 600; font-size: .9rem; color: var(--accent); }
.hook-desc { color: var(--text2); font-size: .75rem; font-style: italic; }
.hook-cmd { color: var(--text3); font-size: .7rem; font-family: 'SF Mono', Menlo, monospace; margin-top: .25rem; padding: .375rem .5rem; background: var(--surface); border-radius: .25rem; word-break: break-all; }

/* MCP */
.mcp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: .625rem; }
.mcp-card { background: var(--bg); border: 1px solid var(--surface2); border-radius: .5rem; padding: .875rem; display: flex; align-items: center; gap: .75rem; transition: border-color .15s, box-shadow .15s; }
.mcp-card:hover { border-color: var(--border); box-shadow: 0 2px 8px rgba(0,0,0,.06); }
.mcp-icon { font-size: 1.4rem; flex-shrink: 0; }
.mcp-name { font-weight: 600; font-size: .85rem; }
.mcp-desc { color: var(--text2); font-size: .75rem; }

/* Stat bar */
.stat-bar { display: flex; gap: 1.5rem; flex-wrap: wrap; margin: 1rem 0; }
.stat { text-align: center; }
.stat-num { font-size: 1.75rem; font-weight: 700; color: var(--accent); }
.stat-label { font-size: .7rem; color: var(--text3); text-transform: uppercase; letter-spacing: .05em; }

/* Nav links */
.nav-link { color: var(--accent); text-decoration: none; }
.nav-link:hover { text-decoration: underline; }

/* File block (per-file view) */
.file-block { background: var(--bg); border: 1px solid var(--surface2); border-radius: .625rem; padding: 1.25rem; margin-bottom: 1rem; }
.file-block:hover { border-color: var(--border); }
.file-header { display: flex; align-items: center; gap: .5rem; margin-bottom: .5rem; flex-wrap: wrap; }
.file-name { font-family: 'SF Mono', Menlo, monospace; font-size: .85rem; font-weight: 600; color: var(--text); }
.file-meta { color: var(--text3); font-size: .7rem; font-family: 'SF Mono', Menlo, monospace; margin-left: auto; }
.file-subtitle { font-size: .9rem; font-weight: 600; color: var(--accent); margin-bottom: .75rem; }
.file-section-label { font-size: .75rem; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: .05em; margin: 1rem 0 .5rem; padding-top: .75rem; border-top: 1px solid var(--surface2); }
.file-block .ja-body { margin-bottom: .5rem; }
.file-block .fulltext-block { margin-top: .5rem; }

/* Annotated tree */
.tree-block { margin: .75rem 0; }
.tree-pre { background: var(--surface); border: 1px solid var(--surface2); border-radius: .5rem; padding: 1rem; font-size: .75rem; line-height: 1.8; overflow-x: auto; }
.tree-line { white-space: pre; }
.tree-name { color: var(--text); }
.tree-dir { color: var(--accent); font-weight: 600; }
.tree-comment { color: var(--text3); font-style: italic; font-size: .7rem; }

/* Full text block */
.fulltext-block { background: var(--surface); border: 1px solid var(--surface2); border-radius: .625rem; padding: 1.25rem 1.5rem; margin-bottom: 1rem; }
.fulltext-section { margin-bottom: 1.25rem; padding-bottom: 1.25rem; border-bottom: 1px solid var(--surface2); }
.fulltext-section:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.fulltext-section h4 { color: var(--text); font-size: .9rem; font-weight: 600; margin-bottom: .5rem; }
.fulltext-section p { color: var(--text2); font-size: .8rem; line-height: 1.8; margin-bottom: .25rem; }
.fulltext-section strong { color: var(--text); }
.fulltext-section ul, .fulltext-section ol { color: var(--text2); font-size: .8rem; line-height: 1.8; margin: .25rem 0 .5rem 1.25rem; }
.fulltext-section li { margin-bottom: .125rem; }
.fulltext-en { border-left: 3px solid var(--accent); }

/* Japanese body text */
.ja-body { color: var(--text2); font-size: .8rem; line-height: 1.8; padding: .75rem 1rem; background: var(--surface); border-radius: .5rem; border-left: 3px solid var(--accent2); }
.ja-body p { margin-bottom: .375rem; }
.ja-body strong { color: var(--text); font-weight: 600; }
.ja-body ul, .ja-body ol { margin: .25rem 0 .5rem 1.25rem; }
.ja-body li { margin-bottom: .125rem; line-height: 1.7; }

/* Responsive */
@media (max-width: 768px) {
  .layout { flex-direction: column; }
  .tabs { flex-direction: row; width: 100%; border-right: none; border-bottom: 1px solid var(--surface2); overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 0; }
  .tab { border-right: none; border-bottom: 3px solid transparent; border-radius: 0; }
  .tab.active { border-bottom-color: var(--accent); border-right-color: transparent; }
  .tab-panel { padding-left: 0; padding-top: 1rem; }
  .grid, .mcp-grid { grid-template-columns: 1fr; }
  .container { padding: .75rem; }
}
</style>
</head>
<body>
<div class="container">

<header>
  <h1>Claude Code 設定ダッシュボード</h1>
  <div class="sub">最終生成: ${esc(now)}</div>
</header>

<div class="layout">
<!-- Sidebar Tab Navigation -->
<nav class="tabs" role="tablist">
${tabs.map((t, i) => `  <div class="tab${i === 0 ? ' active' : ''}" role="tab" data-tab="${t.id}"><span class="tab-icon">${t.icon}</span>${t.label}</div>`).join('\n')}
</nav>

<!-- Content Area -->
<div class="content-area">

<!-- ===== Tab: 概要 ===== -->
<div id="tab-overview" class="tab-panel active">
  <h2>概要</h2>
  <p class="section-desc">Claude Code（<code>~/.claude/</code>）の設定ファイル構成と各機能の一覧です。タブを切り替えて詳細を確認できます。</p>

  <div class="stat-bar">
    <div class="stat"><div class="stat-num">${agents.length}</div><div class="stat-label">エージェント</div></div>
    <div class="stat"><div class="stat-num">${skills.length}</div><div class="stat-label">スキル</div></div>
    <div class="stat"><div class="stat-num">${commands.length}</div><div class="stat-label">コマンド</div></div>
    <div class="stat"><div class="stat-num">${rules.length}</div><div class="stat-label">Rules</div></div>
    <div class="stat"><div class="stat-num">${mcpServers.length}</div><div class="stat-label">MCP 連携</div></div>
    <div class="stat"><div class="stat-num">${perms.length}</div><div class="stat-label">許可ルール</div></div>
    <div class="stat"><div class="stat-num">${Object.values(hooks).flat().reduce((sum, h) => sum + (h.hooks?.length || 0), 0)}</div><div class="stat-label">Hook</div></div>
  </div>

  <h3>ディレクトリ構成</h3>
  <p class="section-desc">Git 管理対象のファイルツリー。ランタイムデータ（projects/, debug/ 等）は除外。</p>
  ${generateAnnotatedTree(agents, skills, commands)}

  <div class="sep"></div>
  <h3>エージェント一覧</h3>
  <p class="section-desc">特定タスクに特化した専門エージェント。サブエージェントとして起動され、指定されたツールのみ使用可能。</p>
  <table>
    <tr><th>エージェント</th><th>用途</th><th>使用ツール</th><th>カラー</th></tr>
    ${agents.map(a => {
      const full = agentFullJa[a.name];
      return `<tr><td><a href="#" class="nav-link" data-tab="agents" data-target="file-agent-${a.name}"><code>${esc(a.name)}</code></a></td><td>${esc(full?.summary || a.description)}</td><td style="font-size:.7rem;">${esc(a.tools)}</td><td><span class="card-dot" style="background:${colorMap[a.color] || colorMap.gray};display:inline-block;vertical-align:middle;margin-right:.25rem;"></span>${esc(a.color)}</td></tr>`;
    }).join('\n    ')}
  </table>

  <div class="sep"></div>
  <h3>スキル一覧</h3>
  <p class="section-desc">定型ワークフローをカプセル化したスキル。特定のトリガーワードで自動起動。</p>
  <table>
    <tr><th>スキル</th><th>用途</th><th>トリガー例</th></tr>
    ${skills.map(s => {
      const full = skillFullJa[s.name];
      return `<tr><td><a href="#" class="nav-link" data-tab="skills" data-target="file-skill-${s.name}"><code>${esc(s.name)}</code></a></td><td>${esc(full?.summary || s.description)}</td><td style="font-size:.7rem;">${s.triggers.slice(0, 3).map(t => esc(t)).join('、') || '—'}</td></tr>`;
    }).join('\n    ')}
  </table>

  <div class="sep"></div>
  <h3>コマンド一覧</h3>
  <p class="section-desc">Claude Code で /コマンド名 として呼び出せるカスタムコマンド。</p>
  <table>
    <tr><th>コマンド</th><th>説明</th></tr>
    ${commands.map(c => {
      const descJa = commandDescJa[c.name] || '';
      const cmdId = c.name.split('/').join('-');
      return `<tr><td><a href="#" class="nav-link" data-tab="commands" data-target="file-cmd-${cmdId}"><code>/${esc(c.name)}</code></a></td><td style="font-size:.8rem;">${esc(descJa).slice(0, 60)}${descJa.length > 60 ? '…' : ''}</td></tr>`;
    }).join('\n    ')}
  </table>

  <div class="sep"></div>
  <h3>ルール一覧</h3>
  <p class="section-desc">常時適用されるルール。CLAUDE.md とは別に rules/ ディレクトリで管理。</p>
  <table>
    <tr><th>ルール</th><th>説明</th></tr>
    ${rules.map(r => `<tr><td><a href="#" class="nav-link" data-tab="rules" data-target="file-rule-${r.name}"><code>${esc(r.filename)}</code></a></td><td>${esc(ruleDescJa[r.name] || r.description)}</td></tr>`).join('\n    ')}
  </table>

  <div class="sep"></div>
  <h3>.gitignore — 追跡/除外ルール</h3>
  <p class="section-desc">ランタイムで自動生成されるデータを除外し、設定ファイルのみを Git 管理。</p>
  <table>
    <tr><th>除外パターン</th><th>種別</th></tr>
    ${gitignore.ignored.slice(0, 8).map(p => `<tr><td><code>${esc(p)}</code></td><td>ランタイムデータ</td></tr>`).join('\n    ')}
    ${gitignore.ignored.length > 8 ? `<tr><td colspan="2" style="color:var(--text3)">…他 ${gitignore.ignored.length - 8} パターン</td></tr>` : ''}
  </table>
</div>

<!-- ===== Tab: CLAUDE.md ===== -->
<div id="tab-claude-md" class="tab-panel">
  <h2>CLAUDE.md — グローバル指示</h2>
  <p class="section-desc">全プロジェクトに適用されるルール。Claude Code 起動時に自動で読み込まれます。</p>

  <h3>📖 日本語全文</h3>
  <div class="fulltext-block">
    ${claudeSections.filter(s => sectionFullJa[s.title]?.body).map(s => {
      const full = sectionFullJa[s.title];
      return `<div class="fulltext-section"><h4>${esc(full.summary)}</h4>${jaBodyToHtml(full.body)}</div>`;
    }).join('')}
  </div>

  <div class="sep"></div>
  <h3>📄 英語全文（原文）</h3>
  <div class="fulltext-block fulltext-en">
    ${claudeSections.map(s => {
      return `<div class="fulltext-section"><h4>${esc(s.title)}</h4><div style="line-height:1.7;">${mdToHtml(s.content.trim())}</div></div>`;
    }).join('')}
  </div>

  <div class="sep"></div>
  <h3>📑 セクション別（日本語説明 + 英語原文）</h3>
  <p class="section-desc">各セクションの日本語説明と、対応する英語原文を並べて表示します。</p>

  ${claudeSections.map(s => {
    const full = sectionFullJa[s.title];
    return `
  <div class="card" style="margin-bottom:.75rem;">
    <div class="card-head">
      <div class="card-dot" style="background:var(--accent)"></div>
      <div class="card-name">${esc(full?.summary || s.title)}</div>
      <span style="color:var(--text3);font-size:.7rem;margin-left:auto;font-family:monospace;">${esc(s.title)}</span>
    </div>
    ${full?.body ? `<div class="ja-body" style="margin-bottom:.5rem;">${jaBodyToHtml(full.body)}</div>` : ''}
    <details class="card-detail" open>
      <summary>英語原文</summary>
      <div class="card-detail-body" style="line-height:1.7;">${mdToHtml(s.content.trim())}</div>
    </details>
  </div>`;
  }).join('')}
</div>

<!-- ===== Tab: settings.json ===== -->
<div id="tab-settings" class="tab-panel">
  <h2>settings.json — 権限・Hook・環境変数</h2>
  <p class="section-desc">Claude Code の動作を制御する設定ファイル。ツール実行の許可/拒否、自動処理、環境変数を定義。</p>

  <h3>権限（Permissions）</h3>
  <p class="section-desc">Claude Code が自動実行できるツール・コマンドのホワイトリスト。ここに含まれない操作は実行前に確認が求められます。</p>
  ${Object.entries(permCategories).filter(([, v]) => v.items.length > 0).map(([cat, { items, desc }]) => `
  <div class="perm-group">
    <div class="perm-head">
      <span class="perm-label">${esc(cat)}</span>
      <span class="perm-sub">— ${esc(desc)}</span>
    </div>
    <div class="chip-list">
      ${items.map(p => `<span class="chip">${esc(p)}</span>`).join('\n      ')}
    </div>
  </div>`).join('')}

  <div class="sep"></div>
  <h3>Hook（自動処理）</h3>
  <p class="section-desc">ツール実行やタスク完了時に自動で実行されるコマンド。安全性チェックやコード整形を自動化。</p>
  ${Object.entries(hooks).map(([type, hookArr]) => `
  <div class="hook-card">
    <div class="hook-head">
      <span class="hook-type">${esc(type)}</span>
      <span class="hook-desc">${esc(hookDescJa[type] || '')}</span>
    </div>
    ${hookArr.map(h => `
    <div style="margin-top:.5rem;">
      ${h.matcher ? `<div style="margin-bottom:.25rem;"><span class="chip chip-accent">matcher: ${esc(h.matcher)}</span></div>` : ''}
      ${(h.hooks || []).map(hk => {
        const cmd = hk.command || '';
        const detail = Object.entries(hookDetailJa).find(([k]) => cmd.includes(k));
        return `<div style="margin-bottom:.375rem;"><div style="color:var(--text2);font-size:.75rem;margin-bottom:.125rem;">${detail ? '→ ' + esc(detail[1]) : ''}</div><div class="hook-cmd">${esc(cmd)}</div></div>`;
      }).join('')}
    </div>`).join('')}
  </div>`).join('')}

  <div class="sep"></div>
  <h3>環境変数・その他</h3>
  <p class="section-desc">Claude Code のグローバル動作設定。</p>
  <table>
    <tr><th>設定</th><th>値</th><th>説明</th></tr>
    ${Object.entries(settings.env || {}).map(([k, v]) => `<tr><td><code>${esc(k)}</code></td><td>${esc(String(v))}</td><td>${k === 'CLAUDE_AUTOCOMPACT_PCT_OVERRIDE' ? 'コンテキスト使用量 70% でオートコンパクション' : ''}</td></tr>`).join('\n    ')}
    <tr><td><code>language</code></td><td>${esc(settings.language || 'N/A')}</td><td>応答言語（日本語）</td></tr>
    <tr><td><code>model</code></td><td>${esc(settings.model || 'N/A')}</td><td>使用モデル</td></tr>
    <tr><td><code>includeCoAuthoredBy</code></td><td>${settings.includeCoAuthoredBy ? 'true' : 'false'}</td><td>コミットの Co-authored-by</td></tr>
    <tr><td><code>defaultMode</code></td><td>${esc(settings.permissions?.defaultMode || 'N/A')}</td><td>権限のデフォルトモード</td></tr>
  </table>
</div>

<!-- ===== Tab: Agents ===== -->
<div id="tab-agents" class="tab-panel">
  <h2>agents/ — カスタムエージェント</h2>
  <p class="section-desc">特定タスクに特化した専門エージェント。サブエージェントとして起動され、指定されたツールのみ使用可能。各エージェントはカラーコードで識別。</p>

  <table class="index-table">
    <tr><th>エージェント</th><th>用途</th><th>ツール</th></tr>
    ${agents.map(a => `<tr><td><a href="#" class="nav-link" data-tab="agents" data-target="file-agent-${a.name}"><code>${esc(a.name)}</code></a></td><td>${esc(agentFullJa[a.name]?.summary || a.description)}</td><td style="font-size:.7rem;">${esc(a.tools)}</td></tr>`).join('\n    ')}
  </table>
  <div class="sep"></div>

  ${agents.map(a => {
    const full = agentFullJa[a.name];
    return `
    <div class="file-block" id="file-agent-${a.name}">
      <div class="file-header">
        <span class="card-dot" style="background:${colorMap[a.color] || colorMap.gray}"></span>
        <span class="file-name">agents/${esc(a.name)}.md</span>
        ${a.tools ? `<span class="file-meta">${esc(a.tools)}</span>` : ''}
      </div>
      <h4 class="file-subtitle">${esc(full?.summary || a.description)}</h4>
      ${full ? `<div class="file-section-label">📖 日本語全文</div><div class="ja-body">${jaBodyToHtml(full.body)}</div>` : ''}
      <div class="file-section-label">📄 英語全文（原文）</div>
      <div class="fulltext-block fulltext-en" style="margin-bottom:0;">
        ${a.bodySections.map(s => `<h5 style="color:var(--text);font-size:.8rem;margin:.5rem 0 .25rem;">${esc(s.title)}</h5><div style="line-height:1.7;">${mdToHtml(s.content.trim())}</div>`).join('')}
      </div>
    </div>`;
  }).join('')}
</div>

<!-- ===== Tab: Skills ===== -->
<div id="tab-skills" class="tab-panel">
  <h2>skills/ — カスタムスキル</h2>
  <p class="section-desc">定型ワークフローをカプセル化したスキル。特定のトリガーワードで自動起動します。各スキルは <code>SKILL.md</code> にルールとチェックリストを定義。</p>

  <table class="index-table">
    <tr><th>スキル</th><th>用途</th><th>トリガー例</th></tr>
    ${skills.map(s => `<tr><td><a href="#" class="nav-link" data-tab="skills" data-target="file-skill-${s.name}"><code>${esc(s.name)}</code></a></td><td>${esc(skillFullJa[s.name]?.summary || s.description)}</td><td style="font-size:.7rem;">${s.triggers.slice(0, 2).map(t => esc(t)).join('、') || '—'}</td></tr>`).join('\n    ')}
  </table>
  <div class="sep"></div>

  ${skills.map(s => {
    const full = skillFullJa[s.name];
    return `
    <div class="file-block" id="file-skill-${s.name}">
      <div class="file-header">
        <span class="card-dot" style="background:var(--accent)"></span>
        <span class="file-name">skills/${esc(s.name)}/SKILL.md</span>
      </div>
      <h4 class="file-subtitle">${esc(full?.summary || s.description)}</h4>
      ${s.triggers.length > 0 ? `<div class="card-tags" style="margin-bottom:.75rem;"><span style="color:var(--text3);font-size:.7rem;margin-right:.25rem;">トリガー:</span>${s.triggers.map(t => `<span class="chip chip-accent">${esc(t)}</span>`).join('')}</div>` : ''}
      ${full ? `<div class="file-section-label">📖 日本語全文</div><div class="ja-body">${jaBodyToHtml(full.body)}</div>` : ''}
      <div class="file-section-label">📄 英語全文（原文）</div>
      <div class="fulltext-block fulltext-en" style="margin-bottom:0;">
        ${s.bodySections.map(sec => `<h5 style="color:var(--text);font-size:.8rem;margin:.5rem 0 .25rem;">${esc(sec.title)}</h5><div style="line-height:1.7;">${mdToHtml(sec.content.trim())}</div>`).join('')}
      </div>
    </div>`;
  }).join('')}
</div>

<!-- ===== Tab: Commands ===== -->
<div id="tab-commands" class="tab-panel">
  <h2>commands/ — スラッシュコマンド</h2>
  <p class="section-desc">Claude Code で <code>/コマンド名</code> として呼び出せるカスタムコマンド。<code>commands/</code> ディレクトリに <code>.md</code> ファイルとして定義。</p>

  <table class="index-table">
    <tr><th>コマンド</th><th>説明</th></tr>
    ${commands.map(c => { const cmdId = c.name.split('/').join('-'); return `<tr><td><a href="#" class="nav-link" data-tab="commands" data-target="file-cmd-${cmdId}"><code>/${esc(c.name)}</code></a></td><td style="font-size:.8rem;">${esc((commandDescJa[c.name] || '').slice(0, 60))}${(commandDescJa[c.name] || '').length > 60 ? '…' : ''}</td></tr>`; }).join('\n    ')}
  </table>
  <div class="sep"></div>

  ${commands.map(c => {
    const descJa = commandDescJa[c.name] || '';
    return `
    <div class="file-block" id="file-cmd-${c.name.replace(/\//g, '-')}">
      <div class="file-header">
        <span class="card-dot" style="background:var(--purple)"></span>
        <span class="file-name">commands/${esc(c.name)}.md</span>
        <span class="chip chip-accent" style="margin-left:auto;">/${esc(c.name)}</span>
      </div>
      ${descJa ? `<div class="file-section-label">📖 日本語説明</div><div class="ja-body"><p>${esc(descJa)}</p></div>` : ''}
      ${c.bodySections.length > 0 ? `
      <div class="file-section-label">📄 英語全文（原文）</div>
      <div class="fulltext-block fulltext-en" style="margin-bottom:0;">
        ${c.bodySections.map(s => `<h5 style="color:var(--text);font-size:.8rem;margin:.5rem 0 .25rem;">${esc(s.title)}</h5><div style="line-height:1.7;">${mdToHtml(s.content.trim())}</div>`).join('')}
      </div>` : ''}
    </div>`;
  }).join('')}
</div>

<!-- ===== Tab: Rules ===== -->
<div id="tab-rules" class="tab-panel">
  <h2>rules/ — ルール</h2>
  <p class="section-desc">常時適用されるルール。CLAUDE.md とは別に <code>rules/</code> ディレクトリで管理し、モジュラーに分割。<code>paths</code> frontmatter でファイル種別ごとのオンデマンドロードも可能。</p>

  <table class="index-table">
    <tr><th>ルール</th><th>説明</th></tr>
    ${rules.map(r => `<tr><td><a href="#" class="nav-link" data-tab="rules" data-target="file-rule-${r.name}"><code>${esc(r.filename)}</code></a></td><td>${esc(ruleDescJa[r.name] || r.description)}</td></tr>`).join('\n    ')}
  </table>
  <div class="sep"></div>

  ${rules.map(r => `
    <div class="file-block" id="file-rule-${r.name}">
      <div class="file-header">
        <span class="card-dot" style="background:var(--orange)"></span>
        <span class="file-name">rules/${esc(r.filename)}</span>
      </div>
      <h4 class="file-subtitle">${esc(ruleDescJa[r.name] || r.title)}</h4>
      <div class="file-section-label">📖 日本語説明</div>
      <div class="ja-body"><p>${esc(ruleDescJa[r.name] || r.description)}</p></div>
      <div class="file-section-label">📄 英語全文（原文）</div>
      <div class="fulltext-block fulltext-en" style="margin-bottom:0;">
        ${r.bodySections.map(s => `<h5 style="color:var(--text);font-size:.8rem;margin:.5rem 0 .25rem;">${esc(s.title)}</h5><div style="line-height:1.7;">${mdToHtml(s.content.trim())}</div>`).join('')}
      </div>
    </div>`).join('')}
</div>

<!-- ===== Tab: MCP 連携 ===== -->
<div id="tab-mcp" class="tab-panel">
  <h2>MCP 連携サーバー</h2>
  <p class="section-desc">Model Context Protocol (MCP) で接続された外部サービス。Claude Code がリアルタイムでツールとして呼び出し可能。</p>

  <div class="mcp-grid">
  ${mcpServers.map(s => `
    <div class="mcp-card">
      <div class="mcp-icon">${s.icon}</div>
      <div>
        <div class="mcp-name">${esc(s.name)}</div>
        <div class="mcp-desc">${esc(s.desc)}</div>
      </div>
    </div>`).join('')}
  </div>

  <div class="sep"></div>
  <h3>MCP ツール使い分けガイド</h3>
  <p class="section-desc">CLAUDE.md で定義された、用途別のツール選択ルール。</p>
  <table>
    <tr><th>用途</th><th>ツール</th><th>使用場面</th></tr>
    <tr><td>ライブラリ API 確認</td><td>Context7</td><td>実装前の最新ドキュメント参照</td></tr>
    <tr><td>外部リサーチ</td><td>Gemini</td><td>ベストプラクティス・技術比較・トレンド調査</td></tr>
    <tr><td>コード解析</td><td>Serena</td><td>シンボル検索・依存関係・リファクタ影響調査</td></tr>
    <tr><td>GitHub 操作</td><td>GitHub MCP</td><td>PR 作成・Issue 管理・コード検索</td></tr>
    <tr><td>Azure 操作</td><td>Azure MCP</td><td>リソース管理・ドキュメント参照</td></tr>
    <tr><td>ブラウザ操作</td><td>Playwright</td><td>E2E テスト・Web スクレイピング</td></tr>
  </table>
</div>

</div><!-- /.content-area -->
</div><!-- /.layout -->
</div><!-- /.container -->

<script>
// Tab switching
function switchTab(tabId) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  const tabEl = document.querySelector('.tab[data-tab="' + tabId + '"]');
  if (tabEl) tabEl.classList.add('active');
  const panel = document.getElementById('tab-' + tabId);
  if (panel) panel.classList.add('active');
}

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

// Navigation links: switch tab + scroll to target
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const tabId = link.dataset.tab;
    const targetId = link.dataset.target;
    switchTab(tabId);
    requestAnimationFrame(() => {
      const el = document.getElementById(targetId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        el.style.outline = '2px solid var(--accent)';
        setTimeout(() => { el.style.outline = ''; }, 2000);
      }
    });
  });
});
</script>
</body>
</html>`;
}

// --- README Generation ---

function generateReadme() {
  const settings = readJson(join(ROOT, 'settings.json')) || {};
  const agents = collectAgents();
  const skills = collectSkills();
  const commands = collectCommands();

  return `# claudefiles

Claude Code（\`~/.claude/\`）の設定ファイルを管理するリポジトリ。

## 構成

\`\`\`
~/.claude/
├── .gitignore             # ランタイムデータ除外
├── CLAUDE.md              # グローバル指示（全プロジェクト共通）
├── settings.json          # 権限・Hooks・環境変数・MCP設定
├── agents/                # カスタムエージェント（${agents.length}種）
├── commands/              # スラッシュコマンド
│   ├── slash-guide.md
│   └── kiro/              # 仕様駆動開発ワークフロー（11コマンド）
├── skills/                # カスタムスキル（${skills.length}種）
│   ├── development-rules/
│   ├── testing-rules/
│   ├── git-workflow/
│   ├── gemini-research/
│   ├── serena-codebase/
│   ├── document-converter/
│   └── rough-estimate/
└── scripts/               # 自動化スクリプト
    ├── generate-dashboard.mjs  # ダッシュボード HTML + README 生成
    └── auto-sync.sh            # 設定変更時の自動 commit & push
\`\`\`

## CLAUDE.md

全プロジェクトに適用されるグローバル指示ファイル。

- **言語**: 日本語で応答、コードは英語
- **スタイル**: 結論ファースト、簡潔でカジュアル
- **原則**: 依頼されたことだけを行う、ファイル作成は最小限
- **コンテキスト管理**: タスク種別に応じた最適な戦略を提案

## settings.json

### 権限

Git 読み取り系（\`status\`, \`diff\`, \`log\`, \`branch\`, \`worktree\`）、\`npm run\`, \`pnpm\`、MCP ツール（Context7, Azure, o3）等を許可。

### Hooks

| Hook | 内容 |
|------|------|
| **PreToolUse** | 破壊的コマンド（\`rm -rf\` 等）と \`git push --force\` をブロック |
| **PostToolUse** | JS/TS ファイル保存時に prettier 自動整形 + 設定変更時にダッシュボード再生成 & 自動 push |
| **Stop** | タスク完了時の通知 |
| **Notification** | terminal-notifier でデスクトップ通知 |

### 環境変数

| 変数 | 値 | 説明 |
|------|-----|------|
| \`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE\` | \`70\` | コンテキスト70%でオートコンパクション |

### MCP 連携

- **Azure** — Azure リソース操作・ドキュメント参照
- **Context7** — ライブラリドキュメント検索
- **o3** — OpenAI o3 モデル連携
- **Serena** — セマンティックコード解析
- **Playwright** — ブラウザ自動操作
- **GitHub** — GitHub API 連携
- **Notion** — Notion API 連携
- **Gemini** — Google Gemini 連携

## エージェント

| エージェント | 用途 |
|-------------|------|
${agents.map(a => `| \`${a.name}\` | ${agentFullJa[a.name]?.summary || a.description} |`).join('\n')}

## スキル

| スキル | 用途 |
|--------|------|
${skills.map(s => `| \`${s.name}\` | ${skillFullJa[s.name]?.summary || s.description} |`).join('\n')}

## コマンド

### \`/slash-guide\`

Claude Code の全スラッシュコマンドを日本語で解説。

### \`/kiro/*\` — 仕様駆動開発ワークフロー

| コマンド | 用途 |
|---------|------|
| \`spec-init\` | 仕様の初期化 |
| \`spec-requirements\` | 要件定義の生成 |
| \`spec-design\` | 技術設計の作成 |
| \`spec-tasks\` | 実装タスクの生成 |
| \`spec-impl\` | TDD による実装実行 |
| \`spec-status\` | 仕様の進捗確認 |
| \`steering\` / \`steering-custom\` | プロジェクト知識の管理 |
| \`validate-design\` | 技術設計のレビュー |
| \`validate-gap\` | 要件と実装のギャップ分析 |
| \`validate-impl\` | 実装の検証 |

## 自動同期

設定ファイル（CLAUDE.md, settings.json, agents/*.md, skills/*/SKILL.md, commands/*.md）を変更すると、PostToolUse hook により以下が自動実行される:

1. ダッシュボード HTML（\`claudesettings-CLAUDE設定.html\`）を再生成
2. README.md を再生成
3. 全変更を \`git commit\` + \`git push origin main\`

## セットアップ

\`\`\`bash
git clone git@github.com:umaionigiri/claudefiles.git ~/.claude
\`\`\`

既に \`~/.claude/\` が存在する場合:

\`\`\`bash
git clone git@github.com:umaionigiri/claudefiles.git /tmp/claudefiles
ln -sf /tmp/claudefiles/CLAUDE.md ~/.claude/CLAUDE.md
ln -sf /tmp/claudefiles/settings.json ~/.claude/settings.json
ln -sf /tmp/claudefiles/agents ~/.claude/agents
ln -sf /tmp/claudefiles/commands ~/.claude/commands
ln -sf /tmp/claudefiles/skills ~/.claude/skills
\`\`\`
`;
}

// --- Main ---

try {
  const html = generateHtml();
  writeFileSync(OUTPUT, html, 'utf-8');
  console.log(`Dashboard generated: ${OUTPUT}`);

  const readme = generateReadme();
  writeFileSync(join(ROOT, 'README.md'), readme, 'utf-8');
  console.log('README.md generated');
} catch (err) {
  console.error('Generation failed:', err.message);
  process.exit(1);
}
