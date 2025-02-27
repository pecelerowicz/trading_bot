from abc import ABC, abstractmethod

class DataSource(ABC):
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        """
        Dodaje subskrybenta do listy.
        """
        if not hasattr(subscriber, 'update'):
            raise ValueError("Subskrybent musi implementować metodę 'update'.")
        self.subscribers.append(subscriber)

    @abstractmethod
    async def start(self):
        """
        Rozpoczyna streamowanie danych.
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        Zatrzymuje streamowanie danych.
        """
        pass

    def _emit(self, data):
        """
        Przekazuje dane do subskrybentów.
        (Prywatna metoda, wywoływana wewnętrznie przez implementacje DataSource).
        """
        print(f"Emitowanie danych do {len(self.subscribers)} subskrybentów.")
        for subscriber in self.subscribers:
            subscriber.update(data)

