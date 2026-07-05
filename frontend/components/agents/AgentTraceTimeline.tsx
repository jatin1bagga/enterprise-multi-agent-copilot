import { CheckCircle2, CircleDashed, Loader2, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { AgentStatusEvent, PlanStep } from "@/lib/types";

const AGENT_LABELS: Record<string, string> = {
  rag: "Document Search",
  data_analysis: "Data Analysis",
  python_exec: "Python Execution",
  report: "Report Generation",
  forecast: "Forecasting",
  mail: "Email Delivery",
};

function latestStatusFor(agent: string, statuses: AgentStatusEvent[]): string | null {
  for (let i = statuses.length - 1; i >= 0; i--) {
    if (statuses[i].agent === agent) return statuses[i].status;
  }
  return null;
}

function StatusIcon({ planStatus, liveStatus }: { planStatus: PlanStep["status"]; liveStatus: string | null }) {
  if (planStatus === "done") return <CheckCircle2 className="h-4 w-4 text-green-600" />;
  if (planStatus === "failed") return <XCircle className="h-4 w-4 text-destructive" />;
  if (liveStatus === "retrying_or_failed") return <Loader2 className="h-4 w-4 animate-spin text-amber-500" />;
  if (liveStatus) return <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />;
  return <CircleDashed className="h-4 w-4 text-muted-foreground" />;
}

export function AgentTraceTimeline({
  plan,
  agentStatuses,
}: {
  plan: PlanStep[];
  agentStatuses: AgentStatusEvent[];
}) {
  if (plan.length === 0) return null;

  return (
    <div className="flex flex-col gap-2 rounded-md border bg-muted/30 p-3">
      <p className="text-xs font-medium text-muted-foreground">Execution plan</p>
      <ul className="flex flex-col gap-2">
        {plan.map((step) => {
          const liveStatus = latestStatusFor(step.agent, agentStatuses);
          return (
            <li key={step.step_id} className="flex items-start gap-2 text-sm">
              <StatusIcon planStatus={step.status} liveStatus={liveStatus} />
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{AGENT_LABELS[step.agent] ?? step.agent}</Badge>
                </div>
                <span className="text-xs text-muted-foreground">{step.instruction}</span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
