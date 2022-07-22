"""ステータスWaitingTranslateの処理
"""
from typing import Tuple
from Common import Language, Status
from DeepLSakubunCallAPI import DeepLSakubunCallAPI


class DeepLSakubunWaitingTranslate(DeepLSakubunCallAPI):
    def _readTranslatedAnswer(self, text: str, language: str) \
            -> Tuple[str, str]:
        self.answer_translated = text
        self.target_lang = language
        return ("answer_translated", text)

    def _showCorrectAnswer(self, auth_key: str) -> Tuple[Tuple[str, str]]:
        # APIキーが入力されている場合、直接DeepLのAPIを叩く
        # APIキーが入力されていない場合、サーバー側で処理
        if auth_key:
            param = self._generateParam(auth_key)
            self._callAPI(param)
        else:
            param = self._generateParamForAPIServer(auth_key)
            self._callAPI(param)

            if self.response["result"] != "OK":
                print(self.response["message"])
                raise Exception

        return self._decideToSplitAnswer()

    def _decideToSplitAnswer(self) -> Tuple[Tuple[str, str]]:
        # "Q. ... A. ..."を翻訳後にAに相当する文字が一意に定まる翻訳先言語の場合、
        # 翻訳後の文字列をAの前で分割して2行で表示する
        if Language.canSeparate(self.target_lang):
            self._splitReceivedAnswer(self.response["translations"][0]["text"])
            self.status = Status("Finish")
            return (("answer_correct_q", self.answer_correct_q),
                    ("answer_correct_a", self.answer_correct_a))
        else:
            self.answer_correct = self.response["translations"][0]["text"]
            self.status = Status("Finish")
            return (("answer_correct_q", self.answer_correct), )

    def _splitReceivedAnswer(self, received: str) -> None:
        separator = Language.getSeparatorFromLanguage(self.target_lang)
        self.answer_correct_q = received.split(separator)[0]
        self.answer_correct_a = received.split(self.answer_correct_q)[1]
