$report = Get-VMHost -Name MyEsx -PipelineVariable sa-esxi-05.vclass.local | Get-Datastore |
Select @{N='VMHost';E={$esx.Name}},Name,FreeSpaceMB,CapacityMB

$report += '' | Select @{N='VMHost';E={'Total'}},@{N='Name';E={''}},
    @{N='FreeSpaceMB';E={($report | Measure-Object -Property FreeSpaceMb -Sum).Sum}},
    @{N='CapacityMB';E={($report | Measure-Object -Property CapacityMB -Sum).Sum}}

$report
