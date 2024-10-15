"use client";
import React, { useEffect, useState } from "react";

import { Character } from "@/types";
import Header from "@/components/header";
import CharacterSearch from "@/components/character-search";

export default function Home() {
  const [characters, setCharacters] = useState<Character[]>();

  useEffect(() => {
    fetch(
      "http://localhost:8080/characters?columns=id&columns=summary&columns=image_url&columns=name&order_by=relevance&limit=100",
    ).then((response) => response.json().then((data) => setCharacters(data)));
  }, []);

  return characters ? (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <Header />
      <CharacterSearch characters={characters} />
    </section>
  ) : (
    <></>
  );
}
