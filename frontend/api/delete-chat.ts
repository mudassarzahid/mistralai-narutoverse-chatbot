import { fetchData } from "./fetch-utils";

type AcceptedResponse = {};

export async function deleteChat(
  threadId: string,
  characterId: Number,
): Promise<AcceptedResponse> {
  const url = `${process.env.NEXT_PUBLIC_BACKEND_URL}/chats/${threadId}/${characterId}`;

  return await fetchData<AcceptedResponse>(url, {
    method: "DELETE",
  });
}
