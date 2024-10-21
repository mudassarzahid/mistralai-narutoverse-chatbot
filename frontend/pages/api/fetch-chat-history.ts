export async function fetchChatHistory(threadId: string, characterId: number) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/history` +
      `?thread_id=${threadId}` +
      `&character_id=${characterId}`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) throw new Error("Failed to fetch character data");

  return await response.json();
}
