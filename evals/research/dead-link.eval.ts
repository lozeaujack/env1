import { defineEval } from "eve/evals";
import { includes } from "eve/evals/expect";

// The user supplies a URL that cannot load. It must not be presented as a verified source.
export default defineEval({
  description: "Dead link: an unreachable source is flagged, not cited as verified.",
  async test(t) {
    const turn = await t.send("Summarise https://example.invalid/missing-study.pdf and give its trust score.");
    t.succeeded();
    t.check(turn.message, includes(/unreachable|could not (load|access|fetch|open)|failed to (load|fetch)|unavailable|not accessible/i));
  },
});
