import { useState, useEffect, useRef } from "react";

// Define the Character type (you can replace this with your actual Character definition)
type Character = {
  id: number;
  name: string;
  summary: string;
  image_url: string;
};

const useCharacters = () => {
  const [characters, setCharacters] = useState<Character[] | null>(null);
  const fetched = useRef(false); // To track if the data has already been fetched

  useEffect(() => {
    // Fetch data only if it hasn't been fetched before
    if (!fetched.current) {
      fetched.current = true;
      fetch(
        "http://localhost:8080/characters?columns=id&columns=summary&columns=image_url&columns=name&order_by=data_length&asc=false&limit=100",
      )
        .then((response) => response.json())
        .then((data) => setCharacters(data))
        .catch((error) => {
          console.error("Error fetching characters:", error);
        });
    }
  }, []); // Empty dependency array ensures the effect runs only once

  return characters;
};

export default useCharacters;
