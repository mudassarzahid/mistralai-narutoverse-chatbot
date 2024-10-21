export async function fetchCharacter(characterId: number) {
  const response = await fetch(
    `http://localhost:8080/characters/${characterId}`,
  );

  if (!response.ok) throw new Error("Failed to fetch character data");

  return await response.json();
}
