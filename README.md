# DeepLで外国語練習するやつ


## 場所
ここ<br>
https://tea25217.github.io/deepl-sakubun/<br>
（PyScriptの仕様上ページ読み込みに少し時間がかかります）<br>
<br>

## 概要
DeepL翻訳の機能を利用して外国語のライティングを練習するwebアプリです。<br>
[Englister](https://english.yunomy.com/)や[Deep英作文](https://deep-eisakubun.vercel.app/)のパチモン。<br>
<br>
オマージュ元に比べての差別化要素として、練習する言語を選択可能です。<br>
API仕様のtarget_langに記載されている言語に対応しています。<br>
https://www.deepl.com/ja/docs-api/translating-text/request/<br>
<br>

## 使い方
- 画面右上の翻訳先言語から練習したい言語を選択
- 画面にあなたへの質問が出ているので、テキストボックスにまずは日本語で回答を入力してください
- 決定ボタンを押したら、今度は先程の回答を練習したい言語で入力してください
- 決定ボタンを押すと、DeepLによる模範解答が表示されます
- クリアボタンを押すと最初に戻ります
<br>

## 補足：APIキー
画面左上にあるAPIキーの欄は入力しなくても動きますが、入れてもらえると喜びます。<br>
（空欄の場合はサーバーサイドを経由して作者のAPIキーを使用、<br>
入力されている場合はアプリから直接DeepLの翻訳APIを叩きます）<br>
<br>
下記リンク先の「無料で登録する」から取得可能。<br>
https://www.deepl.com/pro-api?cta=menu-pro-api<br>
<br>
