import { fetchData } from "./fetch-utils";

import { Message } from "@/types";

type ChatHistory = Message[];

export async function fetchChatHistory(
  threadId: string,
  characterId: number,
): Promise<ChatHistory> {
  const url =
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/history` +
    `?thread_id=${threadId}` +
    `&character_id=${characterId}`;

  return await fetchData<ChatHistory>(url);
}
