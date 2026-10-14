import { defineEval } from "eve/evals";
import { includes } from "eve/evals/expect";

// A settled question: expect at least one URL, and a trust score.
export default defineEval({
  description: "Settled fact: answer includes source URLs and trust scores.",
  async test(t) {
    const turn = await t.send("Is the Earth's average surface temperature rising? Give sources and trust scores.");
    t.succeeded();
    t.check(turn.message, includes(/https?:\/\//));
    t.check(turn.message, includes(/trust score|score/i));
  },
});
