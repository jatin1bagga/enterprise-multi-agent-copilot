"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .createConversation()
      .then((conversation) => router.replace(`/conversations/${conversation.id}`))
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, [router]);

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-2 p-8 text-center">
      <h1 className="text-xl font-semibold">Enterprise Multi-Agent Operations Copilot</h1>
      {error ? (
        <p className="max-w-md text-sm text-destructive">
          Could not reach the backend at {api.baseUrl}: {error}
        </p>
      ) : (
        <p className="text-sm text-muted-foreground">Starting a new conversation…</p>
      )}
    </div>
  );
}
