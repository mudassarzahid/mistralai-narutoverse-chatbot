import React from "react";

import { title, subtitle } from "@/components/primitives";

interface HeaderProps {
  titleText?: string;
  highlightText?: string;
  subtitleText?: string;
}

export function Header({
  titleText = "Chat with your",
  highlightText = "favorite NarutoVerse",
  subtitleText = "MistralAI-powered Chatbots",
}: HeaderProps) {
  return (
    <div className="inline-block max-w-xl text-center justify-center">
      <span className={title()}>{titleText}&nbsp;</span>
      <span className={title({ color: "yellow" })}>{highlightText}&nbsp;</span>
      <span className={title()}>characters!</span>
      <div className={subtitle({ class: "mt-4" })}>{subtitleText}</div>
    </div>
  );
}
