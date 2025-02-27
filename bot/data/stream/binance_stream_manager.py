from binance import AsyncClient, BinanceSocketManager
from bot.data.stream.stream_adapter import StreamAdapter
from bot.data.stream.stream_transformer import StreamTransformer

class BinanceStreamManager:
    def __init__(self, ticker, interval):
        """
        Menedżer strumienia danych Binance dla podanej pary handlowej i interwału.
        """
        self.ticker = ticker
        self.interval = interval
        self.client = None
        self.bm = None

    async def connect(self):
        """
        Tworzy połączenie z Binance.
        """
        print("BinanceStreamManager: Tworzenie klienta Binance...")
        self.client = await AsyncClient.create()
        self.bm = BinanceSocketManager(self.client)
        print("BinanceStreamManager: Klient Binance uruchomiony.")

    async def get_stream(self):
        """
        Zwraca asynchroniczny iterator emitujący dane w formie KlineMessage.
        """
        async with self.bm.kline_socket(symbol=self.ticker, interval=self.interval) as raw_stream:
            adapted_stream = StreamAdapter(raw_stream)
            transformed_stream = StreamTransformer(adapted_stream)
            async for kline_message in transformed_stream:
                yield kline_message

    async def disconnect(self):
        """
        Zamyka połączenie z Binance.
        """
        if self.client:
            print("BinanceStreamManager: Zamykanie połączenia z Binance...")
            await self.client.close_connection()
