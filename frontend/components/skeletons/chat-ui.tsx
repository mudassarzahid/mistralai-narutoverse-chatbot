import React from "react";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Spacer,
  Skeleton,
} from "@nextui-org/react";

import { getRandomWidthClass } from "@/components/skeletons/common";
import useWindowSize from "@/hooks/use-window-size";

export function ChatUiSkeleton() {
  const windowSize = useWindowSize();

  return (
    <div>
      <Card radius={"md"}>
        <CardHeader className={"bg-default"}>
          <Skeleton className="flex rounded-full w-14 h-14" />
          <Spacer x={4} />
          <Skeleton className={`h-3 ${getRandomWidthClass()} rounded-lg`} />
        </CardHeader>
        <CardBody
          style={{
            height: `${windowSize.height * 0.6}px`,
            width: `${windowSize.width * 0.6}px`,
            overflowY: "scroll",
          }}
        >
          <Spacer y={2} />
          <Skeleton className="w-2/5 rounded-2xl p-3 self-end">
            <div className="h-3 w-full rounded-lg bg-secondary-200" />
          </Skeleton>
          <Spacer x={4} />
          <Skeleton className="w-2/5 rounded-2xl p-3 self-start">
            <div className="h-12 w-full rounded-lg bg-secondary-200" />
          </Skeleton>
        </CardBody>
        <CardFooter>
          <Skeleton className="w-full rounded-lg p-3">
            <div className="h-3 w-full rounded-lg bg-secondary-200" />
          </Skeleton>
          <Spacer x={1} />
          <Skeleton className="w-10 rounded-lg p-3">
            <div className="h-3 w-full rounded-lg bg-secondary-200" />
          </Skeleton>
        </CardFooter>
      </Card>
    </div>
  );
}
