export async function fetchChatIds(threadId: string) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/chats` + `?thread_id=${threadId}`,
  );

  if (!response.ok) throw new Error("Failed to fetch character data");

  return await response.json();
}
