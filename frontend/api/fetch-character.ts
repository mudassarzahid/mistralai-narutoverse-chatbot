import { fetchData } from "./fetch-utils";

import { Character } from "@/types";

export async function fetchCharacter(characterId: number): Promise<Character> {
  return await fetchData<Character>(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/characters/${characterId}`,
  );
}
