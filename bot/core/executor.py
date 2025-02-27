import requests

class Executor:
    def __init__(self, bot_token, chat_id):
        """
        Inicjalizuje klienta Telegram bota.
        :param bot_token: Token API bota Telegramowego.
        :param chat_id: ID czatu (Twój osobisty lub grupowy).
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def execute(self, signal):
        """
        Odbiera sygnał i wysyła wiadomość do Telegrama.
        :param signal: Tekst wiadomości do wysłania.
        """
        payload = {
            "chat_id": self.chat_id,
            "text": signal
        }
        response = requests.post(self.api_url, data=payload)
        if response.status_code == 200:
            print("Wiadomość wysłana!")
        else:
            print(f"Błąd wysyłania wiadomości: {response.status_code} {response.text}")
