"use client";
import React, { useEffect, useState } from "react";
import { Autocomplete, AutocompleteItem, Avatar } from "@nextui-org/react";
import { useRouter } from "next/navigation";

import { SearchIcon } from "@/components/icons";
import { Character } from "@/types";
import { subtitle, title } from "@/components/primitives";

function truncateString(text: string, maxLength: number = 150): string {
  let truncated = text.substring(0, maxLength);

  if (text.length > maxLength) {
    truncated += "...";
  }

  return truncated;
}

export default function Home() {
  const router = useRouter();
  const [characters, setCharacters] = useState<Character[]>();

  useEffect(() => {
    fetch(
      "http://localhost:8080/characters?columns=id&columns=summary&columns=image_url&columns=name&order_by=relevance&limit=100",
    ).then((response) => response.json().then((data) => setCharacters(data)));
  }, []);

  return characters ? (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <div className="inline-block max-w-xl text-center justify-center">
        <span className={title()}>Chat with your&nbsp;</span>
        <span className={title({ color: "yellow" })}>
          favorite NarutoVerse&nbsp;
        </span>
        <span className={title()}>characters!</span>
        <div className={subtitle({ class: "mt-4" })}>
          Beautiful, fast and modern React UI library.
        </div>
      </div>
      <div className="min-w-96 text-center justify-center">
        <Autocomplete
          aria-label="Select a character"
          classNames={{
            base: "max-w-xs",
            listboxWrapper: "max-h-[320px]",
            selectorButton: "text-default-500",
          }}
          defaultItems={characters}
          inputProps={{
            classNames: {
              input: "ml-1",
              inputWrapper: "h-[48px]",
            },
          }}
          listboxProps={{
            hideSelectedIcon: true,
            itemClasses: {
              base: [
                "rounded-medium",
                "text-default-500",
                "transition-opacity",
                "data-[hover=true]:text-foreground",
                "dark:data-[hover=true]:bg-default-50",
                "data-[pressed=true]:opacity-70",
                "data-[hover=true]:bg-default-200",
                "data-[selectable=true]:focus:bg-default-100",
                "data-[focus-visible=true]:ring-default-500",
              ],
            },
          }}
          placeholder="Select a character"
          popoverProps={{
            offset: 10,
            classNames: {
              base: "rounded-large",
              content: "p-1 border-small border-default-100 bg-background",
            },
          }}
          radius="full"
          startContent={
            <SearchIcon
              className="text-default-400"
              size={20}
              strokeWidth={2.5}
            />
          }
          variant="bordered"
        >
          {(character) => (
            <AutocompleteItem
              key={character.id!}
              textValue={character.name}
              onClick={() => {
                router.push(`/chat?characterId=${character.id}`);
              }}
            >
              <div className="flex justify-between items-center">
                <div className="flex gap-2 items-center">
                  <Avatar
                    alt={character.name}
                    className="flex-shrink-0"
                    size="sm"
                    src={character.image_url}
                  />
                  <div className="flex flex-col">
                    <span className="text-small">{character.name}</span>
                    <span className="text-tiny text-default-400">
                      {truncateString(character.summary || "")}
                    </span>
                  </div>
                </div>
              </div>
            </AutocompleteItem>
          )}
        </Autocomplete>
      </div>
    </section>
  ) : (
    <></>
  );
}
