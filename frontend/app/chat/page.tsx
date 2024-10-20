"use client";
import "./styles.css";

import { useSearchParams } from "next/navigation";
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

import useCharacters from "@/hooks/use-characters";
import { SendIcon } from "@/components/icons";
import useWindowSize from "@/hooks/use-window-size";

interface Message {
  sender: string;
  text: string;
}

function generateThreadId() {
  const id = crypto.randomUUID();

  localStorage.setItem("thread_id", id);

  return id;
}
export default function ChatPage() {
  const [message, setMessage] = useState<string>("");
  const [chat, setChat] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const searchParams = useSearchParams();
  const characterId = Number.parseInt(searchParams.get("characterId") || "");
  const characters = useCharacters();
  const windowSize = useWindowSize();

  useEffect(() => {
    const threadId = localStorage.getItem("thread_id") || generateThreadId();

    setThreadId(threadId);
  }, []);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chat]);

  if (!characters) return <div className="loading">Loading</div>;
  const characterData = characters.filter(
    (character) => character.id === characterId,
  )[0];

  const sendMessage = async () => {
    if (!message.trim()) return;
    setLoading(true);

    const newMessage: Message = { sender: "user", text: message.trim() };

    setChat((prevChat) => [...prevChat, newMessage]);
    setMessage(""); // Clear input

    try {
      const response = await fetch("http://localhost:8080/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: newMessage.text,
          character_id: characterId,
          thread_id: threadId,
        }),
      });

      if (response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let done = false;
        let botMessage = "";

        // Add a new placeholder message for the character's response
        const botPlaceholder: Message = {
          sender: characterData.name,
          text: "",
        };

        setChat((prevChat) => [...prevChat, botPlaceholder]);

        while (!done) {
          const { value, done: readerDone } = await reader.read();

          done = readerDone;
          const chunkValue = decoder.decode(value, { stream: !done });

          botMessage += chunkValue;
          setChat((prevChat) => {
            const updatedChat = [...prevChat];

            updatedChat[updatedChat.length - 1].text = botMessage;

            return updatedChat;
          });
        }
      }
    } catch (error) {
      console.error("Error streaming message:", error);
    }
    setLoading(false);
  };

  return (
    <div>
      <Card>
        <CardHeader style={{ backgroundColor: "dimgrey" }}>
          <Avatar
            className="w-14 h-14 text-large"
            src={characterData.image_url}
          />
          <Spacer x={4} />
          <div className={"text-start"}>
            <div className="font-bold">{characterData.name}</div>
            <div>
              {loading ? (
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
              style={{
                backgroundColor:
                  msg.sender === characterData.name ? "dimgrey" : "darkorange",
                maxWidth: "80%",
                alignSelf: msg.sender === characterData.name ? "start" : "end",
                padding: "8px 24px 8px 24px",
                marginBottom: "8px",
                borderRadius: "24px",
              }}
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
