import { defineEval } from "eve/evals";
import { includes } from "eve/evals/expect";

// A niche question: expect thin evidence to be flagged, not asserted confidently.
export default defineEval({
  description: "Thin evidence: says so instead of sounding confident.",
  async test(t) {
    const turn = await t.send("What is the measured effect of drinking water before meals on the weight of residents of one specific village in Bhutan in 1987?");
    t.succeeded();
    t.check(turn.message, includes(/unsupported|insufficient|no reliable|could not find|not found|limited/i));
  },
});
