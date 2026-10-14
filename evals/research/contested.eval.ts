import { defineEval } from "eve/evals";
import { includes } from "eve/evals/expect";

// A contested question: expect the disagreement to be stated, not hidden.
export default defineEval({
  description: "Contested question: disagreement between sources is stated.",
  async test(t) {
    const turn = await t.send("Does a low-carb diet beat a low-fat diet for long-term weight loss? Give sources and trust scores.");
    t.succeeded();
    t.check(turn.message, includes(/disagree|conflict|mixed|contested|uncertain/i));
  },
});
