param([int]$WorkerId=13672)
$ErrorActionPreference='Stop'
$taskRoot=$PSScriptRoot
$watchState=Join-Path $taskRoot 'optimization_followup_state.json'
@{status='waiting_for_lods';worker=$WorkerId} | ConvertTo-Json | Set-Content -LiteralPath $watchState -Encoding utf8
$deadline=(Get-Date).AddHours(3)
while ((Get-Date) -lt $deadline) {
    try {
        $lodState=Get-Content -LiteralPath (Join-Path $taskRoot 'static_lod_optimization.json') -Raw | ConvertFrom-Json
        $jobState=Get-Content -LiteralPath (Join-Path $taskRoot 'author_worker_state.json') -Raw | ConvertFrom-Json
        if ($lodState.status -eq 'complete' -and $jobState.status -eq 'success') { break }
        if ($jobState.status -eq 'error') { throw ('Authoring failed: '+$jobState.error) }
    } catch {
        if ($_.Exception.Message -like 'Authoring failed:*') {
            @{status='error';message=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath $watchState -Encoding utf8
            exit 1
        }
    }
    Start-Sleep -Seconds 5
}
if ((Get-Date) -ge $deadline) { throw 'LOD authoring timeout' }
# The original warm worker has a thirty-minute idle limit. Restart only our headless process after its saved job.
$oldWorker=Get-CimInstance Win32_Process -Filter "ProcessId=$WorkerId" -ErrorAction SilentlyContinue
if ($oldWorker) {
    if ($oldWorker.CommandLine -notlike '*BlueprintAuthoring*optimization_author_fast.log*') { throw 'Unexpected worker process' }
    Stop-Process -Id $WorkerId -Force
}
@{script='scripts/finish_optimization_authoring.py'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'author_worker_request.json') -Encoding utf8
$editor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$project=Join-Path $taskRoot 'BlueprintAuthoring/BogotaVoxel.uproject'
$script=Join-Path $taskRoot 'scripts/author_worker.py'
$userDir=Join-Path $taskRoot 'AuthorCrosswalkUser'
$log=Join-Path $taskRoot 'optimization_followup.log'
$arguments='"'+$project+'" /Engine/Maps/Entry -ExecutePythonScript="'+$script+'" -nullrhi -nosound -unattended -NoSplash -NoLiveCoding -NoErrorReport -UserDir="'+$userDir+'" -abslog="'+$log+'"'
$newWorker=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
$newWorker.PriorityClass='AboveNormal'
@{status='authoring_followup';worker=$newWorker.Id;log=$log} | ConvertTo-Json | Set-Content -LiteralPath $watchState -Encoding utf8
