import { defineAgent } from "eve";
import { anthropic } from "eve/models/anthropic";

export default defineAgent({
  // Haiku 5.5 is called directly through Anthropic (needs ANTHROPIC_API_KEY);
  // it is not in the AI Gateway catalog.
  model: anthropic("claude-haiku-5-5"),
  reasoning: "medium",
  // Only the tools in agent/tools/ are exposed. No shell or file access.
  defaultTools: false,
  limits: {
    // Per-run budget, approximating the approved caps (25 searches, 300k tokens, 20 min).
    // Input and output are checked separately, so together they stay within 300k.
    maxInputTokensPerSession: 250_000,
    maxOutputTokensPerSession: 50_000,
    // Note: this is the session lifetime, so a conversation ends 20 minutes after it starts.
    sessionTimeoutMs: 20 * 60 * 1_000,
  },
});
