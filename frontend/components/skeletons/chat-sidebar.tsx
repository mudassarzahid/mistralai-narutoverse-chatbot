import { Card, Skeleton } from "@nextui-org/react";
import React from "react";

import { getRandomWidthClass } from "@/components/skeletons/common";

const ChatSkeleton = () => {
  return (
    <div className="max-w-[300px] w-full flex items-center gap-3">
      <Skeleton className="flex rounded-full w-8 h-8" />
      <div className="w-full flex flex-col gap-2">
        <Skeleton className={`h-3 ${getRandomWidthClass()} rounded-lg`} />
      </div>
    </div>
  );
};

interface ChatSidebarSkeletonProps {
  skeletonCount?: number;
}

export default function ChatSidebarSkeleton({
  skeletonCount = 3,
}: ChatSidebarSkeletonProps) {
  return (
    <Card className="w-[200px] space-y-5 p-4 mx-2" radius="lg">
      <div className="font-bold text-start self-start mb-2">Chats</div>
      <div className="space-y-4">
        {Array.from({ length: skeletonCount }).map((_, idx) => (
          <ChatSkeleton key={idx} />
        ))}
      </div>
    </Card>
  );
}
