"""DeepLSakubun.py

deepl-sakubunの本体。
DOM操作はDeepLSakubun.onClickから対象のidと値を返してindex.htmlでやる。
それ以外はここでやる。

"""
from dataclasses import dataclass
import json
from random import randint
from typing import Literal
from js import XMLHttpRequest

# 質問と回答をQ. ... A. ... で表す言語
LanguagesUsingQA = ("EN-GB", "EN-US", "JA")


@dataclass(slots=True)
class Status:
    """DeepLSakubunクラスが取る状態

    WaitingAnswer -> WaitingTranslate -> Finish -> WaitingAnswer
    のサイクルで遷移する
    (3状態の決定性有限オートマトン)

    """
    name: Literal["WaitingAnswer", "WaitingTranslate", "Finish"]


class DeepLSakubun:
    """deepl-sakubunの主処理を行う

    index.htmlのハンドラーから画面入力を受け取り、
    状態に応じた処理結果をlabelタグの変更内容として返す。

    (index.html, 初期状態)画面に質問を表示
    ↓
    (ユーザー)テキストエリアに日本語で回答を入力し、決定ボタン押下
    ↓
    (DeepLSakubun)画面の変更内容を出力し、翻訳先言語の回答待ち状態に遷移
    ↓
    (ユーザー)テキストエリアに翻訳先言語で回答を入力し、決定ボタン押下
    ↓
    (DeepLSakubun)DeepLの翻訳APIに質問と入力された日本語回答を結合してPOST
    ↓
    (DeepLSakubun)APIのレスポンスをパースし、画面の変更内容を出力、完了状態へ遷移
    ↓
    (ユーザー)クリアボタン押下
    ↓
    (DeepLSakubun)画面の変更内容を出力、初期状態へ遷移

    Attributes:
        questions [List[str]]: question.txtから読み出した全ての質問
        question [str]: 現在の質問
        status [Status[Literal
            ["WaitingAnswer", "WaitingTranslate", "Finish"]]]:
            現在の状態。
            "WaitingAnswer": 日本語の回答を待っている
            "WaitingTranslate": 翻訳先言語の回答を待っている
            "Finish": DeepLによる回答を出力し終え、状態クリア待ち
        target_lang [str]: 翻訳先言語。画面で選択したものを受け取る。
        answer_original [str]: ユーザーが画面で入力した日本語の回答
        answer_translated [str]: ユーザーが画面で入力した翻訳先言語の回答
        response [JSON]: DeepL APIのレスポンス
        answer_correct [str]: DeepLによる翻訳結果
        answer_correct_q [str]: DeepLによる翻訳結果の質問部分
        answer_correct_a [str]: DeepLによる翻訳結果の回答部分

    """

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
            # 日本語の回答を受け付ける状態
            case Status("WaitingAnswer"):
                newLabels = self._readOriginalAnswer(text, language)
            # 翻訳先言語の回答を受け付ける状態
            case Status("WaitingTranslate"):
                newLabels = []
                newLabels.append(self._readTranslatedAnswer(text))
                for label in self._showCorrectAnswer(auth_key):
                    newLabels.append(label)
                newLabels.append(("btn", "クリア"))
            # 終了後のクリアボタンを押された時
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
        # DeepLのAPIを叩く
        if not auth_key:
            raise Exception
        param = self._generateParam(auth_key)
        self._callAPI(param)

        # 翻訳先言語が質問と回答をQとAで表現できる場合、
        # 翻訳後の文字列を" A."の前で分割して2行で表示する
        if self.target_lang in LanguagesUsingQA:
            self._splitReceivedAnswer(self.response["translations"][0]["text"])
            self.status = Status("Finish")
            return (("answer_correct_q", self.answer_correct_q),
                    ("answer_correct_a", self.answer_correct_a))
        else:
            self.answer_correct = self.response["translations"][0]["text"]
            self.status = Status("Finish")
            return (("answer_correct_q", self.answer_correct),)

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
