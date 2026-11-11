$ErrorActionPreference='Stop'
$lab='C:\Users\Public\Documents\QMacroLab'
$process=Start-Process -FilePath (Join-Path $lab 'QMacroGatheringWorkerGuestTest.exe') -WindowStyle Hidden -PassThru
if(-not $process.WaitForExit(35000)){Stop-Process -Id $process.Id -Force;throw 'Gathering worker fixture timed out'}
if($process.ExitCode -ne 0){throw 'Gathering worker failed; inspect original-gathering-worker.json before retrying'}
