export default {
  async fetch(request, env) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Content-Type": "application/json; charset=utf-8"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (request.method !== "POST") {
      return json({ error: "Method not allowed" }, 405, corsHeaders);
    }

    const contentLength = Number(request.headers.get("content-length") || "0");
    if (contentLength > 150000) {
      return json({ error: "Poruka je prevelika." }, 413, corsHeaders);
    }

    if (!env.AI_API_KEY || !env.AI_BASE_URL || !env.AI_MODEL) {
      return json({ error: "AI servis nije podešen na serveru." }, 503, corsHeaders);
    }

    try {
      const body = await request.json();
      if (!body || !Array.isArray(body.messages) || body.messages.length < 1) {
        return json({ error: "Nedostaju poruke." }, 400, corsHeaders);
      }

      const messages = body.messages
        .slice(-20)
        .filter((item) =>
          item &&
          (item.role === "user" || item.role === "assistant") &&
          typeof item.content === "string"
        )
        .map((item) => ({
          role: item.role,
          content: item.content.slice(0, 6000)
        }));

      if (!messages.length || messages[messages.length - 1].role !== "user") {
        return json({ error: "Poslednja poruka mora biti korisnička." }, 400, corsHeaders);
      }

      const endpoint = env.AI_BASE_URL.replace(/\/+$/, "") + "/chat/completions";
      const upstream = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + env.AI_API_KEY,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          model: env.AI_MODEL,
          messages: [
            {
              role: "system",
              content: "Ti si My AI, koristan asistent u aplikaciji WalletCore. Odgovaraj jasno i na jeziku korisnika."
            },
            ...messages
          ],
          temperature: 0.7,
          max_tokens: 1200
        })
      });

      const raw = await upstream.text();
      let data;
      try {
        data = JSON.parse(raw);
      } catch (_) {
        data = null;
      }

      if (!upstream.ok) {
        return json({
          error: data?.error?.message || "AI servis trenutno nije dostupan."
        }, 502, corsHeaders);
      }

      const answer = data?.choices?.[0]?.message?.content;
      if (typeof answer !== "string" || !answer.trim()) {
        return json({ error: "AI servis je vratio prazan odgovor." }, 502, corsHeaders);
      }

      return json({ reply: answer.trim() }, 200, corsHeaders);
    } catch (_) {
      return json({ error: "Greška u komunikaciji sa AI servisom." }, 500, corsHeaders);
    }
  }
};

function json(data, status, headers) {
  return new Response(JSON.stringify(data), { status, headers });
}
