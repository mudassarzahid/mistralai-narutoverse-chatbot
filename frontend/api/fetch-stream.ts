export async function fetchStream(
  threadId: string,
  query: string,
  characterId: Number,
): Promise<Response> {
  const url = `${process.env.NEXT_PUBLIC_BACKEND_URL}/chats/stream`;
  const options: RequestInit = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      character_id: characterId,
      thread_id: threadId,
    }),
  };

  const response = await fetch(url, options);

  if (!response.body) {
    throw new Error("No response body");
  }

  return response;
}
