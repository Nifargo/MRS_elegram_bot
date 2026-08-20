import logging

from groq import Groq, RateLimitError

from config import GROQ_API_KEY, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

# Історія чатів по user_id. Обрізається до HISTORY_LIMIT: раніше росла до
# перезапуску процесу й тягла за собою токени та затримку.
chat_histories = {}

HISTORY_LIMIT = 10  # останніх повідомлень (≈5 обмінів)

APOLOGY = "Вибачте, сталася помилка. Спробуйте ще раз або зверніться до адміністратора."


async def get_response(user_id: int, message: str, context_block: str = "") -> str:
    """Відповідь Groq. RateLimitError (429) пробрасується назовні — викликач
    відповідає клієнтом телефоном салону й реєструє його для дайджесту."""
    history = chat_histories.setdefault(user_id, [])
    history.append({"role": "user", "content": message})

    system = f"{SYSTEM_PROMPT}\n\n{context_block}" if context_block else SYSTEM_PROMPT
    window = history[-HISTORY_LIMIT:]
    if window and window[0]["role"] == "assistant":
        # без свого user-питання відповідь лише збиває модель з пантелику
        window = window[1:]
    messages = [{"role": "system", "content": system}] + window

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
    except RateLimitError:
        history.pop()  # без відповіді пара user/assistant лишилась би кривою
        raise
    except Exception as e:
        logger.error(f"Помилка Groq API: {type(e).__name__}: {e}", exc_info=True)
        history.pop()
        return APOLOGY

    choice = response.choices[0] if response.choices else None
    assistant_message = (choice.message.content or "") if choice else ""
    if not assistant_message:
        logger.error("Groq повернув відповідь без тексту")
        history.pop()  # порожня відповідь у історії псувала б усі наступні запити
        return APOLOGY

    history.append({"role": "assistant", "content": assistant_message})
    chat_histories[user_id] = history[-HISTORY_LIMIT:]
    return assistant_message


def clear_chat_history(user_id: int):
    """Очистити історію чату для користувача."""
    chat_histories.pop(user_id, None)
