"""DeepLSakubunモジュールテスト

現段階で粒度の細かいテストを増やしてもテストコードが即寿命を迎えかねないので、
モジュールの入出力をざっくりと確認する。

"""
import pytest
import docs.DeepLSakubun


@pytest.fixture
def deepLSakubun() -> docs.DeepLSakubun:
    deepLSakubun = docs.DeepLSakubun.DeepLSakubun()
    deepLSakubun.chooseAQuestion()
    return deepLSakubun


class Test_DeepLSakubun__init__():

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


class Test_DeepLSakubun_WaitingAnswer():

    def test_日本語の回答を受け取り_画面の変更内容を出力できる(self, deepLSakubun):
        input_text = "なんか気の利いた回答"
        auth_key = ""
        language = "EN-GB"

        expected_output_answer_original = ("answer_original", input_text)
        expected_output_description = ("description", "翻訳先の言語で回答してみましょう")

        actual_output = deepLSakubun.onClick(input_text, auth_key, language)

        assert expected_output_answer_original in actual_output
        assert expected_output_description in actual_output

    def test_二周目以降_正しいラベルを出力できる(self):
        ...


class Test_DeepLSakubun_WaitingTranslate():

    def test_日本語の回答を受け取り_画面の変更内容を出力できる(self, deepLSakubun):
        ...

    def test_二周目以降_正しいラベルを出力できる(self):
        ...


class Test_DeepLSakubun_Finish():

    def test_変数を空にして_画面の変更内容を出力できる(self, deepLSakubun):
        ...


class Test_others():

    def test_存在しないステータスでonClickを叩くと例外を吐く(self):
        ...
