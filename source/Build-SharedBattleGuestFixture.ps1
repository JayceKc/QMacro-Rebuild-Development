$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$project=if(Test-Path -LiteralPath (Join-Path $taskRoot 'programs\01.json')){$taskRoot}else{Join-Path $taskRoot 'outputs\QMacro-Rebuild-Development'}
$stage=Join-Path $taskRoot 'work\qmacro-analysis-copy-bridge\staging'
if(-not (Test-Path -LiteralPath $stage)){$stage=Join-Path $project 'bin\battle-guest';$null=New-Item -ItemType Directory -Path $stage -Force}
$programs=@()
$cases=@()
foreach($module in @('01','03','06')){
 $p=(Get-FileHash -LiteralPath (Join-Path $project "programs\$module.json") -Algorithm SHA256).Hash.ToLowerInvariant()
 $c=(Get-FileHash -LiteralPath (Join-Path $project "data\battle-$module-cases.json") -Algorithm SHA256).Hash.ToLowerInvariant()
 $programs+=('{"'+$module+'","'+$p+'"}')
 $cases+=('{"'+$module+'","'+$c+'"}')
}
$digest='using System.Collections.Generic; public static class SharedBattleDigests { public static readonly Dictionary<string,string> Programs=new Dictionary<string,string>{'+($programs -join ',')+'}; public static readonly Dictionary<string,string> Cases=new Dictionary<string,string>{'+($cases -join ',')+'}; }'
$digestPath=Join-Path $PSScriptRoot 'SharedBattleDigests.cs'
[IO.File]::WriteAllText($digestPath,$digest,[Text.UTF8Encoding]::new($false))
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
$runtime=Join-Path $project 'bin\QMacro.Rebuild.Runtime.dll'
& $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$runtime" /main:SharedBattleGuestTest "/out:$stage\QMacroSharedBattleGuestTest.exe" (Join-Path $PSScriptRoot 'QMacroSharedBattleGuestTest.cs') (Join-Path $PSScriptRoot 'QMacroCallbackGuestTest.cs') (Join-Path $PSScriptRoot 'CallbackProgramDigests.cs') $digestPath
if($LASTEXITCODE -ne 0){throw 'Shared battle guest fixture compilation failed'}
