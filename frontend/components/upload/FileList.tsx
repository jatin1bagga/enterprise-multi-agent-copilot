import { FileSpreadsheet, FileText, Loader2, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { UploadedFile } from "@/lib/types";

function fileIcon(fileType: string) {
  if (fileType === "pdf") return <FileText className="h-4 w-4 shrink-0" />;
  return <FileSpreadsheet className="h-4 w-4 shrink-0" />;
}

function statusBadge(status: UploadedFile["status"]) {
  if (status === "ingested") return <Badge variant="secondary">ready</Badge>;
  if (status === "failed")
    return (
      <Badge variant="destructive" className="gap-1">
        <XCircle className="h-3 w-3" /> failed
      </Badge>
    );
  return (
    <Badge variant="outline" className="gap-1">
      <Loader2 className="h-3 w-3 animate-spin" /> processing
    </Badge>
  );
}

export function FileList({ files }: { files: UploadedFile[] }) {
  if (files.length === 0) {
    return <p className="text-xs text-muted-foreground">No files uploaded yet.</p>;
  }

  return (
    <ul className="flex flex-col gap-2">
      {files.map((file) => (
        <li key={file.id} className="flex items-center gap-2 text-sm">
          {fileIcon(file.file_type)}
          <span className="truncate flex-1" title={file.filename}>
            {file.filename}
          </span>
          {statusBadge(file.status)}
        </li>
      ))}
    </ul>
  );
}
