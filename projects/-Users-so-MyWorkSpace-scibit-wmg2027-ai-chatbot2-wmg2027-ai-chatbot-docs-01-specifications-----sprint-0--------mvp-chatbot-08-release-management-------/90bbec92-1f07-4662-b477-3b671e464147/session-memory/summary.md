
# Session Title
_A short and distinctive 5-10 word descriptive title for the session. Super info dense, no filler_

WMG2027 Release Schedule Mermaid/PowerPoint Documentation Creation

# Current State
_What is actively being worked on right now? Pending tasks not yet completed. Immediate next steps._

**Completed:** All release schedule files are up-to-date with final dates.

**Final Schedule:**
- サイビット実装＆デプロイ: 12/12-12/16
- ペタビット確認: 12/16-12/18 (デザイン確認・動作確認)
- 本番リリース: 12/19

**Files updated (all in `docs/01_specifications_仕様書/sprint-0_初期導入開発_mvp-chatbot/08_release-management_リリース管理/`):**
- `WMG2027_リリーススケジュール_v1.0.0_20251210.md` - Mermaid gantt + tables
- `WMG2027_リリーススケジュール_v1.0.0_20251210_slides.md` - Pandoc source
- `WMG2027_リリーススケジュール_v1.0.0_20251210.pptx` - Generated PowerPoint

# Task specification
_What did the user ask to build? Any design decisions or other explanatory context_

User requested a release schedule visualization for chatbot and admin panel:

**Schedule Details (Final):**
- チャットボット (Chatbot):
  - 12/12: ペタビット delivers UI design to サイビット
  - 12/12-12/16: サイビット implements design & deploys to dev
  - 12/16-12/18: ペタビット confirms design

- 管理画面 (Admin Panel):
  - 12/11: サイビット submits re-estimate
  - 12/12: ペタビット reviews estimate (OK/NG) & delivers UI design
  - 12/12-12/16: サイビット implements & deploys to dev
  - 12/16-12/18: ペタビット confirms functionality

- 共通 (Common): 12/19 Production release

**Design Decisions:**
1. Mermaid gantt chart grouped by company (ペタビット/サイビット sections), not by product
2. Task labels: "チャットボット：〜" / "管理画面：〜" format
3. Timeline tables separated by company responsibility
4. PowerPoint via pandoc for presentation format

# Files and Functions
_What are the important files? In short, what do they contain and why are they relevant?_

**Created files:**
- `WMG2027_リリーススケジュール_v1.0.0_20251210.md` - Mermaid gantt chart + timeline tables (company-grouped)
- `WMG2027_リリーススケジュール_v1.0.0_20251210_slides.md` - Pandoc source for PowerPoint
- `WMG2027_リリーススケジュール_v1.0.0_20251210.pptx` - Generated PowerPoint (5 slides)

**Naming convention reference:**
- `WMG2027_AIチャットボット統合計画書_ペタビット社向け_v1.0.0_20251210.md` - existing file used as naming pattern
- Format: `WMG2027_{内容}_{バージョン}_{日付}.{ext}`

# Workflow
_What bash commands are usually run and in what order? How to interpret their output if not obvious?_

**PowerPoint generation:**
```bash
pandoc [source].md -o [output].pptx
```
- Pandoc installed at `/opt/homebrew/bin/pandoc`
- Uses `---` as slide separators in source markdown
- YAML frontmatter for title/author/date metadata

# Errors & Corrections
_Errors encountered and how they were fixed. What did the user correct? What approaches failed and should not be tried again?_

# Codebase and System Documentation
_What are the important system components? How do they work/fit together?_

**Directory structure for specifications:**
```
docs/01_specifications_仕様書/
├── sprint-0_初期導入開発_mvp-chatbot/
│   ├── 01_proposals_提案書/
│   ├── 08_release-management_リリース管理/  ← Release schedules go here
│   └── 99_archives_アーカイブ/
└── sprint-1_管理画面開発_admin-knowledge-mgmt/
    ├── 01_proposals_提案書/
    ├── 08_release-management_リリース管理/
    └── ...
```

User preference: Sprint-0 directory for this release schedule (covers both chatbot and admin panel)

# Learnings
_What has worked well? What has not? What to avoid? Do not duplicate items from other sections_

**User preferences for Mermaid gantt charts:**
- Group by company (section ペタビット / section サイビット), NOT by product
- Task label format: "製品名：作業内容" (e.g., "チャットボット：UIデザイン案連携")
- Keep company responsibility clearly visible at a glance

**For PowerPoint output:**
- User chose PPTX direct generation over HTML or Marp
- pandoc handles conversion well

# Key results
_If the user asked a specific output such as an answer to a question, a table, or other document, repeat the exact result here_

# Worklog
_Step by step, what was attempted, done? Very terse summary for each step_

1. Created initial Mermaid gantt chart with schedule data
2. User requested Sprint1 location → found sprint directories in docs/01_specifications_仕様書/
3. Checked naming convention from existing files (WMG2027_*_v1.0.0_YYYYMMDD.md)
4. User changed to Sprint0 path → created MD file there
5. User requested clearer company distinction → separated timeline tables by ペタビット/サイビット
6. User requested gantt grouped by company → changed sections from "チャットボット（ペタビット）" to "section ペタビット" with "チャットボット：〜" task labels
7. User requested PowerPoint → offered HTML/Marp/PPTX options
8. Generated PPTX via pandoc from slides markdown source
9. User requested implementation deadline extension → updated サイビット tasks from 12/15 to 12/16
10. Regenerated PowerPoint file with pandoc to reflect 12/16 date
11. User requested shifting ペタビット confirmation tasks by 1 day → updated:
    - Gantt chart p3, p4 tasks: 12/15-12/17 → 12/16-12/18
    - ペタビット作業 table: 12/17 → 12/18
    - Slides markdown: overview table + ペタビット作業 section dates
12. Regenerated PowerPoint with final dates
