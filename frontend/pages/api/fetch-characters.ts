export async function fetchCharacters() {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/characters` +
      "?columns=id" +
      "&columns=summary" +
      "&columns=image_url" +
      "&columns=name" +
      "&order_by=data_length" +
      "&asc=false" +
      "&limit=100",
  );

  if (!response.ok) throw new Error("Failed to fetch character data");

  return await response.json();
}
