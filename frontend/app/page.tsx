"use client";
import React, { useEffect, useState } from "react";
import {
  Autocomplete,
  AutocompleteItem,
  Avatar,
  Button,
} from "@nextui-org/react";

import { SearchIcon } from "@/components/icons";
import { Character } from "@/types";

export default function Home() {
  const [characters, setCharacters] = useState<Character[]>();

  useEffect(() => {
    fetch(
      "http://localhost:8080/characters?columns=id&columns=summary&columns=image_url",
    ).then((response) => response.json().then((data) => setCharacters(data)));
  }, []);

  return characters ? (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <div className="w-max text-center justify-center">
        <Autocomplete
          aria-label="Select an employee"
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
          placeholder="Enter employee name"
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
            <AutocompleteItem key={character.id!} textValue={character.name}>
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
                      {character.summary}
                    </span>
                  </div>
                </div>
                <Button
                  className="border-small mr-0.5 font-medium shadow-small"
                  radius="full"
                  size="sm"
                  variant="bordered"
                >
                  Add
                </Button>
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
