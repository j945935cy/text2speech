# text2speech

## Word Builder 1200

一個可直接開啟的前端小工具，用 1200 個常用英文單字做字首、字根、字尾的拼字與發音練習。

## 功能

- 從 1200 個英文高頻字中建立單字庫
- 以規則化方式拆成 `prefix + root + suffix`
- 可選字首、輸入字根、選字尾來組字
- 顯示符合條件的真實單字
- 使用瀏覽器 `SpeechSynthesis` 朗讀英文發音

## 使用方式

重新產生資料：

```powershell
python tools/generate_dataset.py
```

開啟：

- GitHub Pages: <https://j945935cy.github.io/text2speech/>
- Repo 檔案位置：`app/index.html`

## 資料說明

- 單字來源：本機 `wordfreq` 套件產出的英文高頻詞
- 拆解方式：教學導向的規則化拆分
- 注意：這不是嚴格的字源學或詞源辭典分析
