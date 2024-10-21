import { fetchData } from "./fetch-utils";

interface ChatIds {
  data: Number[];
}

export async function fetchChatIds(threadId: string): Promise<ChatIds> {
  const url = `${process.env.NEXT_PUBLIC_BACKEND_URL}/chats?thread_id=${threadId}`;

  return await fetchData<ChatIds>(url);
}
