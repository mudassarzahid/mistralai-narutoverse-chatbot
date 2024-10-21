import React, { useEffect } from "react";
import { Listbox, ListboxItem, Avatar } from "@nextui-org/react";

import { fetchChatIds } from "@/api/fetch-chat-ids";
import useCharacters from "@/hooks/use-characters";
import ChatSidebarSkeleton from "@/components/skeletons/chat-sidebar";

interface ChatSidebarProps {
  threadId: string;
  characterId: string;
}

export default function ChatSidebar({
  threadId,
  characterId,
}: ChatSidebarProps) {
  const [filteredChats, setFilteredChats] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const characters = useCharacters();

  useEffect(() => {
    if (characters) {
      fetchChatIds(threadId).then((chatIds) => {
        setFilteredChats(
          characters.filter((character) =>
            [...chatIds.data, Number(characterId)].includes(character.id),
          ),
        );
        setLoading(false);
      });
    }
  }, [characters]);

  if (loading) return <ChatSidebarSkeleton />;

  return (
    <div className="w-full max-w-[260px] max-h-[100%] border-small px-2 mx-2 border-content1 bg-content1 rounded-xl">
      <Listbox
        classNames={{
          base: "max-w-xs p-0 gap-0 rounded-md max-h-full",
          list: "overflow-scroll",
        }}
        defaultSelectedKeys={[1]}
        items={filteredChats}
        label={"Chats"}
        selectionMode="single"
        topContent={
          <div className="font-bold text-start self-start py-4 px-3 bg-content1 min-w-full rounded-md mb-2">
            Chats
          </div>
        }
        variant="faded"
      >
        {(character) => (
          <ListboxItem
            key={character.id}
            hideSelectedIcon
            shouldHighlightOnFocus
            href={`/chat/${character.id}`}
            isDisabled={character.id === Number(characterId)}
            textValue={character.name}
          >
            <div className="flex gap-2 items-center">
              <Avatar
                alt={character.name}
                className="flex-shrink-0"
                size="sm"
                src={character.image_url}
              />
              <div className="flex flex-col">
                <span className="text-small text-start">{character.name}</span>
              </div>
            </div>
          </ListboxItem>
        )}
      </Listbox>
    </div>
  );
}
