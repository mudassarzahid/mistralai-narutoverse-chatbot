export async function fetchStream(
  threadId: string,
  query: string,
  characterId: string,
) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/stream`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        character_id: characterId,
        thread_id: threadId,
      }),
    },
  );

  if (!response.body) {
    throw new Error("No response body");
  }

  return response;
}
