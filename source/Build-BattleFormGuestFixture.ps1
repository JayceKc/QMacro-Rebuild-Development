$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$project=if(Test-Path -LiteralPath (Join-Path $taskRoot 'programs\01.json')){$taskRoot}else{Join-Path $taskRoot 'outputs\QMacro-Rebuild-Development'}
$stage=Join-Path $taskRoot 'work\qmacro-analysis-copy-bridge\staging'
if(-not (Test-Path -LiteralPath $stage)){
 $stage=Join-Path $project 'bin\battle-guest'
 $null=New-Item -ItemType Directory -Path $stage -Force
}
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
$runtime=Join-Path $project 'bin\QMacro.Rebuild.Runtime.dll'
$sources=@('QMacroBattleFormGuestTest.cs','QMacroCallbackGuestTest.cs','CallbackProgramDigests.cs','BattleScanDigests.cs') |
 ForEach-Object {Join-Path $PSScriptRoot $_}
& $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$runtime" /main:BattleFormGuestTest "/out:$stage\QMacroBattleFormGuestTest.exe" $sources
if($LASTEXITCODE){throw 'Form1 guest fixture compilation failed'}
