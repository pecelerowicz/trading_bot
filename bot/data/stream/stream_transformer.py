from bot.models.kline_message import KlineMessage

class StreamTransformer:
    def __init__(self, stream):
        """
        Odpowiada za przekształcanie danych z surowego JSON-a na obiekty KlineMessage.
        :param stream: Strumień danych (np. StreamAdapter).
        """
        self.stream = stream

    def __aiter__(self):
        """
        Zwraca siebie jako asynchroniczny iterator.
        """
        return self

    async def __anext__(self):
        """
        Pobiera wiadomość z surowego strumienia i przekształca ją na obiekt KlineMessage.
        """
        try:
            message = await self.stream.__anext__()
            kline = message['k']
            return KlineMessage(
                timestamp=kline['t'],
                open=float(kline['o']),
                high=float(kline['h']),
                low=float(kline['l']),
                close=float(kline['c']),
                volume=float(kline['v']),
                is_closed=kline['x'],
                symbol=kline['s'],
                interval=kline['i']
            )
        except KeyError as e:
            print(f"StreamTransformer: Klucz nie został znaleziony w wiadomości: {e}")
            raise StopAsyncIteration
        except Exception as e:
            print(f"StreamTransformer: Błąd przetwarzania wiadomości: {e}")
            raise StopAsyncIteration
