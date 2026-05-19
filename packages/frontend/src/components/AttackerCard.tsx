import { AlertTriangle, CheckCircle2, Loader2, MinusCircle } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { AttackerResult, Vendor } from "@/lib/types";

const placeholderReasoning =
  "Awaiting verification — attacker has not yet probed the submission.";

export interface AttackerCardProps {
  vendor: Vendor;
  result?: AttackerResult;
}

export function AttackerCard({ vendor, result }: AttackerCardProps) {
  const status = result?.status ?? "pending";
  const reasoning = result?.reasoning ?? placeholderReasoning;
  const snippet = reasoning.length > 80 ? `${reasoning.slice(0, 80)}…` : reasoning;
  const foundIssue = result?.found_issue === true;
  const isLoading = status === "pending" || status === "running";

  return (
    <Card
      className={cn(
        "h-full transition-colors rounded-none",
        status === "running" && "ring-2 ring-primary/30 animate-pulse-lime",
        status === "ok" && foundIssue && "border-destructive/40",
        status === "ok" && !foundIssue && "border-primary/40",
        status === "error" && "border-destructive/60",
        // fail_open = vendor inactive in this credential pool. Visually
        // neutral (muted border + dim text) so it reads as "documented
        // gap" not "broken system" — see JUDGE-FAQ Q1.
        status === "fail_open" && "border-border/40 opacity-70",
      )}
    >
      <CardHeader className="flex-row items-start justify-between space-y-0 gap-2">
        <div className="flex items-start gap-2 min-w-0">
          <Badge
            variant="outline"
            className="h-8 w-8 shrink-0 rounded-md font-mono justify-center"
            aria-hidden="true"
          >
            {vendor.badge}
          </Badge>
          <div className="min-w-0">
            <CardTitle className="truncate text-sm">{vendor.name}</CardTitle>
            <CardDescription className="truncate">
              via {vendor.gateway}
            </CardDescription>
          </div>
        </div>
        <StatusIndicator
          status={status}
          foundIssue={foundIssue}
          aria-label={
            isLoading
              ? `${vendor.name} is running`
              : foundIssue
                ? `${vendor.name} flagged an issue`
                : `${vendor.name} found no issue`
          }
        />
      </CardHeader>

      <CardContent className="pt-0">
        {isLoading ? (
          <div className="space-y-2" aria-busy="true">
            <div className="skeleton h-3 w-full rounded" />
            <div className="skeleton h-3 w-5/6 rounded" />
            <div className="skeleton h-3 w-3/4 rounded" />
          </div>
        ) : (
          <p className="text-xs leading-relaxed text-muted-foreground">
            {snippet}
          </p>
        )}
        {result?.latency_ms !== undefined && (
          <p className="mt-2 text-[10px] font-mono text-muted-foreground">
            {result.latency_ms.toLocaleString()} ms
          </p>
        )}
      </CardContent>
    </Card>
  );
}

function StatusIndicator({
  status,
  foundIssue,
  ...props
}: {
  status: AttackerResult["status"];
  foundIssue: boolean;
} & React.HTMLAttributes<HTMLSpanElement>) {
  if (status === "pending" || status === "running") {
    return (
      <span
        {...props}
        className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-muted text-muted-foreground"
      >
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
      </span>
    );
  }

  if (status === "error") {
    return (
      <span
        {...props}
        className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-destructive/20 text-destructive"
      >
        <AlertTriangle className="h-3.5 w-3.5" />
      </span>
    );
  }

  if (status === "fail_open") {
    return (
      <span
        {...props}
        className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-muted/40 text-muted-foreground"
      >
        <MinusCircle className="h-3.5 w-3.5" />
      </span>
    );
  }

  if (foundIssue) {
    return (
      <span
        {...props}
        className="inline-flex h-3 w-3 items-center justify-center rounded-full bg-destructive shadow-[0_0_0_3px_hsl(var(--destructive)/0.2)] mt-1.5 mr-1.5"
      />
    );
  }

  return (
    <span
      {...props}
      className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-primary/20 text-primary"
    >
      <CheckCircle2 className="h-3.5 w-3.5" />
    </span>
  );
}
