import { webSearch } from "eve/tools/web_search";

// AI Gateway models use Exa for search.
export default webSearch({ provider: "exa" });
