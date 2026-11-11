$ErrorActionPreference='Stop'
$lab='C:\Users\Public\Documents\QMacroLab'
$process=Start-Process -FilePath (Join-Path $lab 'QMacroGatheringRoutinesGuestTest.exe') -WindowStyle Hidden -PassThru
if(-not $process.WaitForExit(45000)){Stop-Process -Id $process.Id -Force;throw 'Gathering routines fixture timed out'}
if($process.ExitCode -ne 0){throw 'Gathering routines failed; inspect original-gathering-routines.json before retrying'}
