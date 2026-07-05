"use client";

import { useParams } from "next/navigation";
import { toast } from "sonner";

import { ChatInput } from "@/components/chat/ChatInput";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { FileDropzone } from "@/components/upload/FileDropzone";
import { FileList } from "@/components/upload/FileList";
import { useConversation } from "@/lib/hooks/useConversation";

export default function ConversationPage() {
  const params = useParams<{ id: string }>();
  const conversationId = params.id;

  const { history, files, turns, isLoadingHistory, isUploading, uploadFile, sendMessage } =
    useConversation(conversationId);

  const isBusy = turns.some((t) => t.isStreaming);

  const handleFiles = async (incoming: File[]) => {
    for (const file of incoming) {
      try {
        await uploadFile(file);
        toast.success(`${file.name} uploaded`);
      } catch (err) {
        toast.error(`Failed to upload ${file.name}: ${err instanceof Error ? err.message : err}`);
      }
    }
  };

  return (
    <div className="flex h-screen">
      <aside className="hidden w-72 shrink-0 flex-col gap-4 border-r p-4 md:flex">
        <div>
          <h2 className="mb-2 text-sm font-semibold">Operations Copilot</h2>
          <p className="text-xs text-muted-foreground">
            Upload PDFs, CSV, or Excel files, then ask questions. The planner will decide which
            specialist agents to use.
          </p>
        </div>
        <FileDropzone onFiles={handleFiles} disabled={isUploading} />
        <FileList files={files} />
      </aside>

      <main className="flex flex-1 flex-col">
        {isLoadingHistory ? (
          <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
            Loading conversation…
          </div>
        ) : (
          <ChatWindow history={history} turns={turns} />
        )}
        <ChatInput onSend={sendMessage} disabled={isBusy} />
      </main>
    </div>
  );
}
