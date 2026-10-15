# Research agent: plan status

## Status
- **Phase 0 (plumbing): done, except the live model call.** Switched from direct Haiku to Gateway Sonnet 5.
  - eve project scaffolded (`npx eve init . --non-interactive`), eve 0.79.1, Node 24.
  - `agent/instructions.md`, `agent/agent.ts`, `agent/tools/web_search.ts` written.
  - `npx tsc` passes. `npx eve build` passes. `eve dev --no-ui` serves sessions and streams events.
  - `eve eval`: 5 of 5 cases fail, all with `MODEL_CALL_FAILED ... The model connection is unavailable`. Cause: the project is not linked to Vercel, so there are no AI Gateway credentials. The failures are not agent-behavior results.
- **Phase 0 eval:** needs `eve link --project <name>` (Vercel login), then `npx eve eval`. Then judge the answers.

## Decisions
- Model: `anthropic/claude-sonnet-5` through Vercel AI Gateway. No Anthropic key needed. `claude-haiku-5-5` and `claude-sonnet-5-5` are not in the Gateway catalog. Haiku would need a direct Anthropic key.
- Search: `webSearch({ provider: "exa" })`, Gateway's default search provider.
- Default tools off (`defaultTools: false`): no shell, file, or fetch tools.
- Limits: 250k input and 50k output tokens per session. Session lifetime 20 minutes. Note: this also ends follow-up conversations after 20 minutes.
- Sandbox: eve requires one at build time, so `just-bash` is installed as a devDependency. The agent never calls it.
- Evals: five cases in `evals/research/`: known fact, contested, thin evidence, fabrication trap, dead link.

## Open questions
1. Link the project to Vercel (`eve link`), which needs your Vercel account and a project name. Can't be done from here without your login.
2. Search budget: 25 searches per run is written in the instructions but not enforced in code. Enforcing it needs a counting wrapper around search.
3. Session timeout vs. run time: the 20-minute limit ends a session, so long runs and follow-ups need durable workflow tools (a Phase 1 item).
4. Supabase storage, auth allowlist, and `web_fetch` for reading sources come after Phase 0 passes.

## Next
- Phase 0 eval after the Vercel link. Then Phase 1: `web_fetch` plus a trust-score tool, Supabase, and durable runs.
