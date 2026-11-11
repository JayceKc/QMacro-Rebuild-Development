$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$project=if(Test-Path -LiteralPath (Join-Path $taskRoot 'programs\05.json')){$taskRoot}else{Join-Path $taskRoot 'outputs\QMacro-Rebuild-Development'}
$stage=Join-Path $taskRoot 'work\qmacro-analysis-copy-bridge\staging'
if(-not (Test-Path -LiteralPath $stage)){
 $stage=Join-Path $project 'bin\fishing-guest'
 $null=New-Item -ItemType Directory -Path $stage -Force
}
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
$runtime=Join-Path $project 'bin\QMacro.Rebuild.Runtime.dll'
$sources=@('QMacroFishingSuffixGuestTest.cs','QMacroFishingGuestTest.cs','FishingEvidenceDigests.cs',
 'QMacroBattleFormGuestTest.cs','BattleScanDigests.cs','QMacroCallbackGuestTest.cs','CallbackProgramDigests.cs') |
 ForEach-Object {Join-Path $PSScriptRoot $_}
& $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$runtime" /main:FishingSuffixGuestTest "/out:$stage\QMacroFishingSuffixGuestTest.exe" $sources
if($LASTEXITCODE){throw 'Fishing suffix guest fixture compilation failed'}
