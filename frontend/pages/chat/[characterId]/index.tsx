import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import { ChatUi } from "@/components/chat-ui";
import { fetchCharacter } from "@/pages/api/fetch-character";
import { Character } from "@/types";
import ChatSidebar from "@/components/chat-sidebar";
import ChatLayout from "@/layouts/chat";
import useThreadId from "@/hooks/use-thread-id";

export default function GetCharacterPage() {
  const router = useRouter();
  const { characterId } = router.query;
  const [character, setCharacter] = useState<Character>();
  const threadId = useThreadId();

  useEffect(() => {
    if (characterId && threadId) {
      fetchCharacter(Number(characterId)).then((data) => {
        setCharacter(data);
      });
    }
  }, [characterId, threadId]);

  return (
    <ChatLayout>
      <section className="flex flex-col items-center justify-center">
        <div className="inline-block text-center justify-center">
          {character && threadId && (
            <div className={"flex max-h-min"}>
              <ChatSidebar characterId={character.id} threadId={threadId} />
              <ChatUi characterData={character} />
            </div>
          )}
        </div>
      </section>
    </ChatLayout>
  );
}
