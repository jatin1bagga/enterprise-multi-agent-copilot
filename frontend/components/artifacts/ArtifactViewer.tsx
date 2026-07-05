import { Download, FileArchive, FileText, ImageIcon, Table } from "lucide-react";

import { buttonVariants } from "@/components/ui/button";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ArtifactRef } from "@/lib/types";

function artifactIcon(type: string) {
  if (type === "plot") return <ImageIcon className="h-4 w-4" />;
  if (type === "table") return <Table className="h-4 w-4" />;
  if (type.startsWith("report")) return <FileArchive className="h-4 w-4" />;
  return <FileText className="h-4 w-4" />;
}

export function ArtifactViewer({ artifacts }: { artifacts: ArtifactRef[] }) {
  if (artifacts.length === 0) return null;

  return (
    <div className="flex flex-col gap-3">
      {artifacts.map((artifact) => {
        const url = api.artifactDownloadUrl(artifact.id);
        const isImage = artifact.mime_type.startsWith("image");

        return (
          <div key={artifact.id} className="flex flex-col gap-2 rounded-md border p-2">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-sm font-medium">
                {artifactIcon(artifact.type)}
                {artifact.title}
              </div>
              <a
                href={url}
                download
                className={cn(buttonVariants({ variant: "ghost", size: "sm" }))}
              >
                <Download className="h-4 w-4" />
              </a>
            </div>
            {isImage && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={url} alt={artifact.title} className="max-h-80 w-auto rounded border object-contain" />
            )}
          </div>
        );
      })}
    </div>
  );
}
