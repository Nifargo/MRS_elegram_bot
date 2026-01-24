from groq import Groq
from config import GROQ_API_KEY, SYSTEM_PROMPT

# Ініціалізація клієнта
client = Groq(api_key=GROQ_API_KEY)

# Зберігання історії чатів для кожного користувача
chat_histories = {}


async def get_response(user_id: int, message: str) -> str:
    """Отримати відповідь від Groq для повідомлення користувача."""
    try:
        # Отримати або створити історію для користувача
        if user_id not in chat_histories:
            chat_histories[user_id] = []

        # Додати повідомлення користувача до історії
        chat_histories[user_id].append({
            "role": "user",
            "content": message
        })

        # Підготувати повідомлення з системним промптом
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + chat_histories[user_id]

        # Відправити запит до Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )

        # Отримати текст відповіді
        assistant_message = response.choices[0].message.content

        # Додати відповідь до історії
        chat_histories[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    except Exception as e:
        print(f"Помилка Groq API: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return "Вибачте, сталася помилка. Спробуйте ще раз або зверніться до адміністратора."


def clear_chat_history(user_id: int):
    """Очистити історію чату для користувача."""
    if user_id in chat_histories:
        del chat_histories[user_id]