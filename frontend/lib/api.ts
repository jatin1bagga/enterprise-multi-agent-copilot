import type { ArtifactRef, Conversation, Message, UploadedFile } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Request failed (${res.status}): ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  baseUrl: API_BASE,

  createConversation(title = "New conversation"): Promise<Conversation> {
    return fetch(`${API_BASE}/api/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    }).then((res) => json<Conversation>(res));
  },

  listConversations(): Promise<Conversation[]> {
    return fetch(`${API_BASE}/api/conversations`).then((res) => json<Conversation[]>(res));
  },

  getMessages(conversationId: string): Promise<Message[]> {
    return fetch(`${API_BASE}/api/conversations/${conversationId}/messages`).then((res) =>
      json<Message[]>(res),
    );
  },

  listFiles(conversationId: string): Promise<UploadedFile[]> {
    return fetch(`${API_BASE}/api/conversations/${conversationId}/files`).then((res) =>
      json<UploadedFile[]>(res),
    );
  },

  uploadFile(conversationId: string, file: File): Promise<UploadedFile> {
    const formData = new FormData();
    formData.append("file", file);
    return fetch(`${API_BASE}/api/conversations/${conversationId}/files`, {
      method: "POST",
      body: formData,
    }).then((res) => json<UploadedFile>(res));
  },

  listArtifacts(conversationId: string): Promise<ArtifactRef[]> {
    return fetch(`${API_BASE}/api/artifacts/conversations/${conversationId}`).then((res) =>
      json<ArtifactRef[]>(res),
    );
  },

  artifactDownloadUrl(artifactId: string): string {
    return `${API_BASE}/api/artifacts/${artifactId}/download`;
  },

  chatStreamUrl(conversationId: string): string {
    return `${API_BASE}/api/conversations/${conversationId}/chat`;
  },
};
