$ErrorActionPreference='Stop'
$lab='C:\Users\Public\Documents\QMacroLab'
$process=Start-Process -FilePath (Join-Path $lab 'QMacroGatheringMainGuestTest.exe') -WindowStyle Hidden -PassThru
if(-not $process.WaitForExit(45000)){Stop-Process -Id $process.Id -Force;throw 'Gathering main suffix fixture timed out'}
if($process.ExitCode -ne 0){throw 'Gathering main suffix failed; inspect original-gathering-main.json before retrying'}
