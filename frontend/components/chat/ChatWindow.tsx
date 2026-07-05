"use client";

import { useEffect, useRef } from "react";
import { AlertCircle } from "lucide-react";

import { AgentTraceTimeline } from "@/components/agents/AgentTraceTimeline";
import { ArtifactViewer } from "@/components/artifacts/ArtifactViewer";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ChatTurn, Message } from "@/lib/types";

export function ChatWindow({ history, turns }: { history: Message[]; turns: ChatTurn[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history.length, turns]);

  const isEmpty = history.length === 0 && turns.length === 0;

  return (
    <ScrollArea className="flex-1">
      <div className="flex flex-col gap-4 p-4">
        {isEmpty && (
          <p className="mx-auto mt-16 max-w-sm text-center text-sm text-muted-foreground">
            Upload PDFs, CSV, or Excel files, then ask a question to get started.
          </p>
        )}

        {history.map((message) => (
          <MessageBubble key={message.id} role={message.role === "user" ? "user" : "assistant"}>
            {message.content}
          </MessageBubble>
        ))}

        {turns.map((turn) => (
          <div key={turn.id} className="flex flex-col gap-2">
            <MessageBubble role="user">{turn.question}</MessageBubble>

            <AgentTraceTimeline plan={turn.plan} agentStatuses={turn.agentStatuses} />

            <MessageBubble role="assistant">
              {turn.finalPayload?.content ?? turn.streamingAnswer}
            </MessageBubble>

            {turn.error && (
              <div className="flex items-center gap-2 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4 shrink-0" />
                {turn.error}
              </div>
            )}

            {turn.finalPayload && turn.finalPayload.artifacts.length > 0 && (
              <ArtifactViewer artifacts={turn.finalPayload.artifacts} />
            )}
          </div>
        ))}

        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
