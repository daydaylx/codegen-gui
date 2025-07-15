# api_worker.py – Threaded Request-Handler

from PySide6.QtCore import QObject, Signal, Slot
from api.openrouter import generate_code, OpenRouterAPIError

class APIWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, user_prompt, model, system_prompt):
        super().__init__()
        self.user_prompt = user_prompt
        self.model = model
        self.system_prompt = system_prompt

    @Slot()
    def run(self):
        try:
            response = generate_code(
                user_prompt=self.user_prompt,
                model=self.model,
                system_prompt=self.system_prompt
            )
            self.finished.emit(response)
        except OpenRouterAPIError as e:
            self.error.emit(str(e))
