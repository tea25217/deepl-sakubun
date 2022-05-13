from random import randint
from typing import NewType
from js import fetch, document

Status = NewType("Status", str)


class DeepLSakubun:
    def __init__(self):
        self.questions = self._readQuestionFile()
        self.question = ""
        self.answer_original = ""
        self.answer_translated = ""
        self.answer_correct = ""
        self.source_lang = "JA"
        self.target_lang = "EN-GB"
        self.status: Status = Status("WaitingAnswer")
        self.auth_key = ""

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

    def onClick(self, text_element):
        text = text_element.element.value
        text_element.clear()
        match self.status:
            case "WaitingAnswer":
                newLabels = self._readOriginalAnswer(text)
            case "WaitingTranslate":
                newLabels = []
                newLabels.append(self._readTranslatedAnswer(text))
                self._showCorrectAnswer()
            case "Finish":
                self._clear()
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

    def _showCorrectAnswer(self):
        param = self._generateParam()
        res = self._fetch(param)
        self.answer_correct = res["translations"][1]["text"]
        pyscript.write("answer_correct", "DeepLによる回答:" + self.answer_correct)
        self.status = Status("Finish")

    def _generateParam(self):
        if not self.auth_key:
            self.auth_key = Element("auth-key")
        URL = "/v2/translate?auth_key=" + self.auth_key
        headers = {
            "Host": "api-free.deepl.com",
            "User-Agent": "YourApp",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = "auth_key=" + self.auth_key + "&text=Q." + self.question + "&text=A." + self.answer_translated
        init = {
            "method": "POST",
            "headers": headers,
            "body": body
        }
        return {URL, init}

    async def _fetch(param):
        res = await fetch(*param)
        return await res.json()

    def _clear(self):
        self.question = self._choiceQuestion()
        self.answer_original = ""
        self.answer_translated = ""
        self.answer_correct = ""
        self.status = Status("WaitingAnswer")
