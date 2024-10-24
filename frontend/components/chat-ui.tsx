import React, { useEffect, useRef, useState, useCallback } from "react";
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Avatar,
  Spacer,
  Tooltip,
} from "@nextui-org/react";

import { Character, Message } from "@/types";
import { ResetIcon, SendIcon } from "@/components/icons";
import useWindowSize from "@/hooks/use-window-size";
import { fetchChatHistory } from "@/api/fetch-chat-history";
import { fetchStream } from "@/api/fetch-stream";
import { ChatUiSkeleton } from "@/components/skeletons/chat-ui";
import { Sender } from "@/types/enums";
import { deleteChat } from "@/api/delete-chat";

interface ChatUiProps {
  character: Character;
  threadId: string;
}

export function ChatUi({ character, threadId }: ChatUiProps) {
  const [message, setMessage] = useState<string>("");
  const [chat, setChat] = useState<Message[]>([]);
  const [isWriting, setIsWriting] = useState(false);
  const [loading, setLoading] = useState(true);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const { width, height } = useWindowSize();

  useEffect(() => {
    fetchChatHistory(threadId, Number(character.id)).then((chatHistory) => {
      setChat(chatHistory);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chat]);

  const handleSendMessage = useCallback(async () => {
    if (!message.trim() || isWriting) return;

    setIsWriting(true);
    const newMessage: Message = { sender: Sender.HUMAN, text: message.trim() };

    setChat((prevChat) => [...prevChat, newMessage]);
    setMessage("");

    const characterPlaceholder: Message = { sender: Sender.AI, text: "" };

    setChat((prevChat) => [...prevChat, characterPlaceholder]);

    try {
      const response = await fetchStream(
        threadId,
        newMessage.text,
        character.id,
      );
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let characterMessage = "";
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();

        done = readerDone;

        if (value) {
          const chunk = decoder.decode(value, { stream: true });

          characterMessage += chunk;
          setChat((prevChat) => {
            const updatedChat = [...prevChat];

            updatedChat[updatedChat.length - 1].text = characterMessage;

            return updatedChat;
          });
        }
      }
    } catch (error) {
      console.error("Error streaming message:", error);
    } finally {
      setIsWriting(false);
    }
  }, [message, threadId, character.id]);

  const handleDeleteChat = () => {
    deleteChat(threadId, character.id).then((_) => setChat([]));
  };

  if (loading) return <ChatUiSkeleton />;

  return (
    <div>
      <Card radius="md">
        <CardHeader className="bg-default">
          <Avatar
            isBordered
            className="w-14 h-14 text-large"
            src={character.image_url}
            style={{ borderColor: "green" }}
          />
          <Spacer x={4} />
          <div className="text-start">
            <div className="font-bold">{character.name}</div>
            <div>
              {isWriting ? (
                <span className="loading">Writing</span>
              ) : (
                <span>&nbsp;</span>
              )}
            </div>
          </div>
          <Tooltip
            className="capitalize"
            color="foreground"
            content="Delete chat history"
          >
            <Button
              isIconOnly
              aria-label="Delete"
              className="capitalize ml-auto mr-2"
              variant={"bordered"}
              onClick={handleDeleteChat}
            >
              <ResetIcon />
            </Button>
          </Tooltip>
        </CardHeader>
        <CardBody
          style={{
            height: `${height * 0.6}px`,
            width: `${width * 0.6}px`,
            overflowY: "scroll",
          }}
        >
          {chat.map((msg, index) => (
            <div
              key={index}
              className={`${
                msg.sender === Sender.AI
                  ? "bg-default-200 self-start"
                  : "bg-primary-300 self-end"
              } max-w-full rounded-3xl mb-3 px-4 py-3`}
            >
              <p>{msg.text}</p>
            </div>
          ))}
          <div ref={chatEndRef} />
        </CardBody>
        <CardFooter>
          <Input
            isDisabled={isWriting}
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyUp={(e) =>
              (e.key === "Enter" || e.code === "Enter") && handleSendMessage()
            }
          />
          <Spacer x={2} />
          <Tooltip
            className="capitalize"
            color="foreground"
            content="Send message"
          >
            <Button
              isIconOnly
              aria-label="Send"
              className="bg-content2"
              isDisabled={isWriting}
              onClick={handleSendMessage}
            >
              <SendIcon />
            </Button>
          </Tooltip>
        </CardFooter>
      </Card>
    </div>
  );
}
