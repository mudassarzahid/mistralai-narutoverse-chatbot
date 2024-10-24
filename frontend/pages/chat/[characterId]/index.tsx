import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import { Character } from "@/types";
import { ChatUi } from "@/components/chat-ui";
import ChatSidebar from "@/components/chat-sidebar";
import ChatLayout from "@/layouts/chat";
import useThreadId from "@/hooks/use-thread-id";
import { fetchCharacter } from "@/api/fetch-character";
import useWindowSize from "@/hooks/use-window-size";

export default function ChatWithCharacterPage() {
  const router = useRouter();
  const { characterId } = router.query;
  const [character, setCharacter] = useState<Character>();
  const threadId = useThreadId();
  const { deviceType } = useWindowSize();

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
            <div className="flex max-h-min">
              {deviceType !== "mobile" && (
                <ChatSidebar characterId={character.id} threadId={threadId} />
              )}
              <ChatUi characterData={character} />
            </div>
          )}
        </div>
      </section>
    </ChatLayout>
  );
}
