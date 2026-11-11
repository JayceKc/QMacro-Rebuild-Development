$ErrorActionPreference='Stop'
$lab='C:\Users\Public\Documents\QMacroLab'
$process=Start-Process -FilePath (Join-Path $lab 'QMacroGatheringWalkGuestTest.exe') -WindowStyle Hidden -PassThru
if(-not $process.WaitForExit(35000)){Stop-Process -Id $process.Id -Force;throw 'Gathering walk fixture timed out'}
if($process.ExitCode -ne 0){throw 'Gathering walk failed; inspect original-gathering-walk.json before retrying'}
