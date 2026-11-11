# QMacro 繁體重建開發包

這份開發包收錄八組 QMacro 腳本的保留指令、繁體流程解讀、重建程式碼及驗證資料。可用它查閱原始記錄、預覽繁體介面，以及重跑已建立的離線測試。

## 從哪裡開始

- **看腳本流程**。在 `readable/` 選擇模組，先讀 `流程_逐筆.txt`，再依記錄編號查 `函式-Lxxxxx.qms.txt`、`介面事件.md` 或 `缺失記錄.json`。[目錄結構](目錄結構.md)
- **看繁體介面**。在 Windows 開啟根目錄的 `QMacro-繁體介面預覽.exe`，可查看卡號版與帳戶版的介面及設定。[測試方式](測試方式.md)
- **核對還原進度**。依各模組查看原始記錄、候選覆蓋與驗證範圍。[整套還原進度](verification/完整還原進度.md)

## 離線驗證

在解壓後的 `QMacro-Rebuild-Development` 根目錄開啟 PowerShell。Python 測試使用標準函式庫，開發包已用 Python 3.13 驗證。

```powershell
python -X utf8 -m unittest discover -s source -p "test_*.py"
```

重播三個戰鬥模組從設定到主迴圈的流程，可執行以下命令。案例會記錄讀取的設定、走過的分支、缺失停點和回跳位置。[戰鬥入口對照](analysis/initialization/01-03-06-從原入口到主迴圈.md)

```powershell
python -X utf8 source/replay_battle_entry_join.py
```

編譯 C# 核心與介面預覽並執行測試，需要 Windows 的 .NET Framework x86 C# 編譯器。建置產物在 `bin/`，測試報告在 `verification/`。[建置腳本](Build-Development.ps1)

```powershell
.\Build-Development.ps1 -Test
```

## 目前範圍

八組腳本均有逐筆資料與子程序索引。原始資料含 3,261 筆缺失位置，部分位置已有候選操作或分支，相關依據可回查原記錄和字串池編號。完整遊戲流程、外掛行為及執行緒時序仍待逐項驗證。[程式清單](programs/manifest.json) · [驗證帳冊](verification/full-objective-ledger.json)
