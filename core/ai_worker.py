from PySide6.QtCore import QObject, Signal
from core.ai_agent import AIAgent

class AIWorker(QObject):
    # Сигнал, который отправит результат обратно в главный поток
    finished = Signal(dict)

    def __init__(self, ai_agent: AIAgent, query: str):
        super().__init__()
        self.ai_agent = ai_agent
        self.query = query

    def run(self):
        # Эта функция выполнится в фоновом потоке
        result = self.ai_agent.process_request(self.query)
        self.finished.emit(result)