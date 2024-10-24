// components/character-search.tsx
import { Autocomplete, AutocompleteItem, Avatar } from "@nextui-org/react";
import React, { useMemo } from "react";
import { useRouter } from "next/navigation";
import { Link } from "@nextui-org/link";

import { SearchIcon } from "./icons";

import useCharacters from "@/hooks/use-characters";
import { Character } from "@/types";

function truncateString(text: string, maxLength: number = 150): string {
  return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
}

export function CharacterSearch() {
  const router = useRouter();
  const characters = useCharacters();

  const characterItems = useMemo(
    () =>
      (characters || []).map((character: Character) => (
        <AutocompleteItem
          key={character.id.toString()}
          textValue={character.name}
        >
          <Link
            key={character.id.toString()}
            color={"foreground"}
            href={`/chat/${character.id}`}
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
          </Link>
        </AutocompleteItem>
      )),
    [characters, router],
  );

  return (
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
        {characterItems}
      </Autocomplete>
    </div>
  );
}
