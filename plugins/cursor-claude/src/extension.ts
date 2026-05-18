import * as vscode from "vscode";

interface VerifyResponse {
  verdict: "verified" | "risky" | "blocked";
  attackers: Array<{ vendor: string; model: string; found_issue: boolean; reasoning: string }>;
  signed_hash: string;
  latency_ms: number;
  cost_estimate_usd: number;
}

export function activate(context: vscode.ExtensionContext) {
  const verifyPRCmd = vscode.commands.registerCommand(
    "apohara-probant.verifyPR",
    async () => {
      const diff = await getCurrentDiff();
      if (!diff) {
        vscode.window.showWarningMessage("No git diff found in current workspace.");
        return;
      }
      await runVerification(diff, "Git diff");
    }
  );

  const verifySelectionCmd = vscode.commands.registerCommand(
    "apohara-probant.verifySelection",
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor.");
        return;
      }
      const selection = editor.document.getText(editor.selection);
      if (!selection.trim()) {
        vscode.window.showWarningMessage("No selection. Select code to verify.");
        return;
      }
      await runVerification(selection, "Selection");
    }
  );

  context.subscriptions.push(verifyPRCmd, verifySelectionCmd);
}

async function getCurrentDiff(): Promise<string | null> {
  // Use git CLI via vscode.workspace.workspaceFolders + child_process
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) return null;
  const cwd = folders[0].uri.fsPath;
  return new Promise((resolve) => {
    const { exec } = require("child_process");
    exec("git diff HEAD", { cwd }, (err: Error | null, stdout: string) => {
      resolve(err ? null : stdout);
    });
  });
}

async function runVerification(code: string, sourceName: string) {
  const config = vscode.workspace.getConfiguration("apohara");
  const apiUrl = config.get<string>("apiUrl", "https://api.apohara.dev");
  const geminiKey = config.get<string>("geminiApiKey", "");

  const useDemoKey = !geminiKey;
  const endpoint = useDemoKey ? "/v1/demo_verify" : "/v1/verify";
  const body = useDemoKey
    ? { task_input: code }
    : { task_input: code, gemini_api_key: geminiKey };

  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: `Apohara: verifying ${sourceName}...`,
      cancellable: false,
    },
    async () => {
      try {
        const resp = await fetch(`${apiUrl}${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!resp.ok) {
          vscode.window.showErrorMessage(`Apohara HTTP ${resp.status}`);
          return;
        }
        const data = (await resp.json()) as VerifyResponse;
        displayVerdict(data);
      } catch (e: unknown) {
        vscode.window.showErrorMessage(`Apohara error: ${(e as Error).message}`);
      }
    }
  );
}

function displayVerdict(r: VerifyResponse) {
  const color =
    r.verdict === "verified" ? "✓" : r.verdict === "risky" ? "⚠" : "✕";
  const harmful = r.attackers.filter((a) => a.found_issue).length;
  const total = r.attackers.length;
  const msg = `${color} Apohara: ${r.verdict.toUpperCase()} — ${harmful}/${total} attackers flagged | cost $${r.cost_estimate_usd.toFixed(4)} | latency ${(r.latency_ms / 1000).toFixed(1)}s`;
  if (r.verdict === "verified") vscode.window.showInformationMessage(msg);
  else if (r.verdict === "risky") vscode.window.showWarningMessage(msg);
  else vscode.window.showErrorMessage(msg);

  // Show details in output channel
  const out = vscode.window.createOutputChannel("Apohara PROBANT");
  out.show(true);
  out.appendLine(`=== Verdict: ${r.verdict} (signed_hash: ${r.signed_hash.slice(0, 16)}...) ===`);
  for (const a of r.attackers) {
    const mark = a.found_issue ? "FLAGGED" : "ok";
    out.appendLine(`[${mark}] ${a.vendor}:${a.model}: ${a.reasoning}`);
  }
}

export function deactivate() {}
