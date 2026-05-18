/**
 * SSE streaming client for POST /v1/verify_stream (US-T2-D).
 *
 * EventSource does not natively support POST, so we use fetch +
 * ReadableStream + manual SSE parsing (blank-line delimited frames).
 */

export interface StreamEvent {
  event: string;
  data: unknown;
}

/**
 * verifyStream — async generator that yields one StreamEvent per SSE frame.
 *
 * Typical event sequence:
 *   gemini_complete     — writer returned
 *   vendor_started (×9) — attacker probes dispatched
 *   vendor_completed    — one per attacker as each resolves
 *   all_done            — aggregated verdict (payload === /v1/verify JSON)
 *
 * On DPI block:
 *   blocked_at_dpi + all_done (verdict: "blocked")
 *
 * On auth/upstream error:
 *   error               — {code, detail}
 */
export async function* verifyStream(
  apiUrl: string,
  body: { task_input: string; gemini_api_key?: string },
  signal?: AbortSignal,
): AsyncGenerator<StreamEvent> {
  const resp = await fetch(`${apiUrl}/v1/verify_stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!resp.ok || !resp.body) {
    let detail = `HTTP ${resp.status}`;
    try {
      const text = await resp.text();
      if (text) detail += `: ${text}`;
    } catch {
      // ignore read error
    }
    throw new Error(detail);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE events are separated by a blank line ("\n\n").
    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);

      const lines = raw.split("\n");
      let event = "message";
      let dataStr = "";

      for (const line of lines) {
        if (line.startsWith("event:")) {
          event = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          dataStr += line.slice(5).trim();
        }
      }

      let data: unknown;
      try {
        data = JSON.parse(dataStr);
      } catch {
        data = dataStr;
      }

      yield { event, data };
    }
  }
}
