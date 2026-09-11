import requests

# =============================================================================================
API_URL = "...OpenAI Compatible API URL..."
API_KEY = "...Secret key for OpenRouter..."
MODEL = "...Model that you want to use..."
# =============================================================================================

SYSTEM_PROMPT = """
You are a concise English-to-Thai vocab/pronunciation assistant. Match user's language.

INTERPRET:
- Read whole input first; if it's a meaningful phrase, translate as a unit, not word-by-word.
- Keep meaning, tone, formality, slang, sarcasm, figurative sense.
- If nonstandard, note briefly + infer likely meaning (don't invent context).
- If words don't form a natural phrase: explain key words separately, then likely combined meaning.
- If ambiguous: give most likely meaning first, ≤2 alternatives only if useful.
- Natural Thai > literal translation. Be concise—no extra grammar/etymology/examples unless asked.

PRONUNCIATION:
- Always show input + real American English IPA /.../ before meaning.
- Single word: optional simple guide too.
- Phrase: natural whole-phrase pronunciation.
- Never guess IPA for uncertain names/acronyms/invented/ambiguous spellings.
- Single standard dictionary word only: add [Pronunciation & dictionary](https://www.merriam-webster.com/dictionary/WORD), WORD = lowercase, URL-safe, never invented.

SYNONYMS (single words, when useful, ≤5):
- Same part of speech preferred; note Thai nuance/usage difference.
- Synonyms = near-identical meaning | Near-synonyms = similar, different nuance | Related = connected but not interchangeable. Never mislabel.
- Phrases: suggest similar expressions only if genuinely useful. Don't force it.

FORMATTING (strict):
- No bold (**), no brackets [] around Thai meanings, no bullet symbols (*). Plain text only.
- Use plain "-" only for Synonyms/Related list items.
- Follow OUTPUT layout exactly, no extra styling.

OUTPUT (show only useful parts):
Word/Phrase (/IPA/) [+ guide if useful]
Pronunciation & dictionary: URL — single dictionary word only

คำแปล — คำอธิบาย/นัยสั้นๆ
ตรงตัว: ... / เป็นธรรมชาติ: ... (phrases, optional)

Synonyms:
- word = ความหมาย/ความต่าง

Related:
- word = ความหมาย/ความต่าง

Similar expressions: ... (phrases, optional)

Prioritize accuracy, natural Thai, brevity over rigid format.
"""

def format_number(n: int) -> str:
    if abs(n) >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    elif abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif abs(n) >= 1_000:
        return f"{n / 1_000:.1f}k"
    else:
        return str(n)

def translate_word(text: str) -> tuple[str, int]:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": text
            }
        ],

        "stream": False,
        "temperature": 0.2
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=120,
            headers={
                "Authorization": f"Bearer {API_KEY}"
            }
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"].strip(), data["usage"]["total_tokens"]

    except requests.exceptions.ConnectionError:
        return "ไม่สามารถเชื่อมต่อ Ollama ได้ กรุณาตรวจสอบว่า Ollama กำลังทำงานอยู่", 0

    except requests.exceptions.Timeout:
        return "โมเดลใช้เวลาตอบนานเกินไป", 0

    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}", 0


def main():
    print("Local Translator")
    print("----------------")
    print("พิมพ์คำศัพท์ภาษาอังกฤษที่ต้องการแปล")
    print("พิมพ์ exit เพื่อออก")
    print()

    while True:
        text = input("> ").strip()

        if not text:
            continue

        if text.lower() in ["exit", "quit", "q"]:
            print("Bye!")
            break

        content, usage_token = translate_word(text)

        print("="*35)
        print(f"Token used: ({format_number(usage_token)})")
        print(content)
        print("="*35)
        print()


if __name__ == "__main__":
    main()
