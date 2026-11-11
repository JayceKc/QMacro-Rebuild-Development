$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$project=if(Test-Path -LiteralPath (Join-Path $taskRoot 'programs\08.json')){$taskRoot}else{Join-Path $taskRoot 'outputs\QMacro-Rebuild-Development'}
$stage=Join-Path $taskRoot 'work\qmacro-analysis-copy-bridge\staging'
if(-not (Test-Path -LiteralPath $stage)){$stage=Join-Path $project 'bin\gathering-worker-guest';$null=New-Item -ItemType Directory -Path $stage -Force}
$programHash=(Get-FileHash -LiteralPath (Join-Path $project 'programs\08.json') -Algorithm SHA256).Hash.ToLowerInvariant()
$casesHash=(Get-FileHash -LiteralPath (Join-Path $project 'data\gathering-worker-cases.json') -Algorithm SHA256).Hash.ToLowerInvariant()
$digest='public static class GatheringWorkerDigests {public const string Program="'+$programHash+'";public const string Cases="'+$casesHash+'";}'
$digestPath=Join-Path $PSScriptRoot 'GatheringWorkerDigests.cs'
[IO.File]::WriteAllText($digestPath,$digest,[Text.UTF8Encoding]::new($false))
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
$runtime=Join-Path $project 'bin\QMacro.Rebuild.Runtime.dll'
& $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$runtime" /main:GatheringWorkerGuestTest "/out:$stage\QMacroGatheringWorkerGuestTest.exe" (Join-Path $PSScriptRoot 'QMacroGatheringWorkerGuestTest.cs') (Join-Path $PSScriptRoot 'QMacroCallbackGuestTest.cs') (Join-Path $PSScriptRoot 'CallbackProgramDigests.cs') $digestPath
if($LASTEXITCODE -ne 0){throw 'Gathering worker guest fixture compilation failed'}
Write-Output 'Compiled fixed-guest fixture only; original source was not executed on this host.'
