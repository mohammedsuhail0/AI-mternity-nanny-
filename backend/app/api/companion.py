from __future__ import annotations

import logging
import re

import httpx
from fastapi import APIRouter

from app.api.schemas import CompanionChatRequest, CompanionChatResponse
from app.core.config import get_settings


router = APIRouter(prefix="/companion", tags=["companion"])
settings = get_settings()
logger = logging.getLogger(__name__)


EMERGENCY_PATTERNS = (
    r"bleeding",
    r"severe pain",
    r"chest pain",
    r"shortness of breath",
    r"faint",
    r"contraction.*(every|minute)",
    r"baby.*not moving",
    r"headache.*vision",
)


ROADMAP_STAGES = (
    ("First steps", "Confirm care, medicines, and nutrition plan.", "foundation"),
    ("Early checks", "Blood pressure, nausea, and early screening.", "check-in"),
    ("Growth phase", "Track baby growth, movement, and fetal heart rate.", "watch"),
    ("Delivery prep", "Hospital plan, warning signs, and birth preferences.", "finish"),
)

SYSTEM_PROMPT = (
    "You are a warm, patient-first medical companion for general health, human body, pregnancy, and prenatal care. "
    "Answer directly like a human clinician or care coach. Do not sound generic, templated, or like a preset FAQ. "
    "Use plain language, keep replies short and natural, and answer the user's exact question first. "
    "Only use bullet points if they clearly help the answer. If the user describes emergency symptoms, tell them to seek urgent care immediately. "
    "Never mention that you are an AI model. Do not reveal reasoning, analysis, or hidden thoughts. "
    "Return only the final answer the patient should see."
)

EMERGENCY_ACTION_LABEL = "Call emergency now"
EMERGENCY_ACTION_URL = "tel:911"


def _clean_llm_reply(content: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<think>.*", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = cleaned.strip()
    return cleaned


def _build_context_block(payload: CompanionChatRequest) -> str:
    lines: list[str] = []

    if payload.journey:
        journey_bits = ["Current pregnancy journey context:"]
        if payload.journey.stage_title:
            journey_bits.append(f"- Stage: {payload.journey.stage_title}")
        if payload.journey.stage_label:
            journey_bits.append(f"- Timeline: {payload.journey.stage_label}")
        if payload.journey.stage_detail:
            journey_bits.append(f"- Guidance: {payload.journey.stage_detail}")
        lines.append("\n".join(journey_bits))

    if payload.attachments:
        attachment_lines = ["Attached files or notes:"]
        for attachment in payload.attachments[:5]:
            attachment_lines.append(f"- {attachment.name}")
            if attachment.content:
                attachment_lines.append(attachment.content[:3000])
        lines.append("\n".join(attachment_lines))

    if payload.history:
        history_lines = ["Recent conversation:"]
        for turn in payload.history:
            history_lines.append(f"{turn.role}: {turn.content}")
        lines.append("\n".join(history_lines))

    return "\n\n".join(lines).strip()


def _suggested_prompts_for(message: str) -> list[str]:
    normalized = message.lower().strip()

    if any(word in normalized for word in ["medicine", "medication", "pill", "tablet", "dose"]):
        return [
            "Is this medicine usually used in pregnancy?",
            "What side effects should I watch for?",
            "Can I take over-the-counter pain relief?",
        ]

    if any(word in normalized for word in ["eat", "diet", "food", "nutrition", "meal"]):
        return [
            "What are good breakfast ideas in pregnancy?",
            "What foods should I avoid?",
            "How much water should I drink?",
        ]

    if any(word in normalized for word in ["exercise", "workout", "walk", "movement", "activity", "yoga"]):
        return [
            "What exercise is safe in the first trimester?",
            "Can I keep walking every day?",
            "What signs mean I should stop exercising?",
        ]

    if any(word in normalized for word in ["report", "result", "scan", "ultrasound", "fhr", "heartbeat", "blood pressure"]):
        return [
            "What does a fetal heart rate mean?",
            "What blood pressure numbers are concerning?",
            "How do I understand a pregnancy report?",
        ]

    if any(word in normalized for word in ["roadmap", "journey", "progress", "track", "health"]):
        return [
            "How healthy does my journey look?",
            "What stage am I in now?",
            "What should I watch for this week?",
        ]

    return [
        "What should I eat today?",
        "Is this symptom normal?",
        "How do I understand my report?",
    ]


def _build_emergency_response() -> CompanionChatResponse:
    return CompanionChatResponse(
        reply=(
            "This could be urgent. Please contact your maternity care team or emergency services now, "
            "especially if the bleeding, pain, breathing trouble, or reduced baby movement is new or worsening."
        ),
        safety_note="Emergency symptoms should be assessed by your care team right away.",
        suggested_prompts=[
            "What symptoms need urgent care?",
            "What should I bring to the hospital?",
            "What happens when I call emergency?",
        ],
        action_label=EMERGENCY_ACTION_LABEL,
        action_url=EMERGENCY_ACTION_URL,
    )


async def _generate_llm_reply(payload: CompanionChatRequest) -> str:
    if not settings.COMPANION_LLM_API_KEY or not settings.COMPANION_LLM_MODEL:
        raise RuntimeError("COMPANION_LLM_API_KEY or COMPANION_LLM_MODEL is not configured")

    context_block = _build_context_block(payload)
    user_message = payload.message

    request_body = {
        "model": settings.COMPANION_LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *(
                [{"role": "system", "content": context_block}]
                if context_block
                else []
            ),
            {
                "role": "user",
                "content": (
                    "Answer the user's question directly and naturally. "
                    "Make the answer practical, gentle, and maternity-safe. "
                    "If symptoms sound urgent, clearly say to seek urgent care.\n"
                    f"Question: {user_message}"
                ),
            },
        ],
        "temperature": 0.4,
        "max_tokens": 220,
    }

    headers = {
        "Authorization": f"Bearer {settings.COMPANION_LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(base_url=settings.COMPANION_LLM_BASE_URL, timeout=settings.COMPANION_LLM_TIMEOUT_SECONDS) as client:
        response = await client.post("/chat/completions", headers=headers, json=request_body)
        response.raise_for_status()
        data = response.json()

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("OpenAI returned no chat choices")

    content = choices[0].get("message", {}).get("content")
    if not content:
        raise RuntimeError("OpenAI returned an empty message")

    return _clean_llm_reply(content)


def _build_local_reply(message: str) -> CompanionChatResponse:
    normalized = message.lower().strip()

    if any(re.search(pattern, normalized) for pattern in EMERGENCY_PATTERNS):
        return _build_emergency_response()

    if any(word in normalized for word in ["medicine", "medication", "pill", "tablet", "dose"]):
        return CompanionChatResponse(
            reply=(
                "Take only medicines that your maternity care team or pharmacist has approved for pregnancy. "
                "Do not stop a prescribed medicine without asking your care team first. "
                "If you tell me the medicine name, I can explain what it is generally used for and what questions to ask."
            ),
            safety_note="I can explain medicines, but I cannot confirm whether a drug is safe for your exact pregnancy without a care-team review.",
            suggested_prompts=[
                "Is this medicine usually used in pregnancy?",
                "What side effects should I watch for?",
                "Can I take over-the-counter pain relief?",
            ],
        )

    if any(word in normalized for word in ["eat", "diet", "food", "nutrition", "meal"]):
        return CompanionChatResponse(
            reply=(
                "Aim for balanced meals with protein, whole grains, fruits, vegetables, and enough water. "
                "Pregnancy-friendly staples include eggs, yogurt or milk that is pasteurized, beans, lentils, oats, leafy greens, and lean meats cooked well. "
                "Avoid raw seafood, unpasteurized dairy, and undercooked meat."
            ),
            safety_note="If you have diabetes, high blood pressure, anemia, or nausea, your nutrition plan may need to be adjusted by a clinician.",
            suggested_prompts=[
                "What are good breakfast ideas in pregnancy?",
                "What foods should I avoid?",
                "How much water should I drink?",
            ],
        )

    if any(word in normalized for word in ["exercise", "workout", "walk", "movement", "activity", "yoga"]):
        return CompanionChatResponse(
            reply=(
                "Gentle activity is usually helpful in pregnancy, such as walking, prenatal yoga, light stretching, and approved swimming. "
                "Stop and get medical advice if you feel dizziness, bleeding, pain, contractions, or shortness of breath."
            ),
            safety_note="The safest exercise plan depends on your pregnancy history and any high-risk conditions.",
            suggested_prompts=[
                "What exercise is safe in the first trimester?",
                "Can I keep walking every day?",
                "What signs mean I should stop exercising?",
            ],
        )

    if any(word in normalized for word in ["report", "result", "scan", "ultrasound", "fhr", "heartbeat", "blood pressure"]):
        return CompanionChatResponse(
            reply=(
                "If you want help reading a report, send the numbers or wording and I can explain them in plain language. "
                "Common things to review are blood pressure, fetal heart rate, movement, contraction pattern, and any risk flags."
            ),
            safety_note="A report explanation is educational only; your care team should confirm whether the result is normal for you.",
            suggested_prompts=[
                "What does a fetal heart rate mean?",
                "What blood pressure numbers are concerning?",
                "How do I understand a pregnancy report?",
            ],
        )

    if any(word in normalized for word in ["roadmap", "journey", "progress", "track", "health"]):
        stage_lines = [f"{index + 1}. {title} - {detail}" for index, (title, detail, _) in enumerate(ROADMAP_STAGES)]
        return CompanionChatResponse(
            reply=(
                "Here is the pregnancy journey roadmap I use as your friendly partner:\n"
                + "\n".join(stage_lines)
                + "\n\nI can also keep an eye on your health signals, explain what they mean, and tell you when the journey looks steady or when it needs extra attention."
            ),
            safety_note="A roadmap is helpful guidance, but only your care team can confirm whether your journey is healthy for your specific case.",
            suggested_prompts=[
                "How healthy does my journey look?",
                "What stage am I in now?",
                "What should I watch for this week?",
            ],
        )

    return CompanionChatResponse(
        reply=(
            "I can help with pregnancy questions about diet, exercise, medicines, reports, symptoms, and when to seek care. "
            "If you describe what you are feeling or share a report number, I will explain it in plain language."
        ),
        safety_note="This assistant is educational and does not replace your obstetric team or emergency care.",
        suggested_prompts=[
            "What should I eat today?",
            "Is this symptom normal?",
            "How do I understand my report?",
        ],
    )


def build_reply(message: str) -> CompanionChatResponse:
    normalized = message.lower().strip()

    if any(re.search(pattern, normalized) for pattern in EMERGENCY_PATTERNS):
        return CompanionChatResponse(
            reply=(
                "This could be urgent. Please contact your maternity care team or emergency services now, "
                "especially if the bleeding, pain, breathing trouble, or reduced baby movement is new or worsening."
            ),
            safety_note="Emergency symptoms should be assessed by your care team right away.",
            suggested_prompts=[
                "What symptoms need urgent care?",
                "When should I call my doctor?",
                "What should I bring to the hospital?",
            ],
        )

    if any(word in normalized for word in ["medicine", "medication", "pill", "tablet", "dose"]):
        return CompanionChatResponse(
            reply=(
                "Take only medicines that your maternity care team or pharmacist has approved for pregnancy. "
                "Do not stop a prescribed medicine without asking your care team first. "
                "If you tell me the medicine name, I can explain what it is generally used for and what questions to ask."
            ),
            safety_note="I can explain medicines, but I cannot confirm whether a drug is safe for your exact pregnancy without a care-team review.",
            suggested_prompts=[
                "Is this medicine usually used in pregnancy?",
                "What side effects should I watch for?",
                "Can I take over-the-counter pain relief?",
            ],
        )

    if any(word in normalized for word in ["eat", "diet", "food", "nutrition", "meal"]):
        return CompanionChatResponse(
            reply=(
                "Aim for balanced meals with protein, whole grains, fruits, vegetables, and enough water. "
                "Pregnancy-friendly staples include eggs, yogurt or milk that is pasteurized, beans, lentils, oats, leafy greens, and lean meats cooked well. "
                "Avoid raw seafood, unpasteurized dairy, and undercooked meat."
            ),
            safety_note="If you have diabetes, high blood pressure, anemia, or nausea, your nutrition plan may need to be adjusted by a clinician.",
            suggested_prompts=[
                "What are good breakfast ideas in pregnancy?",
                "What foods should I avoid?",
                "How much water should I drink?",
            ],
        )

    if any(word in normalized for word in ["exercise", "workout", "walk", "movement", "activity", "yoga"]):
        return CompanionChatResponse(
            reply=(
                "Gentle activity is usually helpful in pregnancy, such as walking, prenatal yoga, light stretching, and approved swimming. "
                "Stop and get medical advice if you feel dizziness, bleeding, pain, contractions, or shortness of breath."
            ),
            safety_note="The safest exercise plan depends on your pregnancy history and any high-risk conditions.",
            suggested_prompts=[
                "What exercise is safe in the first trimester?",
                "Can I keep walking every day?",
                "What signs mean I should stop exercising?",
            ],
        )

    if any(word in normalized for word in ["report", "result", "scan", "ultrasound", "fhr", "heartbeat", "blood pressure"]):
        return CompanionChatResponse(
            reply=(
                "If you want help reading a report, send the numbers or wording and I can explain them in plain language. "
                "Common things to review are blood pressure, fetal heart rate, movement, contraction pattern, and any risk flags."
            ),
            safety_note="A report explanation is educational only; your care team should confirm whether the result is normal for you.",
            suggested_prompts=[
                "What does a fetal heart rate mean?",
                "What blood pressure numbers are concerning?",
                "How do I understand a pregnancy report?",
            ],
        )

    if any(word in normalized for word in ["roadmap", "journey", "progress", "track", "health"]):
        stage_lines = [f"{index + 1}. {title} - {detail}" for index, (title, detail, _) in enumerate(ROADMAP_STAGES)]
        return CompanionChatResponse(
            reply=(
                "Here is the pregnancy journey roadmap I use as your friendly partner:\n"
                + "\n".join(stage_lines)
                + "\n\nI can also keep an eye on your health signals, explain what they mean, and tell you when the journey looks steady or when it needs extra attention."
            ),
            safety_note="A roadmap is helpful guidance, but only your care team can confirm whether your journey is healthy for your specific case.",
            suggested_prompts=[
                "How healthy does my journey look?",
                "What stage am I in now?",
                "What should I watch for this week?",
            ],
        )

    return CompanionChatResponse(
        reply=(
            "I can help with pregnancy questions about diet, exercise, medicines, reports, symptoms, and when to seek care. "
            "If you describe what you are feeling or share a report number, I will explain it in plain language."
        ),
        safety_note="This assistant is educational and does not replace your obstetric team or emergency care.",
        suggested_prompts=[
            "What should I eat today?",
            "Is this symptom normal?",
            "How do I understand my report?",
        ],
    )


@router.post("/chat", response_model=CompanionChatResponse)
async def chat_with_companion(payload: CompanionChatRequest):
    normalized = payload.message.lower().strip()

    if any(re.search(pattern, normalized) for pattern in EMERGENCY_PATTERNS):
        return _build_emergency_response()

    if settings.COMPANION_LLM_API_KEY and settings.COMPANION_LLM_MODEL:
        try:
            reply = await _generate_llm_reply(payload)
            return CompanionChatResponse(
                reply=reply,
                safety_note="Educational guidance only. If this feels urgent, call emergency care right away.",
                suggested_prompts=_suggested_prompts_for(payload.message),
            )
        except Exception as exc:
            logger.exception("Companion LLM request failed, falling back to local reply: %s", exc)
            pass

    return _build_local_reply(payload.message)