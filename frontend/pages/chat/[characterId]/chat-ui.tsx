"use client";
import React, { useEffect, useRef, useState } from "react";
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Avatar,
  Spacer,
} from "@nextui-org/react";
import { Character, Message } from "@/types";
import { SendIcon } from "@/components/icons";
import useWindowSize from "@/hooks/use-window-size";
import "./styles.css";

interface ChatUiProps {
  characterData: Character;
  threadId: string;
}

export function ChatUi({ characterData, threadId }: ChatUiProps) {
  const [message, setMessage] = useState<string>("");
  const [chat, setChat] = useState<Message[]>([]);
  const [isWriting, setIsWriting] = useState(false);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const windowSize = useWindowSize();

  useEffect(() => {
    if (chat.length === 0) {
      setLoading(true);
    }
    fetch(
      `http://localhost:8080/chat/history?thread_id=${threadId}&character_id=${characterData.id}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      },
    ).then((res) =>
      res.json().then((data) => {
        console.log(data);
        setChat(data);
      }),
    );
  }, []);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chat]);

  const sendMessage = async () => {
    console.log(chat);
    if (!message.trim()) return;

    setIsWriting(true);
    const newMessage: Message = { sender: "user", text: message.trim() };

    setChat((prevChat) => [...prevChat, newMessage]);
    setMessage("");

    const characterPlaceholder: Message = {
      sender: "bot",
      text: "",
    };

    setChat((prevChat) => [...prevChat, characterPlaceholder]);

    try {
      const response = await fetch("http://localhost:8080/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: newMessage.text,
          character_id: characterData.id,
          thread_id: threadId,
        }),
      });

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let characterMessage = "";
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();

        done = readerDone;

        if (value) {
          // Update messages with each incoming chunk
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
  };

  return (
    <div>
      <Card>
        <CardHeader className={"bg-default"}>
          <Avatar
            isBordered
            className="w-14 h-14 text-large"
            src={characterData.image_url}
          />
          <Spacer x={4} />
          <div className={"text-start"}>
            <div className="font-bold">{characterData.name}</div>
            <div>
              {isWriting ? (
                <span className="loading">Writing</span>
              ) : (
                <span>&nbsp;</span>
              )}
            </div>
          </div>
        </CardHeader>
        <CardBody
          style={{
            height: `${windowSize.height * 0.6}px`,
            width: `${windowSize.width * 0.6}px`,
            overflowY: "scroll",
          }}
        >
          {chat.map((msg, index) => (
            <div
              key={index}
              className={`${
                msg.sender === "bot"
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
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyUp={(e) =>
              (e.key === "Enter" || e.code === "Enter") && sendMessage()
            }
          />
          <Spacer x={2} />
          <Button isIconOnly aria-label="Like" onClick={sendMessage}>
            <SendIcon />
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
