# Communication Bridge – MVP

Basit ihtiyaçlar için ikon tabanlı TTS iletişim aracı.

## Özellikler
- 6 büyük ikon: Su, Yemek, Tuvalet, Doktor, Ağrı, Uyku
- Flask backend `/speak` ucu: `{ "need": "water" }` ile MP3 döner
- OpenAI TTS (gpt-4o-mini-tts) ile seslendirme
- Basit HTML/CSS/JS arayüz, anında oynatma

## Kurulum

1) Python 3.10+

2) Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

3) Ortam değişkeni ayarla:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "YOUR_API_KEY"
```

4) Backend'i çalıştır:
```bash
python backend/app.py
```

5) Frontend'i aç:
- `frontend/index.html` dosyasını tarayıcıda açın.
- Yerelde backend `http://localhost:5000` beklenir.

## API

POST `/speak`
- Girdi JSON: `{ "need": "water" }`
- Çıktı: `audio/mpeg` MP3 akışı
- Geçerli değerler: `water, food, toilet, doctor, pain, sleep`

Sağlık: GET `/health` → `{ "status": "ok" }`

## Notlar
- CORS açık. Demo için uygundur.
- Ses modeli ve `voice` değeri ihtiyaca göre değiştirilebilir.
