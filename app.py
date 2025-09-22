import os
from io import BytesIO
from typing import Dict
from datetime import datetime
import json
from pathlib import Path
from collections import defaultdict

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

try:
	from openai import OpenAI
except ImportError:  # graceful message if SDK missing at runtime
	OpenAI = None  # type: ignore

try:
	from gtts import gTTS
except ImportError:
	gTTS = None  # type: ignore


app = Flask(__name__)
CORS(app)


NEED_TO_SENTENCE: Dict[str, str] = {
	"water": "Su istiyorum.",
	"food": "Açım.",
	"toilet": "Tuvalete gitmem gerekiyor.",
	"doctor": "Doktora ihtiyacım var.",
	"nurse": "Hemşireye ihtiyacım var.",
	"pain": "Ağrım var.",
	"sleep": "Uyumak istiyorum.",
	"medicine": "İlaçlarımı istiyorum.",
	"help": "Yardım eder misiniz?",
	"blanket": "Üşüyorum, battaniye istiyorum.",
	"hot": "Sıcakladım, serinlemek istiyorum.",
	"cold": "Üşüyorum, oda sıcaklığını artırabilir miyiz?",
	"position": "Pozisyonumu değiştirmenizi istiyorum.",
	"bathroom": "Banyoya gitmek istiyorum.",
	"wash_hands": "Ellerimi yıkamak istiyorum.",
	"call_family": "Ailemi aramak istiyorum.",
	"phone": "Telefonumu istiyorum.",
	"wheelchair": "Tekerlekli sandalyeye geçmek istiyorum.",
	"open_window": "Pencereyi açabilir misiniz?",
	"close_window": "Pencereyi kapatabilir misiniz?",
	"music": "Müzik açabilir misiniz?",
	"tv": "Televizyonu açabilir misiniz?",
	"yes": "Evet.",
	"no": "Hayır.",
	"thanks": "Teşekkür ederim.",
}

# Accept both Turkish and English inputs
NEED_ALIASES: Dict[str, str] = {
	"water": "water",
	"su": "water",
	"food": "food",
	"yemek": "food",
	"toilet": "toilet",
	"tuvalet": "toilet",
	"doctor": "doctor",
	"doktor": "doctor",
	"nurse": "nurse",
	"hemşire": "nurse",
	"hemsire": "nurse",
	"pain": "pain",
	"ağrı": "pain",
	"agri": "pain",
	"sleep": "sleep",
	"uyku": "sleep",
	"ilaç": "medicine",
	"ilac": "medicine",
	"medicine": "medicine",
	"yardım": "help",
	"yardim": "help",
	"help": "help",
	"battaniye": "blanket",
	"blanket": "blanket",
	"sıcak": "hot",
	"sicak": "hot",
	"hot": "hot",
	"soğuk": "cold",
	"soguk": "cold",
	"cold": "cold",
	"pozisyon": "position",
	"position": "position",
	"banyo": "bathroom",
	"bathroom": "bathroom",
	"eller": "wash_hands",
	"el": "wash_hands",
	"wash": "wash_hands",
	"wash_hands": "wash_hands",
	"aile": "call_family",
	"family": "call_family",
	"call_family": "call_family",
	"telefon": "phone",
	"phone": "phone",
	"tekerlekli sandalye": "wheelchair",
	"sandalyeye": "wheelchair",
	"wheelchair": "wheelchair",
	"pencereyi aç": "open_window",
	"pencere aç": "open_window",
	"open_window": "open_window",
	"pencereyi kapa": "close_window",
	"pencere kapa": "close_window",
	"close_window": "close_window",
	"müzik": "music",
	"muzik": "music",
	"music": "music",
	"tv": "tv",
	"televizyon": "tv",
	"evet": "yes",
	"yes": "yes",
	"hayır": "no",
	"hayir": "no",
	"no": "no",
	"teşekkürler": "thanks",
	"tesekkurler": "thanks",
	"teşekkür": "thanks",
	"thanks": "thanks",
}


def synthesize_speech(text: str, *, lang: str = "tr", slow: bool = False, voice: str | None = None, force_gtts: bool = False, gender: str | None = None) -> bytes:
	"""Generate MP3 audio bytes from text.

	Preference order:
	1) OpenAI TTS if OPENAI_API_KEY is set and SDK available
	2) gTTS (Google Text-to-Speech) fallback with no API key required
	"""
	api_key = os.getenv("OPENAI_API_KEY")

	# Try OpenAI if allowed and SDK/key present
	if (not force_gtts) and api_key and OpenAI is not None:
		try:
			client = OpenAI(api_key=api_key)
			with client.audio.speech.with_streaming_response.create(
				model="gpt-4o-mini-tts",
				voice=voice or "alloy",
				input=text,
				format="mp3",
			) as response:
				buf = BytesIO()
				response.stream_to_file(buf)  # type: ignore[attr-defined]
				return buf.getvalue()
		except Exception:
			# Fall back to gTTS below
			pass

	# Fallback to gTTS (no API key needed)
	if gTTS is None:
		raise RuntimeError(
			"No TTS available: install openai or gTTS. Try: pip install gTTS"
		)
	buf = BytesIO()
	# gTTS'te cinsiyet/seviye yok; sabit hızda oku
	gTTS(text=text, lang=lang, slow=False).write_to_fp(buf)
	return buf.getvalue()


def _log_event(payload: Dict) -> None:
	"""Append anonymized speak event to logs/events.jsonl"""
	try:
		log_dir = Path("logs")
		log_dir.mkdir(parents=True, exist_ok=True)
		payload_with_time = {**payload, "ts": datetime.utcnow().isoformat() + "Z"}
		with open(log_dir / "events.jsonl", "a", encoding="utf-8") as f:
			f.write(json.dumps(payload_with_time, ensure_ascii=False) + "\n")
	except Exception:
		# Logging failures should not break main flow
		pass


@app.post("/speak")
def speak():
	data = request.get_json(silent=True) or {}

	# Options
	lang = str(data.get("lang", "tr")).strip().lower() or "tr"
	slow = False
	voice_value = data.get("voice")
	voice = str(voice_value) if isinstance(voice_value, str) and voice_value.strip() else None
	category = str(data.get("category", "")).strip().lower() or None
	provider = str(data.get("provider", "")).strip().lower()
	force_gtts = (provider == "gtts")
	gender = str(data.get("gender", "")).strip().lower() or None

	# Either direct text or need mapping
	text_value = data.get("text")
	if isinstance(text_value, str) and text_value.strip():
		sentence = text_value.strip()
		need = None
	else:
		need_input = str(data.get("need", "")).strip().lower()
		need = NEED_ALIASES.get(need_input, need_input)
		if need not in NEED_TO_SENTENCE:
			return jsonify({
				"error": "Geçersiz ihtiyaç",
				"allowed": list(sorted(set(list(NEED_TO_SENTENCE.keys()) + list(NEED_ALIASES.keys())))),
			}), 400
		sentence = NEED_TO_SENTENCE[need]

	try:
		audio_bytes = synthesize_speech(sentence, lang=lang, slow=slow, voice=voice, force_gtts=force_gtts, gender=gender)
	except Exception as e:
		return jsonify({"error": str(e)}), 500

	# best-effort logging (non-blocking)
	_log_event({
		"category": category,
		"need": need,
		"text": sentence if need is None else None,
		"lang": lang,
		"slow": slow,
		"voice": voice,
		"provider": provider or ("gtts" if force_gtts else None),
		"gender": gender,
	})

	# Return as audio/mpeg stream
	return send_file(
		BytesIO(audio_bytes),
		mimetype="audio/mpeg",
		as_attachment=False,
		download_name=f"{(need or 'custom')}.mp3",
	)


@app.get("/stats")
def stats():
	"""Return simple usage counts by need or custom text for recent events."""
	limit = int(request.args.get("limit", "500"))
	log_file = Path("logs") / "events.jsonl"
	counts: Dict[str, int] = {}
	if log_file.exists():
		lines = log_file.read_text(encoding="utf-8").splitlines()
		for line in lines[-limit:]:
			try:
				evt = json.loads(line)
				key = evt.get("need") or evt.get("text") or "unknown"
				counts[key] = counts.get(key, 0) + 1
			except Exception:
				continue
	return jsonify({"counts": counts})


@app.get("/speak_text")
def speak_text_get():
	"""Convenience endpoint to speak arbitrary text via gTTS: /speak_text?text=...&lang=tr&slow=false

	Always uses gTTS (free) to minimize setup friction for local demos.
	"""
	text = request.args.get("text", "").strip()
	if not text:
		return jsonify({"error": "text query param is required"}), 400
	lang = (request.args.get("lang") or "tr").strip().lower()
	slow_str = (request.args.get("slow") or "false").strip().lower()
	slow = slow_str in ("1", "true", "yes", "on")

	try:
		audio_bytes = synthesize_speech(text, lang=lang, slow=slow, force_gtts=True)
	except Exception as e:
		return jsonify({"error": str(e)}), 500

	return send_file(
		BytesIO(audio_bytes),
		mimetype="audio/mpeg",
		as_attachment=False,
		download_name="speech.mp3",
	)


@app.get("/stats_daily")
def stats_daily():
	"""Return usage counts grouped by day (UTC) and need/text for the last N days.

	Query params:
	- days: number of days to include (default 7)
	- limit: max lines to read from the end of log (default 5000)
	"""
	days = int(request.args.get("days", "7"))
	limit = int(request.args.get("limit", "5000"))
	end_date = datetime.utcnow().date()
	start_date = end_date.fromordinal(end_date.toordinal() - (days - 1))

	log_file = Path("logs") / "events.jsonl"
	counts_by_day = defaultdict(lambda: defaultdict(int))  # day -> key -> count

	if log_file.exists():
		lines = log_file.read_text(encoding="utf-8").splitlines()
		for line in lines[-limit:]:
			try:
				evt = json.loads(line)
				ts = evt.get("ts")
				if not ts:
					continue
				# ts like 2025-09-22T10:10:10Z
				day_str = ts[:10]
				day = datetime.strptime(day_str, "%Y-%m-%d").date()
				if day < start_date or day > end_date:
					continue
				key = evt.get("need") or evt.get("text") or "unknown"
				counts_by_day[day_str][key] += 1
			except Exception:
				continue

	# ensure all days exist in output
	ordered = {}
	for i in range(days):
		d = start_date.fromordinal(start_date.toordinal() + i)
		ordered[d.strftime("%Y-%m-%d")] = counts_by_day.get(d.strftime("%Y-%m-%d"), {})

	return jsonify({
		"range": {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")},
		"daily": ordered,
	})


@app.get("/health")
def health():
	return jsonify({"status": "ok"})


if __name__ == "__main__":
	port = int(os.getenv("PORT", "5000"))
	app.run(host="0.0.0.0", port=port, debug=True)


