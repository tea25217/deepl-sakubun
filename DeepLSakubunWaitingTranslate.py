"""ステータスWaitingTranslateの処理
"""
import json
import os
from typing import Tuple
from Common import Language, Status


class DeepLSakubunWaitingTranslate:
    def _readTranslatedAnswer(self, text: str, language: str) \
            -> Tuple[str, str]:
        self.answer_translated = text
        self.target_lang = language
        return ("answer_translated", text)

    def _showCorrectAnswer(self, auth_key: str) -> Tuple[Tuple[str, str]]:
        # DeepLのAPIを叩く
        if not auth_key:
            auth_key = os.getenv("DEEPL_API_KEY_FREE")

        if not auth_key:
            raise Exception

        param = self._generateParam(auth_key)
        self._callAPI(param)

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
            return (("answer_correct_q", self.answer_correct),)

    def _generateParam(self, auth_key: str) -> dict[str, str]:
        URL = "https://api-free.deepl.com/v2/translate"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = "auth_key=" + auth_key + \
            "&text=Q." + self.question + \
            " A." + self.answer_original + \
            "&target_lang=" + self.target_lang
        param = {"URL": URL, "headers": headers, "body": body}
        return param

    def _callAPI(self, param: dict[str, str | dict[str, str]]) -> None:
        # モジュールテストを可能にするため、PyScriptのjsモジュールはlazy importする
        from js import XMLHttpRequest
        req = XMLHttpRequest.new()
        req.open("POST", param["URL"], False)
        for k, v in param["headers"].items():
            req.setRequestHeader(k, v)
        req.send(param["body"])
        self.response = json.loads(req.response)

    def _splitReceivedAnswer(self, received: str) -> None:
        separator = Language.getSeparatorFromLanguage(self.target_lang)
        self.answer_correct_q = received.split(separator)[0]
        self.answer_correct_a = received.split(self.answer_correct_q)[1]
