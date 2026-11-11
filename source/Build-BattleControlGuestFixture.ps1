param([switch]$Recovery,[switch]$Restart,[switch]$Routes,[switch]$Tail,[switch]$Scan,[switch]$RootSuffix,[switch]$Small)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$project=if(Test-Path -LiteralPath (Join-Path $taskRoot 'programs\01.json')){$taskRoot}else{Join-Path $taskRoot 'outputs\QMacro-Rebuild-Development'}
$stage=Join-Path $taskRoot 'work\qmacro-analysis-copy-bridge\staging'
if(-not (Test-Path -LiteralPath $stage)){$stage=Join-Path $project 'bin\battle-guest';$null=New-Item -ItemType Directory -Path $stage -Force}
$programs=@()
$cases=@()
if(@($Recovery,$Restart,$Routes,$Tail,$Scan,$RootSuffix,$Small).Where({$_}).Count -gt 1){throw 'Choose one fixture family'}
$caseRoot=if($Recovery -or $Restart -or $Routes -or $Tail -or $Scan -or $RootSuffix -or $Small){Join-Path $PSScriptRoot 'battle-recovery-candidates'}else{Join-Path $project 'data'}
if(-not (Test-Path -LiteralPath $caseRoot)){$caseRoot=Join-Path $project 'data'}
$variant=if($Small){'Small'}elseif($RootSuffix){'Root'}elseif($Scan){'Scan'}elseif($Tail){'Tail'}elseif($Routes){'Routes'}elseif($Restart){'Restart'}elseif($Recovery){'Recovery'}else{'Control'}
$family=$variant.ToLowerInvariant()
$modules=if($Small){@('09','10')}elseif($RootSuffix){@('01','06')}else{@('01','03','06')}
foreach($module in $modules){
 $p=(Get-FileHash -LiteralPath (Join-Path $project "programs\$module.json") -Algorithm SHA256).Hash.ToLowerInvariant()
 $c=(Get-FileHash -LiteralPath (Join-Path $caseRoot "battle-$family-$module-cases.json") -Algorithm SHA256).Hash.ToLowerInvariant()
 $programs+=('{"'+$module+'","'+$p+'"}')
 $cases+=('{"'+$module+'","'+$c+'"}')
}
$digest='using System.Collections.Generic; public static class SharedBattleDigests { public static readonly Dictionary<string,string> Programs=new Dictionary<string,string>{'+($programs -join ',')+'}; public static readonly Dictionary<string,string> Cases=new Dictionary<string,string>{'+($cases -join ',')+'}; }'
$digestPath=Join-Path $PSScriptRoot "Battle${variant}Digests.cs"
[IO.File]::WriteAllText($digestPath,$digest,[Text.UTF8Encoding]::new($false))
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
$runtime=Join-Path $project 'bin\QMacro.Rebuild.Runtime.dll'
& $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$runtime" /main:SharedBattleGuestTest "/out:$stage\QMacroBattle${variant}GuestTest.exe" (Join-Path $PSScriptRoot 'QMacroSharedBattleGuestTest.cs') (Join-Path $PSScriptRoot 'QMacroCallbackGuestTest.cs') (Join-Path $PSScriptRoot 'CallbackProgramDigests.cs') $digestPath
if($LASTEXITCODE -ne 0){throw 'Shared battle guest fixture compilation failed'}
if($Small){
 & $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$runtime" /main:BattleFormGuestTest "/out:$stage\QMacroSkillIslandHostGuestTest.exe" (Join-Path $PSScriptRoot 'QMacroBattleFormGuestTest.cs') (Join-Path $PSScriptRoot 'QMacroCallbackGuestTest.cs') (Join-Path $PSScriptRoot 'CallbackProgramDigests.cs') $digestPath
 if($LASTEXITCODE){throw 'Skill/island host guest fixture compilation failed'}
}
