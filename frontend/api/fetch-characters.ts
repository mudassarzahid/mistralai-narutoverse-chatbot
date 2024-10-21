import { fetchData } from "./fetch-utils";

import { Character } from "@/types";

export async function fetchCharacters(): Promise<Character[]> {
  const url =
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/characters` +
    "?columns=id" +
    "&columns=summary" +
    "&columns=image_url" +
    "&columns=name" +
    "&order_by=data_length" +
    "&asc=false" +
    "&limit=100";

  return await fetchData<Character[]>(url);
}
