class Engine:
    def __init__(self, data_source, executor):
        """
        Inicjalizuje komponenty silnika.
        :param data_source: Instancja DataSource odpowiedzialna za dane.
        :param executor: Instancja Executor odpowiedzialna za wykonywanie sygnałów.
        """
        self.data_source = data_source
        self.executor = executor
        self.strategies = []

    def add_strategy(self, strategy):
        """
        Dodaje strategię do silnika.
        :param strategy: Instancja Strategy odpowiedzialna za przetwarzanie danych.
        """
        print(f"Engine: Dodawanie strategii {strategy.__class__.__name__}...")
        self.strategies.append(strategy)

    def setup(self):
        """
        Łączy komponenty: DataSource, Strategy i Executor.
        """
        print("Engine: Konfiguracja komponentów...")
        for strategy in self.strategies:
            self.data_source.subscribe(strategy)
            strategy.subscribe(self.executor.execute)
        print("Engine: Komponenty połączone.")

    async def start(self):
        """
        Rozpoczyna działanie systemu.
        """
        print("Engine: Uruchamianie DataSource...")
        await self.data_source.start()
