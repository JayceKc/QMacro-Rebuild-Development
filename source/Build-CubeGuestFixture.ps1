$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$project=if(Test-Path -LiteralPath (Join-Path $taskRoot 'programs\07.json')){$taskRoot}else{Join-Path $taskRoot 'outputs\QMacro-Rebuild-Development'}
$stage=Join-Path $taskRoot 'work\qmacro-analysis-copy-bridge\staging'
if(-not (Test-Path -LiteralPath $stage)){$stage=Join-Path $project 'bin\cube-guest';$null=New-Item -ItemType Directory -Path $stage -Force}
$programHash=(Get-FileHash -LiteralPath (Join-Path $project 'programs\07.json') -Algorithm SHA256).Hash.ToLowerInvariant()
$casesHash=(Get-FileHash -LiteralPath (Join-Path $project 'data\cube-cases.json') -Algorithm SHA256).Hash.ToLowerInvariant()
$caseCount=((Get-Content -LiteralPath (Join-Path $project 'data\cube-cases.json') -Raw -Encoding UTF8 | ConvertFrom-Json).cases).Count
$digest='public static class CubeDigests {public const string Program="'+$programHash+'";public const string Cases="'+$casesHash+'";public const int CaseCount='+$caseCount+';}'
$digestPath=Join-Path $PSScriptRoot 'CubeDigests.cs'
[IO.File]::WriteAllText($digestPath,$digest,[Text.UTF8Encoding]::new($false))
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
$runtime=Join-Path $project 'bin\QMacro.Rebuild.Runtime.dll'
& $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$runtime" /main:CubeGuestTest "/out:$stage\QMacroCubeGuestTest.exe" (Join-Path $PSScriptRoot 'QMacroCubeGuestTest.cs') (Join-Path $PSScriptRoot 'QMacroCallbackGuestTest.cs') (Join-Path $PSScriptRoot 'CallbackProgramDigests.cs') $digestPath
if($LASTEXITCODE -ne 0){throw 'Cube guest fixture compilation failed'}
Write-Output 'Compiled fixed-guest fixture only; original source was not executed on this host.'
