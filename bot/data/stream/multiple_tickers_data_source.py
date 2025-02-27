from bot.data.stream.data_source import DataSource
from bot.data.stream.binance_stream_manager import BinanceStreamManager
import asyncio

class MultipleTickersDataSource(DataSource):
    def __init__(self, tickers, interval, timeout=5, only_closed=False):
        """
        Tworzy DataSource obsługujący wiele tickerów z opcją synchronizacji świec.
        :param tickers: Lista symboli par handlowych (np. ['BTCUSDT', 'ETHUSDT']).
        :param interval: Interwał czasowy świec (np. '1m').
        :param timeout: Czas oczekiwania (w sekundach) na synchronizację zamkniętych świec.
        """
        super().__init__()
        self.tickers = tickers
        self.interval = interval
        self.stream_managers = {ticker: BinanceStreamManager(ticker, interval) for ticker in tickers}
        self.klines_buffer = {ticker: None for ticker in tickers}  # Bufor dla najnowszych świec
        self.closed_klines_buffer = {ticker: None for ticker in tickers}  # Bufor dla zamkniętych świec
        self.timeout = timeout
        self.only_closed = only_closed
        self.lock = asyncio.Lock()

    async def start(self):
        """
        Rozpoczyna streamowanie danych i synchronizuje świece dla wszystkich tickerów.
        """
        await asyncio.gather(*[manager.connect() for manager in self.stream_managers.values()])
        await self._stream_data()

    async def stop(self):
        """
        Zatrzymuje streamowanie danych.
        """
        await asyncio.gather(*[manager.disconnect() for manager in self.stream_managers.values()])

    async def _stream_data(self):
        tasks = [self._handle_stream(ticker, manager) for ticker, manager in self.stream_managers.items()]
        await asyncio.gather(*tasks)

    async def _handle_stream(self, ticker, manager):
        async for kline in manager.get_stream():
            async with self.lock:
                # Aktualizacja bufora otwartych świec
                self.klines_buffer[ticker] = kline

                # Jeśli świeca zamknięta, aktualizujemy bufor zamkniętych świec
                if kline.is_closed:
                    self.closed_klines_buffer[ticker] = kline

                # Procesujemy bufor
                if all(self.closed_klines_buffer.values()):
                    await self._emit_closed_klines()
                elif all(self.klines_buffer.values()) and not any(self.closed_klines_buffer.values()):
                    if not self.only_closed:
                        await self._emit_open_klines()

    async def _emit_open_klines(self):
        """
        Emituje paczkę otwartych świec.
        """
        self._emit({ticker: kline for ticker, kline in self.klines_buffer.items()})
        self._reset_open_buffer()

    async def _emit_closed_klines(self):
        """
        Emituje paczkę zamkniętych świec.
        """
        self._emit({ticker: kline for ticker, kline in self.closed_klines_buffer.items()})
        self._reset_buffers()

    def _reset_open_buffer(self):
        """
        Resetuje bufor otwartych świec po emisji.
        """
        self.klines_buffer = {ticker: None for ticker in self.tickers}

    def _reset_buffers(self):
        """
        Resetuje wszystkie bufory po emisji zamkniętych świec.
        """
        self.klines_buffer = {ticker: None for ticker in self.tickers}
        self.closed_klines_buffer = {ticker: None for ticker in self.tickers}
