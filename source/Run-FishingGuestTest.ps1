$ErrorActionPreference='Stop'
$lab='C:\Users\Public\Documents\QMacroLab'
$fixture=Join-Path $lab 'QMacroFishingGuestTest.exe'
$process=Start-Process -FilePath $fixture -WindowStyle Hidden -PassThru
if(-not $process.WaitForExit(35000)){Stop-Process -Id $process.Id -Force;throw 'Fishing fixture exceeded its guest bound'}
$report=Join-Path $lab 'original-fishing-vm-test.json'
if(-not (Test-Path -LiteralPath $report)){throw 'Fishing fixture did not create a report'}
if($process.ExitCode -ne 0){throw 'Fishing fixture failed; inspect its report before retrying'}
