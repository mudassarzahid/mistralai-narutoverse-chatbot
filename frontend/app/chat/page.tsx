"use client";
import { useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Avatar,
} from "@nextui-org/react";

import useCharacters from "@/hooks/use-characters";
import { SendIcon } from "@/components/icons";
interface Message {
  user: string;
  message: string;
}

export default function ChatPage() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [message, setMessage] = useState<string>("");
  const [chat, setChat] = useState<Message[]>([]);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8080/ws");

    setWs(socket);

    socket.onmessage = (event: MessageEvent) => {
      const newMessage: Message = JSON.parse(event.data);

      setChat((prev) => [...prev, newMessage]);
    };

    return () => {
      socket.close();
    };
  }, []);

  const sendMessage = () => {
    if (ws && message.trim()) {
      const userMessage: Message = { user: "You", message };

      setChat((prev) => [...prev, userMessage]);
      ws.send(JSON.stringify({ message }));
      setMessage("");
    }
  };

  const searchParams = useSearchParams();
  const characterId = Number.parseInt(searchParams.get("characterId") || "");
  const characters = useCharacters();

  if (!characters) return <div>Loading...</div>;

  const characterData = characters.filter(
    (character) => character.id === characterId,
  )[0];

  return (
    <div>
      <Card className={"min-w-96"}>
        <CardHeader>
          <Avatar
            className="w-14 h-14 text-large"
            src={characterData.image_url}
          />
          <p className="italic ...">Chat with {characterData.name}</p>
        </CardHeader>
        <CardBody>
          <div
            style={{
              minHeight: "200px",
              maxHeight: "300px",
              overflowY: "scroll",
            }}
          >
            {chat.map((msg, index) => (
              <p key={index} className="text-small">
                <strong>{msg.user}:</strong> {msg.message}
              </p>
            ))}
          </div>
        </CardBody>
        <CardFooter>
          <Input
            isClearable
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <Button isIconOnly aria-label="Like" onClick={sendMessage}>
            <SendIcon />
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
