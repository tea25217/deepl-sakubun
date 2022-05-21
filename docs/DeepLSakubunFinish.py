"""ステータスFinishの処理
"""
from typing import Tuple
from docs.Common import Status


class DeepLSakubunFinish:
    def _clear(self) -> Tuple[Tuple[str, str]]:
        self.question = self.chooseAQuestion()
        self.answer_original = ""
        self.answer_translated = ""
        self.answer_correct = ""
        self.answer_correct_q = ""
        self.answer_correct_a = ""
        self.status = Status("WaitingAnswer")
        newLabels = (("description", "まずは日本語で回答してみましょう"),
                     ("question", self.question),
                     ("btn", "決定"),
                     ("answer_original", ""),
                     ("answer_translated", ""),
                     ("answer_correct_q", ""),
                     ("answer_correct_a", ""))
        return newLabels
