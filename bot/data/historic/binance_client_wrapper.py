from binance.client import Client
import time
from datetime import datetime, timedelta

class BinanceClientWrapper:
    def __init__(self):
        """
        Inicjalizuje klienta Binance.
        """
        self.client = Client()

    def get_klines(self, symbol, interval, startTime, endTime=None):
        """
        Pobiera wszystkie dostępne świece w danym zakresie czasu.
        :param symbol: Symbol pary handlowej (np. "BTCUSDT").
        :param interval: Interwał świec (np. "1h", "15m").
        :param start_time: Początek zakresu (w milisekundach od EPOCH).
        :param end_time: Koniec zakresu (w milisekundach od EPOCH, opcjonalny).
        :return: Lista świec w formacie zwracanym przez Binance API.
        """
        data = []
        request_count = 0
        while True:
            # Pobierz maksymalnie 1000 świec w jednym zapytaniu
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=1000
            )

            if not klines:
                break

            data.extend(klines)

            # Ustawienie start_time na czas otwarcia ostatniej świecy + 1 ms
            startTime = klines[-1][0] + 1

            # Licznik zapytań
            request_count += 1

            # Jeśli zwrócono mniej niż 1000 świec, oznacza to koniec danych
            if len(klines) < 1000:
                break

            # Mały delay, aby uniknąć przekroczenia limitu zapytań API
#             time.sleep(0.1)

        print(f"Liczba zapytań do API: {request_count}")
        return data

    def get_n_klines(self, symbol, interval, n_klines):
        """
        Pobiera n ostatnich świec dla podanego symbolu i interwału.
        :param symbol: Symbol pary handlowej (np. "BTCUSDT").
        :param interval: Interwał świec (np. "1h", "15m").
        :param n_klines: Liczba świec do pobrania.
        :return: Lista n ostatnich świec w formacie zwracanym przez Binance API.
        """
        # Konwersja interwału na milisekundy
        interval_map = {
            "1m": 60 * 1000,
            "3m": 3 * 60 * 1000,
            "5m": 5 * 60 * 1000,
            "15m": 15 * 60 * 1000,
            "30m": 30 * 60 * 1000,
            "1h": 60 * 60 * 1000,
            "2h": 2 * 60 * 60 * 1000,
            "4h": 4 * 60 * 60 * 1000,
            "6h": 6 * 60 * 60 * 1000,
            "8h": 8 * 60 * 60 * 1000,
            "12h": 12 * 60 * 60 * 1000,
            "1d": 24 * 60 * 60 * 1000,
            "3d": 3 * 24 * 60 * 60 * 1000,
            "1w": 7 * 24 * 60 * 60 * 1000,
            "1M": 30 * 24 * 60 * 60 * 1000
        }

        if interval not in interval_map:
            raise ValueError(f"Nieobsługiwany interwał: {interval}")

        interval_ms = interval_map[interval]

        # Pobierz bieżący czas z Binance
        server_time = self.client.get_server_time()['serverTime']

        # Obliczenie startTime na podstawie liczby świec i interwału
        end_time = server_time  # Aktualny czas w milisekundach od EPOCH
        start_time = end_time - (n_klines * interval_ms)

        # Pobranie świec za pomocą istniejącej metody
        klines = self.get_klines(symbol, interval, start_time, end_time)

        # Jeśli zwrócono więcej świec niż potrzebujemy, przytnij listę
        return klines[-n_klines:]
