export async function fetchCharacter(characterId: number) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/characters/${characterId}`,
  );

  if (!response.ok) throw new Error("Failed to fetch character data");

  return await response.json();
}
