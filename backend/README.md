# My AI backend (Cloudflare Worker)

WalletCore ne sadrži AI API ključ. Aplikacija šalje poruke ovom Worker-u, a Worker poziva AI provajdera koristeći ključ koji je sačuvan kao Cloudflare secret.

## Postavljanje

1. U Cloudflare Dashboard-u otvori **Workers & Pages** i napravi novi Worker.
2. Kopiraj sadržaj fajla `backend/my_ai_worker.js` u Worker editor i sačuvaj/deploy.
3. U Worker-u otvori **Settings → Variables and Secrets** i dodaj:
   - Secret `AI_API_KEY`: novi API ključ provajdera. Nemoj koristiti ključ koji je ranije bio javno objavljen.
   - Variable `AI_BASE_URL`: OpenAI-compatible API base URL, bez završnog `/chat/completions` (na primer URL provajdera koji koristiš).
   - Variable `AI_MODEL`: tačan naziv modela koji je omogućen na tvom nalogu.
4. U Cloudflare-u podesi rate limiting za Worker da drugi ne bi mogli da potroše tvoj API limit.
5. Kopiraj Worker URL i upiši ga kao `AI_API_URL` u `components/my_ai_config.py`, pa sačuvaj izmenu u GitHub-u.
6. Pokreni workflow **WalletCore Test APK** iz GitHub Actions i instaliraj testni APK.

## Važno

- Nikada ne stavljaj AI API ključ u WalletCore, Python fajlove, GitHub commit ili APK.
- CORS nije autentifikacija; zato podesi rate limiting i prati upotrebu API-ja.
- Worker prihvata poruke poslednjih 20 poruka razgovora i ograničava tekst svake poruke.
- Dok `AI_API_URL` nije podešen, aplikacija će prikazati poruku da servis još nije konfigurisan.
