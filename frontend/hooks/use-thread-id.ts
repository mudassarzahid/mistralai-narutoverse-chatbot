import { useState, useEffect } from "react";

const useThreadId = () => {
  const [threadId, setThreadId] = useState<string | null>(null);

  useEffect(() => {
    try {
      const existingThreadId = localStorage.getItem("thread_id");

      if (existingThreadId) {
        setThreadId(existingThreadId);
      } else {
        const newThreadId = crypto.randomUUID();

        localStorage.setItem("thread_id", newThreadId);
        setThreadId(newThreadId);
      }
    } catch (error) {
      console.error("Error accessing localStorage:", error);
    }
  }, []);

  return threadId;
};

export default useThreadId;
