"use client";

import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";

import { cn } from "@/lib/utils";

interface FileDropzoneProps {
  onFiles: (files: File[]) => void;
  disabled?: boolean;
}

const ACCEPTED = ".pdf,.csv,.xlsx,.xls";

export function FileDropzone({ onFiles, disabled }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-1 rounded-lg border border-dashed p-4 text-center text-sm transition-colors cursor-pointer",
        isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/30",
        disabled && "pointer-events-none opacity-50",
      )}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = Array.from(e.dataTransfer.files);
        if (files.length) onFiles(files);
      }}
    >
      <UploadCloud className="h-5 w-5 text-muted-foreground" />
      <p className="text-muted-foreground">
        Drop PDFs, CSV, or Excel files here, or click to browse
      </p>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        multiple
        className="hidden"
        onChange={(e) => {
          const files = Array.from(e.target.files ?? []);
          if (files.length) onFiles(files);
          e.target.value = "";
        }}
      />
    </div>
  );
}
