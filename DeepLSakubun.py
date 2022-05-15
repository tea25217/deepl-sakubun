from dataclasses import dataclass
import json
from random import randint
from typing import Literal
from js import XMLHttpRequest


@dataclass(slots=True)
class Status:
    name: Literal["WaitingAnswer", "WaitingTranslate", "Finish"]


class DeepLSakubun:
    def __init__(self):
        self.questions = self._readQuestionFile()
        self.question = ""
        self.answer_original = ""
        self.answer_translated = ""
        self.answer_correct = ""
        self.source_lang = "JA"
        self.target_lang = "EN-GB"
        self.status = Status("WaitingAnswer")

    def _readQuestionFile(self):
        try:
            with open("./question.txt", encoding="utf-8") as f:
                return f.readlines()
        except Exception:
            raise Exception

    def choiceQuestion(self):
        idx = randint(0, len(self.questions) - 1)
        self.question = self.questions[idx]
        return self.question

    def onClick(self, text, auth_key):
        match self.status:
            case Status("WaitingAnswer"):
                newLabels = self._readOriginalAnswer(text)
            case Status("WaitingTranslate"):
                newLabels = []
                newLabels.append(self._readTranslatedAnswer(text))
                newLabels.append(self._showCorrectAnswer(auth_key))
            case Status("Finish"):
                newLabels = self._clear()
            case _:
                raise Exception
        return newLabels

    def _readOriginalAnswer(self, text):
        self.answer_original = text
        self.status = Status("WaitingTranslate")
        newLabels = (("answer_original", "日本語の回答:" + text),
                     ("description", "英語で回答してみましょう"))
        return newLabels

    def _readTranslatedAnswer(self, text):
        self.answer_translated = text
        return ("answer_translated", "英語の回答:" + text)

    def _showCorrectAnswer(self, auth_key):
        if not auth_key:
            raise Exception
        param = self._generateParam(auth_key)
        self._callAPI(param)
        self.answer_correct = self.response["translations"][0]["text"]
        self.status = Status("Finish")
        return ("answer_correct", "DeepLによる回答:" + self.answer_correct)

    def _generateParam(self, auth_key):
        URL = "https://api-free.deepl.com/v2/translate"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = "auth_key=" + auth_key + \
            "&text=Q." + self.question + \
            " A." + self.answer_original + \
            "&target_lang=" + self.target_lang
        param = {"URL": URL, "headers": headers, "body": body}
        return param

    def _callAPI(self, param):
        req = XMLHttpRequest.new()
        req.open("POST", param["URL"], False)
        for k, v in param["headers"].items():
            req.setRequestHeader(k, v)
        req.send(param["body"])
        self.response = json.loads(req.response)

    def _clear(self):
        self.question = self.choiceQuestion()
        self.answer_original = ""
        self.answer_translated = ""
        self.answer_correct = ""
        self.status = Status("WaitingAnswer")
        newLabels = (("question", self.question),
                     ("answer_original", ""),
                     ("answer_translated", ""),
                     ("answer_correct", ""))
        return newLabels
