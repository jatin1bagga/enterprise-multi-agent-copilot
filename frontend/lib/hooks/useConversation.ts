"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { api } from "@/lib/api";
import { streamSse } from "@/lib/sse";
import type {
  AgentStatusEvent,
  ChatTurn,
  FinalPayload,
  Message,
  PlanStep,
  UploadedFile,
} from "@/lib/types";

function newTurn(question: string): ChatTurn {
  return {
    id: crypto.randomUUID(),
    question,
    streamingAnswer: "",
    finalPayload: null,
    plan: [],
    agentStatuses: [],
    isStreaming: true,
    error: null,
  };
}

export function useConversation(conversationId: string) {
  const [history, setHistory] = useState<Message[]>([]);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const refreshFiles = useCallback(async () => {
    setFiles(await api.listFiles(conversationId));
  }, [conversationId]);

  useEffect(() => {
    setIsLoadingHistory(true);
    // History is loaded once on mount; turns sent during this session are tracked
    // (with their plan/agent-trace/artifacts) in `turns` rather than re-fetched, so
    // completed turns don't lose their rich display or get rendered twice.
    Promise.all([api.getMessages(conversationId), api.listFiles(conversationId)])
      .then(([messages, fileList]) => {
        setHistory(messages);
        setFiles(fileList);
      })
      .finally(() => setIsLoadingHistory(false));
  }, [conversationId]);

  const uploadFile = useCallback(
    async (file: File) => {
      setIsUploading(true);
      try {
        await api.uploadFile(conversationId, file);
        await refreshFiles();
      } finally {
        setIsUploading(false);
      }
    },
    [conversationId, refreshFiles],
  );

  const sendMessage = useCallback(
    async (message: string) => {
      const turn = newTurn(message);
      setTurns((prev) => [...prev, turn]);

      const controller = new AbortController();
      abortRef.current = controller;

      const updateTurn = (patch: Partial<ChatTurn>) => {
        setTurns((prev) => prev.map((t) => (t.id === turn.id ? { ...t, ...patch } : t)));
      };

      try {
        for await (const event of streamSse(
          api.chatStreamUrl(conversationId),
          { message },
          controller.signal,
        )) {
          if (event.event === "token") {
            const { content } = event.data as { content: string };
            setTurns((prev) =>
              prev.map((t) =>
                t.id === turn.id ? { ...t, streamingAnswer: t.streamingAnswer + content } : t,
              ),
            );
          } else if (event.event === "plan") {
            const { plan } = event.data as { plan: PlanStep[] };
            updateTurn({ plan });
          } else if (event.event === "agent_status") {
            const status = event.data as AgentStatusEvent;
            setTurns((prev) =>
              prev.map((t) =>
                t.id === turn.id ? { ...t, agentStatuses: [...t.agentStatuses, status] } : t,
              ),
            );
          } else if (event.event === "final") {
            const payload = event.data as FinalPayload;
            updateTurn({ finalPayload: payload, isStreaming: false });
          } else if (event.event === "error") {
            const { message: errorMessage } = event.data as { message: string };
            updateTurn({ error: errorMessage, isStreaming: false });
          }
        }
      } catch (err) {
        updateTurn({ error: err instanceof Error ? err.message : String(err), isStreaming: false });
      } finally {
        updateTurn({ isStreaming: false });
      }
    },
    [conversationId],
  );

  return {
    history,
    files,
    turns,
    isLoadingHistory,
    isUploading,
    uploadFile,
    sendMessage,
  };
}
