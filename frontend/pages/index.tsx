"use client";
import React from "react";

import Header from "@/components/header";
import CharacterSearch from "@/components/character-search";
import DefaultLayout from "@/layouts/default";

export default function IndexPage() {
  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <Header />
        <CharacterSearch />
      </section>
    </DefaultLayout>
  );
}
