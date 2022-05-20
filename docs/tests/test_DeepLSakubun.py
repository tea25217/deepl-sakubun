"""DeepLSakubunモジュールテスト

現段階で粒度の細かいテストを増やしてもテストコードが即寿命を迎えかねないので、
モジュールの入出力をざっくりと確認する。

"""
from typing import Tuple
import pytest
import docs.DeepLSakubun


@pytest.fixture
def deepLSakubun() -> docs.DeepLSakubun:
    deepLSakubun = docs.DeepLSakubun.DeepLSakubun()
    deepLSakubun.chooseAQuestion()
    return deepLSakubun


@pytest.fixture
def default_input() -> Tuple[str]:
    return ("なんか気の利いた回答", "", "EN-GB")


class Test_DeepLSakubun__init__:

    def test_インスタンス生成できて_必要なインスタンス変数がある(self):
        instance = docs.DeepLSakubun.DeepLSakubun()
        assert len(instance.questions) > 1
        assert instance.status == docs.DeepLSakubun.Status("WaitingAnswer")

    def test_chooseAQuestionでランダムに質問を取得できる(self):
        instance = docs.DeepLSakubun.DeepLSakubun()
        assert instance.chooseAQuestion()
        assert instance.question

        old_question = instance.question
        for _ in range(100):
            new_question = instance.chooseAQuestion()
            if old_question != new_question:
                assert new_question == instance.question
                break
        else:
            assert False


class Test_DeepLSakubun_WaitingAnswer:

    def test_日本語の回答を受け取り_画面の変更内容を出力できる(self, deepLSakubun, default_input):
        expected_output_answer_original = ("answer_original", default_input[0])
        expected_output_description = ("description", "翻訳先の言語で回答してみましょう")

        actual_output = deepLSakubun.onClick(*default_input)

        assert expected_output_answer_original in actual_output
        assert expected_output_description in actual_output

    def test_ステータスがWaitingTranslateに遷移する(self, deepLSakubun, default_input):
        expected_status = docs.DeepLSakubun.Status("WaitingTranslate")

        assert deepLSakubun.status == docs.DeepLSakubun.Status("WaitingAnswer")
        deepLSakubun.onClick(*default_input)
        actual_status = deepLSakubun.status

        assert expected_status == actual_status

    def test_二周目以降_新しい回答を元に画面変更内容を出力できる(self):
        ...


class Test_DeepLSakubun_WaitingTranslate:

    def test_翻訳先言語の回答を受け取り_画面の変更内容を出力できる(self, deepLSakubun):
        ...

    def test_ステータスがFinishに遷移する(self):
        ...

    def test_二周目以降_新しい回答を元に画面変更内容を出力できる(self):
        ...

    def test_選択した言語が_callAPIの引数に渡される(self):
        ...

    def test_APIキー未入力の場合は例外を吐く(self):
        ...

    def test_分割判定可能な言語ではDeepLの回答を質問と答えに分割して出力する(self):
        ...

    def test_分割判定できない言語ではDeepLの回答を1つのタプルで出力する(self):
        ...


class Test_DeepLSakubun_Finish:

    def test_変数を空にして_画面の変更内容を出力できる(self, deepLSakubun):
        ...

    def test_ステータスがWaitingAnswerに遷移する(self):
        ...


class Test_others:

    def test_存在しないステータスでonClickを叩くと例外を吐く(self):
        ...
