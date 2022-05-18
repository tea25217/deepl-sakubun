from dataclasses import dataclass
import json
from random import randint
from typing import Literal
from js import XMLHttpRequest

LanguagesUsingQA = ("EN-GB", "EN-US")


@dataclass(slots=True)
class Status:
    name: Literal["WaitingAnswer", "WaitingTranslate", "Finish"]


class DeepLSakubun:
    def __init__(self):
        self.questions = self._readQuestionFile()
        self.status = Status("WaitingAnswer")

    def _readQuestionFile(self):
        try:
            with open("./question.txt", encoding="utf-8") as f:
                return f.readlines()
        except Exception:
            raise Exception

    def chooseAQuestion(self):
        idx = randint(0, len(self.questions) - 1)
        self.question = self.questions[idx]
        return self.question

    def onClick(self, text, auth_key, language, *args):
        match self.status:
            case Status("WaitingAnswer"):
                newLabels = self._readOriginalAnswer(text, language)
            case Status("WaitingTranslate"):
                newLabels = []
                newLabels.append(self._readTranslatedAnswer(text))
                for label in self._showCorrectAnswer(auth_key):
                    newLabels.append(label)
                newLabels.append(("btn", "クリア"))
            case Status("Finish"):
                newLabels = self._clear()
            case _:
                raise Exception
        return newLabels

    def _readOriginalAnswer(self, text, language):
        self.answer_original = text
        self.target_lang = language
        self.status = Status("WaitingTranslate")
        newLabels = (("answer_original", text),
                     ("description", "翻訳先の言語で回答してみましょう"))
        return newLabels

    def _readTranslatedAnswer(self, text):
        self.answer_translated = text
        return ("answer_translated", text)

    def _showCorrectAnswer(self, auth_key):
        if not auth_key:
            raise Exception
        param = self._generateParam(auth_key)
        self._callAPI(param)
        if self.target_lang in LanguagesUsingQA:
            self._splitReceivedAnswer(self.response["translations"][0]["text"])
            self.status = Status("Finish")
            return (("answer_correct_q", self.answer_correct_q),
                    ("answer_correct_a", self.answer_correct_a))
        else:
            self.answer_correct = self.response["translations"][0]["text"]
            self.status = Status("Finish")
            return (("answer_correct_q", self.answer_correct))

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

    def _splitReceivedAnswer(self, received):
        self.answer_correct_q = received.split(" A.")[0]
        self.answer_correct_a = received.split(self.answer_correct_q)[1]

    def _clear(self):
        self.question = self.chooseAQuestion()
        self.answer_original = ""
        self.answer_translated = ""
        self.answer_correct = ""
        self.status = Status("WaitingAnswer")
        newLabels = (("description", "まずは日本語で回答してみましょう"),
                     ("question", self.question),
                     ("btn", "決定"),
                     ("answer_original", ""),
                     ("answer_translated", ""),
                     ("answer_correct_q", ""),
                     ("answer_correct_a", ""))
        return newLabels
