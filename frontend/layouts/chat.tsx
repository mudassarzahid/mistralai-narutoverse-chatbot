import React from "react";

import { Head } from "./head";

import { Navbar } from "@/components/navbar";
import { Footer } from "@/layouts/footer";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex flex-col h-screen">
      <Head />
      <Navbar />
      <main className="container mx-auto max-w-8xl px-6 flex-grow pt-8">
        {children}
      </main>
      <Footer />
    </div>
  );
}
