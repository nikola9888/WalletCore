# My AI backend — Groq preko Cloudflare Workers

WalletCore šalje poruke Cloudflare Worker-u. Worker poziva Groq API. Groq API ključ ostaje kao Worker secret i nikada se ne ugrađuje u aplikaciju ili GitHub.

## 1. Objavi Worker

1. Otvori Cloudflare Dashboard → **Workers & Pages**.
2. Napravi novi Worker (na primer `walletcore-my-ai`).
3. Otvori uređivač koda i zameni sadržaj fajlom `backend/my_ai_worker.js` iz ovog repozitorijuma.
4. Sačuvaj i izaberi **Deploy**.

## 2. Podesi Groq

U Worker-u otvori **Settings → Variables and Secrets** i dodaj:

- **Secret** `AI_API_KEY`: novi Groq API ključ.
- **Variable** `AI_MODEL`: tačan naziv modela koji je dostupan na tvom Groq nalogu.
- Opcionalno, **Variable** `AI_BASE_URL`: `https://api.groq.com/openai/v1`. Ako se izostavi, Worker koristi tu adresu automatski.

Nemoj koristiti ranije javno objavljene API ključeve. Ako je neki ključ ikada bio u javnom Pastebin-u, GitHub-u ili poruci koja je deljena, opozovi ga i napravi novi.

## 3. Ograniči zloupotrebu pre povezivanja aplikacije

Worker endpoint je dostupan preko javnog URL-a, pa čuvanje Groq ključa kao secret-a samo po sebi ne sprečava druge da pozivaju endpoint. U Cloudflare-u podesi rate limiting pravilo za Worker rutu, sa ograničenjem zahteva po IP adresi, i prati potrošnju/limit na Groq nalogu. Nemoj se oslanjati na CORS kao zaštitu — to nije autentifikacija. Za javno izdanje aplikacije treba dodati jaču kontrolu zloupotrebe, npr. korisničku autentifikaciju i server-side kvote.

## 4. Poveži WalletCore

1. Kopiraj javni URL Worker-a (na primer `https://walletcore-my-ai.<tvoj-nalog>.workers.dev`).
2. U `components/my_ai_config.py` postavi taj URL kao `AI_API_URL`.
3. Sačuvaj izmenu u GitHub-u.
4. Pokreni **WalletCore Test APK** workflow u GitHub Actions i testiraj razgovor.

Dok URL nije upisan, My AI će javiti da backend nije podešen.

## Trenutni obim

Ova verzija podržava tekstualne poruke i poslednjih 12 poruka konteksta, uz ograničenje veličine zahteva i dužine poruka. Slike, glas i druge funkcije dodaju se kasnije kao zasebna proširenja API-ja; trenutno ih ne prikazujemo kao podržane.

## Bezbednost

- Nikada ne stavljaj Groq API ključ u Python fajlove, APK, GitHub commit ili poruke.
- Ne stavljaj Cloudflare API token ili bilo koji admin ključ u aplikaciju.
- Rate limiting je obavezan za javni endpoint. Ograničenja modela i potrošnje treba proveriti na Groq nalogu.
