import { webSearch } from "eve/tools/web_search";

// Direct Anthropic models use Anthropic's native web search.
export default webSearch({ provider: "native" });
