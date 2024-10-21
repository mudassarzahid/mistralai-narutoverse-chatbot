import { Card, Skeleton } from "@nextui-org/react";
import React from "react";

import { getRandomWidthClass } from "@/components/skeletons/common";

const ChatSkeleton = () => {
  return (
    <div className="max-w-[300px] w-full flex items-center gap-3">
      <div>
        <Skeleton className="flex rounded-full w-8 h-8" />
      </div>
      <div className="w-full flex flex-col gap-2">
        <Skeleton className={`h-3 ${getRandomWidthClass()} rounded-lg`} />
      </div>
    </div>
  );
};

export default function ChatSidebarSkeleton() {
  return (
    <Card className="w-[200px] space-y-5 p-4 mx-2" radius="lg">
      <div className="font-bold text-start self-start mb-2">Chats</div>
      <div className="space-y-4">
        <ChatSkeleton />
        <ChatSkeleton />
        <ChatSkeleton />
      </div>
    </Card>
  );
}
