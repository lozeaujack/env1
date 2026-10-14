# Research agent: plan status

## Status
- **Phase 0 (plumbing): done, except the live model call.**
  - eve project scaffolded (`npx eve init . --non-interactive`), eve 0.79.1, Node 24.
  - `agent/instructions.md`, `agent/agent.ts`, `agent/tools/web_search.ts` written.
  - `npx tsc` passes. `npx eve build` passes. `eve dev --no-ui` serves sessions and streams events.
  - `eve eval`: 5 of 5 cases fail, all with `MODEL_CALL_FAILED: The model connection is unavailable`. Cause: no `ANTHROPIC_API_KEY`. The failures are not agent-behavior results.
- **Phase 0 eval (you):** set `ANTHROPIC_API_KEY`, rerun `npx eve eval`, then judge the answers.

## Decisions
- Model: Haiku 5.5 via `anthropic("claude-haiku-5-5")`, calling Anthropic directly. It is not in eve's AI Gateway catalog.
- Search: `webSearch({ provider: "native" })`, which is Anthropic's own web search for direct Anthropic models. eve's other search providers (Exa, Parallel, Browserbase) only work through AI Gateway models.
- Default tools off (`defaultTools: false`): no shell, file, or fetch tools.
- Limits: 250k input and 50k output tokens per session. Session lifetime 20 minutes. Note: this also ends follow-up conversations after 20 minutes.
- Sandbox: eve requires one at build time, so `just-bash` is installed as a devDependency. The agent never calls it.
- Evals: five cases in `evals/research/`: known fact, contested, thin evidence, fabrication trap, dead link.

## Open questions
1. Provide an Anthropic API key for local dev and for the deployment environment. Do not commit it.
2. Search budget: 25 searches per run is written in the instructions but not enforced in code. Enforcing it needs a counting wrapper around search.
3. Session timeout vs. run time: the 20-minute limit ends a session, so long runs and follow-ups need durable workflow tools (a Phase 1 item).
4. Supabase storage, auth allowlist, and `web_fetch` for reading sources come after Phase 0 passes.

## Next
- Phase 0 eval with a key. Then Phase 1: `web_fetch` plus a trust-score tool, Supabase, and durable runs.
