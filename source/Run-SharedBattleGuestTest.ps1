$ErrorActionPreference='Stop'
$lab='C:\Users\Public\Documents\QMacroLab'
foreach($module in @('01','03','06')){
 $process=Start-Process -FilePath (Join-Path $lab 'QMacroSharedBattleGuestTest.exe') -ArgumentList $module -WindowStyle Hidden -PassThru
 if(-not $process.WaitForExit(12000)){Stop-Process -Id $process.Id -Force;throw "Battle fixture timed out for module $module"}
 if($process.ExitCode -ne 0){throw "Battle fixture failed for module $module. Inspect saved output."}
}
