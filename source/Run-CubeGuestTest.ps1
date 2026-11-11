$ErrorActionPreference='Stop'
$lab='C:\Users\Public\Documents\QMacroLab'
$process=Start-Process -FilePath (Join-Path $lab 'QMacroCubeGuestTest.exe') -WindowStyle Hidden -PassThru
if(-not $process.WaitForExit(45000)){Stop-Process -Id $process.Id -Force;throw 'Cube fixture timed out'}
if($process.ExitCode -ne 0){throw 'Cube fixture failed; inspect original-cube-routines.json before retrying'}
