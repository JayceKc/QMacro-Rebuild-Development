$ErrorActionPreference='Stop'
$lab='C:\Users\Public\Documents\QMacroLab'
$process=Start-Process -FilePath (Join-Path $lab 'QMacroColorListOracle.exe') -WindowStyle Hidden -PassThru
if(-not $process.WaitForExit(20000)){Stop-Process -Id $process.Id -Force;throw 'Color-list oracle exceeded guest bound'}
if($process.ExitCode -ne 0){throw 'Color-list oracle failed; inspect original-color-list-oracle.json'}
