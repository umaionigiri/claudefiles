#!/usr/bin/env node
// Merge ECC hooks into user's settings.json (additive, non-destructive).
// Adds ECC_DISABLED_HOOKS env var with all adopted hook IDs initially disabled.
// Source: /tmp/everything-claude-code/hooks/hooks.json
// Target: /home/shokenohshiro/.claude/settings.json

import { readFileSync, writeFileSync } from 'node:fs';

const USER_SETTINGS = '/home/shokenohshiro/.claude/settings.json';
const ECC_HOOKS = '/tmp/everything-claude-code/hooks/hooks.json';

// 14 hook IDs adopted per Round 2 of the plan
const ADOPTED_IDS = new Set([
  'pre:bash:dispatcher',
  'pre:edit-write:gateguard-fact-force',
  'pre:config-protection',
  'post:edit:design-quality-check',
  'post:edit:accumulator',
  'post:quality-gate',
  'post:edit:console-warn',
  'stop:format-typecheck',
  'stop:check-console-log',
  'stop:desktop-notify',
  'stop:evaluate-session',
  'stop:cost-tracker',
  'post:session-activity-tracker',
  'pre:compact',
]);

const userSettings = JSON.parse(readFileSync(USER_SETTINGS, 'utf8'));
const eccHooks = JSON.parse(readFileSync(ECC_HOOKS, 'utf8')).hooks;

// Disable ALL adopted hooks initially. User removes ids from CSV to enable individually.
userSettings.env = userSettings.env || {};
userSettings.env.ECC_DISABLED_HOOKS = [...ADOPTED_IDS].join(',');
userSettings.env.ECC_HOOK_PROFILE = 'standard';

userSettings.hooks = userSettings.hooks || {};
let added = 0;
for (const [event, entries] of Object.entries(eccHooks)) {
  for (const entry of entries) {
    if (!entry.id) continue;
    if (!ADOPTED_IDS.has(entry.id)) continue;
    userSettings.hooks[event] = userSettings.hooks[event] || [];
    userSettings.hooks[event].push({
      matcher: entry.matcher,
      hooks: entry.hooks,
    });
    added += 1;
    console.log(`  added ${event} :: ${entry.id} (matcher=${entry.matcher})`);
  }
}

userSettings._eccAdoptedHooks = {
  note: 'Added by ECC import. Disable individually via ECC_DISABLED_HOOKS env var. To enable a hook, remove its id from the CSV.',
  ids: [...ADOPTED_IDS],
};

writeFileSync(USER_SETTINGS, JSON.stringify(userSettings, null, 2) + '\n');
console.log(`\nTotal: ${added} hook entries added.`);
console.log(`ECC_DISABLED_HOOKS now contains ${ADOPTED_IDS.size} hook ids (all disabled initially).`);
console.log('To enable hook X: remove "X" from ECC_DISABLED_HOOKS CSV in settings.json env.');
