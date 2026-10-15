# Research agent: plan status

## Status
- **Phase 0 (plumbing): done, except the live model call.** Switched from direct Haiku to Gateway Sonnet 5.
  - eve project scaffolded (`npx eve init . --non-interactive`), eve 0.79.1, Node 24.
  - `agent/instructions.md`, `agent/agent.ts`, `agent/tools/web_search.ts` written.
  - `npx tsc` passes. `npx eve build` passes. `eve dev --no-ui` serves sessions and streams events.
  - `eve eval`: 5 of 5 cases fail, all with `MODEL_CALL_FAILED` (credit card required by AI Gateway). The failures are not agent-behavior results.
- **Vercel:** project `env1-research-agent` created and linked (Hobby plan, personal scope). AI Gateway budget: $5 per month.
- **Phase 0 eval:** blocked on billing. All 5 evals fail with `AI Gateway requires a valid credit card on file`. Add a card in the Vercel dashboard (this also unlocks the free Gateway credit), then run `npx eve eval`.

## Decisions
- Model: `anthropic/claude-sonnet-5` through Vercel AI Gateway. No Anthropic key needed. `claude-haiku-5-5` and `claude-sonnet-5-5` are not in the Gateway catalog. Haiku would need a direct Anthropic key.
- Search: `webSearch({ provider: "exa" })`, Gateway's default search provider.
- Default tools off (`defaultTools: false`): no shell, file, or fetch tools.
- Limits: 250k input and 50k output tokens per session. Session lifetime 20 minutes. Note: this also ends follow-up conversations after 20 minutes.
- Sandbox: eve requires one at build time, so `just-bash` is installed as a devDependency. The agent never calls it.
- Evals: five cases in `evals/research/`: known fact, contested, thin evidence, fabrication trap, dead link.

## Open questions
1. Add a credit card to the Vercel account (AI Gateway requires one). The $5 monthly Gateway budget limits spend. Not deployed yet; the deploy needs your yes.
2. Search budget: 25 searches per run is written in the instructions but not enforced in code. Enforcing it needs a counting wrapper around search.
3. Session timeout vs. run time: the 20-minute limit ends a session, so long runs and follow-ups need durable workflow tools (a Phase 1 item).
4. Supabase storage, auth allowlist, and `web_fetch` for reading sources come after Phase 0 passes.

## Next
- Phase 0 eval after the Vercel link. Then Phase 1: `web_fetch` plus a trust-score tool, Supabase, and durable runs.
