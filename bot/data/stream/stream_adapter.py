class StreamAdapter:
    def __init__(self, stream):
        """
        Odpowiada za nadanie strukturze WebSocket kontraktu asynchronicznego iteratora.
        :param stream: Obiekt strumienia WebSocket (np. ReconnectingWebsocket).
        """
        self.stream = stream

    def __aiter__(self):
        """
        Zwraca siebie jako asynchroniczny iterator.
        """
        return self

    async def __anext__(self):
        """
        Odbiera następną wiadomość z WebSocket i zwraca ją jako surowy obiekt JSON.
        """
        try:
            message = await self.stream.recv()
            return message
        except Exception as e:
            print(f"StreamAdapter: Błąd podczas odbierania wiadomości: {e}")
            raise StopAsyncIteration
