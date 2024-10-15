"use client";
import { useSearchParams } from "next/navigation";
import React from "react";
import { Button, Image, Input } from "@nextui-org/react";

import { title } from "@/components/primitives";
import useCharacters from "@/hooks/use-characters";
import { SendIcon } from "@/components/icons";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const characterId = Number.parseInt(searchParams.get("characterId") || "");
  const characters = useCharacters();

  if (!characters) return <div>Loading...</div>;

  const characterData = characters.filter(
    (character) => character.id === characterId,
  )[0];

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <span className={title({ size: "md" })}>Chat with&nbsp;</span>
      <span className={title({ size: "md", color: "yellow" })}>
        {characterData.name}
      </span>
      <Image
        isBlurred
        alt={characterData.name}
        className="m-4"
        src={characterData.image_url}
        width={240}
      />
      <Input
        endContent={
          <Button isIconOnly aria-label="Like">
            <SendIcon />
          </Button>
        }
        label="Message"
        type="Write a message"
        variant={"bordered"}
      />
    </div>
  );
}
