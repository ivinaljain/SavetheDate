from dotenv import load_dotenv
import os
# os.chdir("/mnt/e/Projects/Vinal-hackathon")
# Load environment variables from .env file
load_dotenv()
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",  # or your deployment
    api_version="2023-12-01-preview",  # or your api version
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=4,
    # other params...
)

"""
event_poster_analyser.py
────────────────────────
• Sends an image to GPT‑4‑o (or any vision‑capable model)
• Expects a strict JSON reply defined by StructuredOutputParser
• Auto‑fixes malformed JSON (OutputFixingParser)
• Auto‑retries the whole call up to N times (RetryOutputParser)
No optional imports – runs on old or new LangChain releases.
"""

import base64, json, traceback
from pathlib import Path

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate   # ← always available

from langchain.output_parsers import (
    ResponseSchema,
    StructuredOutputParser,
    OutputFixingParser,
    RetryOutputParser,
)

# ───────────────────────── vision LLM ─────────────────────────
llm = llm

# ───────────────────── JSON schema & parsers ──────────────────
schemas = [
    ResponseSchema(name="is_valid_event_poster",
                   description="true if the image shows a legitimate event poster, false otherwise"),
    ResponseSchema(name="justification",
                   description="One‑sentence rationale"),
    ResponseSchema(name="event_name",
                   description="Event name or null"),
    ResponseSchema(name="event_datetime_iso",
                   description="Event date‑time ISO‑8601 or null"),
]

base_parser  = StructuredOutputParser.from_response_schemas(schemas)
fix_parser   = OutputFixingParser.from_llm(parser=base_parser,  llm=llm)
retry_parser = RetryOutputParser.from_llm(  parser=fix_parser, llm=llm, max_retries=2)
FORMAT = base_parser.get_format_instructions()

# ─────────────────── helper: file → data‑URL ─────────────────
def to_data_url(img_path: str | Path) -> str:
    img_path = Path(img_path)
    mime = f"image/{img_path.suffix.lstrip('.') or 'png'}"
    data = base64.b64encode(img_path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"

# ─────────────────── main analyse routine ────────────────────
def analyse_event_poster(image_path: str | Path) -> dict:
    try:
        # 1. craft the chat messages
        data_url = to_data_url(image_path)
        system_msg = SystemMessage(content="You are an AI assistant that analyses event posters., todays date is 20 April 2025")
        human_msg  = HumanMessage(
            content=[
                {"type": "text",
                 "text": f"{FORMAT}\n\nAnalyse the image below and respond:"},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]
        )
        messages = [system_msg, human_msg]

        # 2. turn messages → PromptValue WITHOUT importing ChatPromptValue
        prompt_value = ChatPromptTemplate.from_messages(messages).format_prompt()

        # 3. call the model
        raw_output = llm(messages).content

        # 4. parse / auto‑fix / auto‑retry
        return retry_parser.parse_with_prompt(raw_output, prompt_value)

    except Exception as exc:
        return {
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }
# ───────────────────── quick CLI test ───────────────────────
if __name__ == "__main__":
    test_path = "/mnt/e/Projects/Vinal-hackathon/user_image_2.png"   # change as needed
    result = analyse_event_poster(test_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def create_event_ics(result: dict,
                     filename: str = "event.ics",
                     default_duration_minutes: int = 60) -> bool:
    from datetime import datetime, timedelta, timezone
    from pathlib import Path

    if str(result.get("is_valid_event_poster", "")).lower() != "true":
        return False

    start_dt = datetime.fromisoformat(result["event_datetime_iso"])
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(minutes=default_duration_minutes)

    # formatter
    zfmt = "%Y%m%dT%H%M%SZ"
    def z(dt): return dt.astimezone(timezone.utc).strftime(zfmt)

    ical_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//EventPosterParser 1.0//EN",
        "METHOD:PUBLISH",                        # <-- NEW
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:{int(start_dt.timestamp())}@eventposter",
        f"DTSTAMP:{z(datetime.utcnow())}",
        f"DTSTART:{z(start_dt)}",
        f"DTEND:{z(end_dt)}",
        f"SUMMARY:{result.get('event_name','Untitled Event')}",
        "END:VEVENT",
        "END:VCALENDAR"
    ]

    # Write with CRLF endings
    Path(filename).write_text("\r\n".join(ical_lines) + "\r\n",
                              encoding="utf-8")
    return True
