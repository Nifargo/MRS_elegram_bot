import logging

from groq import Groq, RateLimitError

from config import GROQ_API_KEY, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

# Історія чатів по user_id. Обрізається до HISTORY_LIMIT: раніше росла до
# перезапуску процесу й тягла за собою токени та затримку.
chat_histories = {}

HISTORY_LIMIT = 10  # останніх повідомлень (≈5 обмінів)


async def get_response(user_id: int, message: str, context_block: str = "") -> str:
    """Відповідь Groq. RateLimitError (429) пробрасується назовні — викликач
    відповідає клієнтом телефоном салону й реєструє його для дайджесту."""
    history = chat_histories.setdefault(user_id, [])
    history.append({"role": "user", "content": message})

    system = f"{SYSTEM_PROMPT}\n\n{context_block}" if context_block else SYSTEM_PROMPT
    messages = [{"role": "system", "content": system}] + history[-HISTORY_LIMIT:]

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
        return "Вибачте, сталася помилка. Спробуйте ще раз або зверніться до адміністратора."

    assistant_message = response.choices[0].message.content
    history.append({"role": "assistant", "content": assistant_message})
    chat_histories[user_id] = history[-HISTORY_LIMIT:]
    return assistant_message


def clear_chat_history(user_id: int):
    """Очистити історію чату для користувача."""
    chat_histories.pop(user_id, None)
