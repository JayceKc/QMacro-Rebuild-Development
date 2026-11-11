param([switch]$Test)
$ErrorActionPreference='Stop'
$developmentRoot=$PSScriptRoot
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
if(-not (Test-Path -LiteralPath $compiler)){throw '.NET Framework x86 C# compiler is unavailable'}
$sourceRoot=Join-Path $developmentRoot 'source'
$outputRoot=Join-Path $developmentRoot 'bin'
$null=New-Item -ItemType Directory -Path $outputRoot -Force
$sourceNames=@('QMacroVbsEngine.cs','QMacroVm.cs','QMacroDryRunHost.cs','QMacroProgramReader.cs','QMacroVision.cs','QMacroScreenCapture.cs','QMacroAssetResolver.cs','QMacroBuiltinColor.cs','QMacroBuiltinPicture.cs','QMacroBuiltinVisionService.cs')
$sources=@($sourceNames | ForEach-Object {Join-Path $sourceRoot $_})
$libraryPath=Join-Path $outputRoot 'QMacro.Rebuild.Runtime.dll'
& $compiler /nologo /target:library /platform:x86 /reference:System.Web.Extensions.dll "/out:$libraryPath" @sources
if($LASTEXITCODE -ne 0){throw 'Runtime compilation failed'}
Write-Output "Built: $libraryPath"
$uiPath=Join-Path $outputRoot 'QMacro-繁體介面預覽.exe'
$uiSources=@((Join-Path $sourceRoot 'QMacroUiPreview.cs'),(Join-Path $sourceRoot 'QMacroSettings10.cs'))
& $compiler /nologo /target:winexe /platform:x86 /reference:System.Web.Extensions.dll /reference:System.Windows.Forms.dll /reference:System.Drawing.dll "/out:$uiPath" @uiSources
if($LASTEXITCODE -ne 0){throw 'Unicode UI preview compilation failed'}
Copy-Item -LiteralPath $uiPath -Destination (Join-Path $developmentRoot 'QMacro-繁體介面預覽.exe') -Force
Write-Output "Built: $uiPath"
if($Test){
 $testSource=Join-Path $sourceRoot 'QMacroVmSelfTest.cs'
 $testPath=Join-Path $outputRoot 'QMacro.OwnFixtureTest.exe'
 & $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll /main:VmSelfTest "/out:$testPath" @sources $testSource
 if($LASTEXITCODE -ne 0){throw 'Owned test compilation failed'}
 $reportPath=Join-Path $developmentRoot 'verification\local-vm-self-test.json'
 # This executable runs fixed, owned fixtures; it does not load programs/*.json.
 $quotedReport='"'+$reportPath+'"'
 $testProcess=Start-Process -FilePath $testPath -ArgumentList $quotedReport -WindowStyle Hidden -PassThru
 if(-not $testProcess.WaitForExit(15000)){Stop-Process -Id $testProcess.Id -Force;throw 'Owned fixture test timed out'}
 if($testProcess.ExitCode -ne 0){throw "Owned fixture test failed; inspect $reportPath"}
 $report=Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
 if(-not $report.ok){throw 'Owned fixture report is not successful'}
 Write-Output "Owned fixture tests passed: $reportPath"
 $settingsPath=Join-Path $outputRoot 'QMacro.SettingsFixtureTest.exe'
 & $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/out:$settingsPath" (Join-Path $sourceRoot 'QMacroSettings10.cs') (Join-Path $sourceRoot 'QMacroSettings10SelfTest.cs')
 if($LASTEXITCODE -ne 0){throw 'Settings test compilation failed'}
 $settingsInput=Join-Path $developmentRoot 'verification\semantic-main10-verification.json'
 $settingsOutput=Join-Path $developmentRoot 'verification\settings10-semantic-comparison.json'
 $settingsProcess=Start-Process -FilePath $settingsPath -ArgumentList ('"'+$settingsInput+'"'),('"'+$settingsOutput+'"') -WindowStyle Hidden -PassThru
 if(-not $settingsProcess.WaitForExit(15000)){Stop-Process -Id $settingsProcess.Id -Force;throw 'Owned settings test timed out'}
 if($settingsProcess.ExitCode -ne 0){throw 'Settings model did not match the guest reconstruction fixtures'}
 Write-Output "Settings comparison passed: $settingsOutput"
 $visionPath=Join-Path $outputRoot 'QMacro.VisionFixtureTest.exe'
 & $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll /main:VisionSelfTest "/out:$visionPath" (Join-Path $sourceRoot 'QMacroVbsEngine.cs') (Join-Path $sourceRoot 'QMacroVision.cs') (Join-Path $sourceRoot 'QMacroScreenCapture.cs') (Join-Path $sourceRoot 'QMacroAssetResolver.cs') (Join-Path $sourceRoot 'QMacroVisionSelfTest.cs')
 if($LASTEXITCODE -ne 0){throw 'Vision test compilation failed'}
 $visionOutput=Join-Path $developmentRoot 'verification\csharp-vision-replay.json'
 $visionProcess=Start-Process -FilePath $visionPath -ArgumentList ('"'+$developmentRoot+'"'),('"'+$visionOutput+'"') -WindowStyle Hidden -PassThru
 if(-not $visionProcess.WaitForExit(30000)){Stop-Process -Id $visionProcess.Id -Force;throw 'Vision replay test timed out'}
 if($visionProcess.ExitCode -ne 0){throw 'C# vision backend differs from saved native observations'}
 Write-Output "Vision replay passed: $visionOutput"
 $builtinPath=Join-Path $outputRoot 'QMacro.BuiltinFixtureTest.exe'
 & $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll /main:BuiltinSelfTest "/out:$builtinPath" @sources (Join-Path $sourceRoot 'QMacroBuiltinSelfTest.cs')
 if($LASTEXITCODE -ne 0){throw 'Builtin color test compilation failed'}
 $builtinOutput=Join-Path $developmentRoot 'verification\csharp-builtin-color-replay.json'
 $builtinProcess=Start-Process -FilePath $builtinPath -ArgumentList ('"'+$developmentRoot+'"'),('"'+$builtinOutput+'"') -WindowStyle Hidden -PassThru
 if(-not $builtinProcess.WaitForExit(15000)){Stop-Process -Id $builtinProcess.Id -Force;throw 'Builtin fixture test timed out'}
 if($builtinProcess.ExitCode -ne 0){throw "Builtin contract failed; inspect $builtinOutput"}
 Write-Output "Builtin color and VBS bridge passed: $builtinOutput"
 $readerPath=Join-Path $outputRoot 'QMacro.ProgramReaderFixtureTest.exe'
 & $compiler /nologo /target:exe /platform:x86 /reference:System.Web.Extensions.dll "/reference:$libraryPath" "/out:$readerPath" (Join-Path $sourceRoot 'QMacroProgramReaderSelfTest.cs')
 if($LASTEXITCODE -ne 0){throw 'Program reader test compilation failed'}
 $programDirectory=Join-Path $developmentRoot 'programs'
 $readerOutput=Join-Path $developmentRoot 'verification\vm-program-load-verification.json'
 $readerProcess=Start-Process -FilePath $readerPath -ArgumentList ('"'+$programDirectory+'"'),('"'+$readerOutput+'"') -WindowStyle Hidden -PassThru
 if(-not $readerProcess.WaitForExit(15000)){Stop-Process -Id $readerProcess.Id -Force;throw 'Program reader test timed out'}
 if($readerProcess.ExitCode -ne 0){throw 'Current runtime rejected the original eight preserved programs'}
 Write-Output "Eight-program load check passed: $readerOutput"
}
