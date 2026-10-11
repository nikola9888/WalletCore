export default {
  async fetch(request, env) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (request.method !== "POST") {
      return json({ error: "Method not allowed." }, 405, corsHeaders);
    }

    if (!env.AI_API_KEY || !env.AI_MODEL) {
      return json({ error: "AI servis nije podešen na serveru." }, 503, corsHeaders);
    }

    try {
      const rawBody = await request.text();
      if (new TextEncoder().encode(rawBody).length > 30000) {
        return json({ error: "Zahtev je prevelik." }, 413, corsHeaders);
      }

      let body;
      try {
        body = JSON.parse(rawBody);
      } catch (_) {
        return json({ error: "Neispravan JSON zahtev." }, 400, corsHeaders);
      }

      if (!body || !Array.isArray(body.messages) || body.messages.length < 1) {
        return json({ error: "Nedostaju poruke." }, 400, corsHeaders);
      }

      const messages = body.messages
        .slice(-12)
        .filter((item) =>
          item &&
          (item.role === "user" || item.role === "assistant") &&
          typeof item.content === "string" &&
          item.content.trim().length > 0
        )
        .map((item) => ({
          role: item.role,
          content: item.content.slice(0, 4000)
        }));

      if (!messages.length || messages[messages.length - 1].role !== "user") {
        return json({ error: "Poslednja poruka mora biti korisnička." }, 400, corsHeaders);
      }

      const baseUrl = (env.AI_BASE_URL || "https://api.groq.com/openai/v1")
        .replace(/\/+$/, "");
      const upstream = await fetch(baseUrl + "/chat/completions", {
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
              content: "Ti si My AI, koristan asistent u aplikaciji WalletCore. Odgovaraj jasno, sažeto i na jeziku korisnika. Ne tvrdi da možeš da vidiš slike, slušaš audio ili izvršavaš radnje ako ti te mogućnosti nisu dostupne u konkretnom razgovoru."
            },
            ...messages
          ],
          temperature: 0.7,
          max_tokens: 1000
        }),
        signal: AbortSignal.timeout(40000)
      });

      if (!upstream.ok) {
        // Do not return provider details or secrets to the public client.
        return json({ error: "Groq trenutno nije dostupan. Pokušaj ponovo kasnije." }, 502, corsHeaders);
      }

      const data = await upstream.json();
      const answer = data?.choices?.[0]?.message?.content;
      if (typeof answer !== "string" || !answer.trim()) {
        return json({ error: "AI servis nije vratio tekstualni odgovor." }, 502, corsHeaders);
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
