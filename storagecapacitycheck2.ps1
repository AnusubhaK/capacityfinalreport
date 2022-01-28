function Get-ClusterCapacityCheck {

[CmdletBinding()]
param(
[Parameter(Position=0,Mandatory=$true,HelpMessage="Name of the cluster to test",
ValueFromPipeline=$True,ValueFromPipelineByPropertyName=$true)]
[System.String]
$ClusterName
)

begin {
$Finish = (Get-Date -Hour 0 -Minute 0 -Second 0)
$Start = $Finish.AddDays(-1).AddSeconds(1)

New-VIProperty -Name FreeSpaceGB -ObjectType Datastore -Value {
param($ds)
[Math]::Round($ds.FreeSpaceMb/1KB,0)
} -Force

}

process {

$Cluster = Get-Cluster $ClusterName

$ClusterCPUCores = $Cluster.ExtensionData.Summary.NumCpuCores
$ClusterEffectiveMemoryGB = [math]::round(($Cluster.ExtensionData.Summary.EffectiveMemory / 1KB),0)

$ClusterVMs = $Cluster | Get-VM

$ClusterAllocatedvCPUs = ($ClusterVMs | Measure-Object -Property NumCPu -Sum).Sum
$ClusterAllocatedMemoryGB = [math]::round(($ClusterVMs | Measure-Object -Property MemoryMB -Sum).Sum / 1KB)

$ClustervCPUpCPURatio = [math]::round($ClusterAllocatedvCPUs / $ClusterCPUCores,2)
$ClusterActiveMemoryPercentage = [math]::round(($Cluster | Get-Stat -Stat mem.usage.average -Start $Start -Finish $Finish | Measure-Object -Property Value -Average).Average,0)

$VMHost = $Cluster | Get-VMHost | Select-Object -Last 1
$ClusterFreeDiskspaceGB = ($VMHost | Get-Datastore | Where-Object {$_.Extensiondata.Summary.MultipleHostAccess -eq $True} | Measure-Object -Property FreeSpaceGB -Sum).Sum

New-Object -TypeName PSObject -Property @{
Cluster = $Cluster.Name
ClusterCPUCores = $ClusterCPUCores
ClusterAllocatedvCPUs = $ClusterAllocatedvCPUs
ClustervCPUpCPURatio = $ClustervCPUpCPURatio
ClusterEffectiveMemoryGB = $ClusterEffectiveMemoryGB
ClusterAllocatedMemoryGB = $ClusterAllocatedMemoryGB
ClusterActiveMemoryPercentage = $ClusterActiveMemoryPercentage
ClusterFreeDiskspaceGB = $ClusterFreeDiskspaceGB
}
}
}
Get-Cluster | Get-ClusterCapacityCheck | Select-Object Cluster,ClusterCPUCores,ClusterAllocatedvCPUs,ClustervCPUpCPURatio,ClusterEffectiveMemoryGB,ClusterAllocatedMemoryGB,ClusterActiveMemoryPercentage,ClusterFreeDiskspaceGB
