import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import DefaultLayout from "@/layouts/default";
import { ChatUi } from "@/pages/chat/[characterId]/chat-ui";
import { fetchCharacter } from "@/pages/api/fetch-character";
import { Character } from "@/types";

export default function GetCharacterPage() {
  const router = useRouter();
  const { characterId } = router.query;
  const [character, setCharacter] = useState<Character>();
  const [threadId, setThreadId] = useState<string>();

  useEffect(() => {
    const threadId = localStorage.getItem("thread_id") || crypto.randomUUID();

    setThreadId(threadId);
    localStorage.setItem("thread_id", threadId);
  }, []);

  useEffect(() => {
    if (characterId) {
      fetchCharacter(Number(characterId)).then((data) => {
        setCharacter(data);
      });
    }
  }, [characterId]);

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center">
        <div className="inline-block text-center justify-center">
          {character && threadId && (
            <ChatUi characterData={character} threadId={threadId} />
          )}
        </div>
      </section>
    </DefaultLayout>
  );
}