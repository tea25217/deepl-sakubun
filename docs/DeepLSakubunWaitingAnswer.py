"""ステータスWaitingAnswerの処理
"""
from typing import Tuple
from docs.Common import Status


class DeepLSakubunWaitingAnswer:
    def _readOriginalAnswer(self, text: str) \
            -> Tuple[Tuple[str, str]]:
        self.answer_original = text
        self.status = Status("WaitingTranslate")
        newLabels = (("answer_original", text), ("description",
                                                 "翻訳先の言語で回答してみましょう"))
        return newLabels
