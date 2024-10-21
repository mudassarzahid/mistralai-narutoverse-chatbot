import { useState, useEffect, useRef } from "react";

import { Character } from "@/types";
import { fetchCharacters } from "@/pages/api/fetch-characters";

const useCharacters = () => {
  const [characters, setCharacters] = useState<Character[] | null>(null);
  const fetched = useRef(false);

  useEffect(() => {
    // Fetch data only if it hasn't been fetched before
    if (!fetched.current) {
      fetched.current = true;
      fetchCharacters().then((data) => setCharacters(data));
    }
  }, []);

  return characters;
};

export default useCharacters;
