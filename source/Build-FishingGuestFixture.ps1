$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$project=Join-Path $taskRoot 'outputs\QMacro-Rebuild-Development'
$guestOutput=Join-Path $taskRoot 'outputs\fishing-recovery\guest'
$null=New-Item -ItemType Directory -Path $guestOutput -Force
$programHash=(Get-FileHash -LiteralPath (Join-Path $project 'programs\05.json') -Algorithm SHA256).Hash.ToLowerInvariant()
$casesHash=(Get-FileHash -LiteralPath (Join-Path $project 'data\fishing-cases.json') -Algorithm SHA256).Hash.ToLowerInvariant()
$digest='public static class FishingEvidenceDigests {public const string Program="'+$programHash+'";public const string Cases="'+$casesHash+'";}'
$digestPath=Join-Path $PSScriptRoot 'FishingEvidenceDigests.cs'
[IO.File]::WriteAllText($digestPath,$digest,[Text.UTF8Encoding]::new($false))
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
$executable=Join-Path $guestOutput 'QMacroFishingGuestTest.exe'
$runtime=Join-Path $project 'bin\QMacro.Rebuild.Runtime.dll'
& $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$runtime" /main:FishingGuestTest "/out:$executable" (Join-Path $PSScriptRoot 'QMacroFishingGuestTest.cs') (Join-Path $PSScriptRoot 'QMacroCallbackGuestTest.cs') (Join-Path $PSScriptRoot 'CallbackProgramDigests.cs') $digestPath
if($LASTEXITCODE -ne 0){throw 'Fishing fixed-guest fixture compilation failed'}
Copy-Item -LiteralPath $runtime -Destination (Join-Path $guestOutput 'QMacro.Rebuild.Runtime.dll') -Force
Copy-Item -LiteralPath (Join-Path $project 'programs\05.json') -Destination (Join-Path $guestOutput '05.json') -Force
Copy-Item -LiteralPath (Join-Path $project 'data\fishing-cases.json') -Destination (Join-Path $guestOutput 'fishing-cases.json') -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Run-FishingGuestTest.ps1') -Destination (Join-Path $guestOutput 'Run-FishingGuestTest.ps1') -Force
Write-Output 'Compiled fixed-guest fixture only; original bodies were not run on this host.'
