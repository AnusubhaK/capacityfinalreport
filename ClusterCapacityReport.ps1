function Get-ClusterCapacityCheck {

    [CmdletBinding()]
    param(
    [Parameter(Position=0,Mandatory=$true,HelpMessage="Name of the cluster to test",
    ValueFromPipeline=$True,ValueFromPipelineByPropertyName=$true)]
    [System.String]
    $ClusterName
    )
    
    begin {
    #$Finish = (Get-Date -Hour 0 -Minute 0 -Second 0)
    #$Start = $Finish.AddDays(-1).AddSeconds(1)
    
    New-VIProperty -Name FreeSpaceGB -ObjectType Datastore -Value {
    param($ds)
    [Math]::Round($ds.FreeSpaceMb/1KB,0)
    } -Force
    
    }
    
    process {
    
    $Cluster = Get-Cluster $ClusterName
    
    #$ClusterCPUCores = $Cluster.ExtensionData.Summary.NumCpuCores
    #$ClusterEffectiveMemoryGB = [math]::round(($Cluster.ExtensionData.Summary.EffectiveMemory / 1KB),0)
    
    $ClusterVMs = $Cluster | Get-VM
    
    #$ClusterAllocatedvCPUs = ($ClusterVMs | Measure-Object -Property NumCPu -Sum).Sum
    #$ClusterAllocatedMemoryGB = [math]::round(($ClusterVMs | Measure-Object -Property MemoryMB -Sum).Sum / 1KB)
    
    #$ClustervCPUpCPURatio = [math]::round($ClusterAllocatedvCPUs / $ClusterCPUCores,2)
    #$ClusterActiveMemoryPercentage = [math]::round(($Cluster | Get-Stat -Stat mem.usage.average -Start $Start -Finish $Finish | Measure-Object -Property Value -Average).Average,0)
    
    $VMHost = $Cluster | Get-VMHost | Select-Object -Last 1
    $ClusterFreeDiskspaceGB = ($VMHost | Get-Datastore | Where-Object {$_.Extensiondata.Summary.MultipleHostAccess -eq $True} | Measure-Object -Property FreeSpaceGB -Sum).Sum
    $ClusterCPUUsageMHz = ($Cluster | Get-VMHost | Measure-Object -Property CpuUsageMhz -Sum).Sum
    $ClusterCPUTotalMHz = ($Cluster | Get-VMHost | Measure-Object -Property CpuTotalMhz -Sum).Sum
    $ClusterNumCPU = ($Cluster | Get-VMHost | Measure-Object -Property NumCpu -Sum).Sum
    $ClusterTotalMemory = [math]::Round(($Cluster | Get-VMHost | Measure-Object -Property MemoryTotalGB -Sum).Sum,0)
    $ClusterUsedMemory =[math]::Round(($Cluster | Get-VMHost | Measure-Object -Property MemoryUsageGB -Sum).Sum,0)
    
    $ClusterFreeCPUGHz = [math]::Round(($ClusterCPUTotalMHz - $ClusterCPUUsageMHz)/1000,0)
    $ClusterFreeCPUCore =[math]:: Round(($ClusterFreeCPUGHz/ ($ClusterCPUTotalMHz/(1000*$ClusterNumCPU))),0)
    $ClusterFreeMemoryGB = [math]::Round(($ClusterTotalMemory - $ClusterUsedMemory),0)

    New-Object -TypeName PSObject -Property @{
    Cluster = $Cluster.Name
    #ClusterCPUCores = $ClusterCPUCores
    #ClusterAllocatedvCPUs = $ClusterAllocatedvCPUs
    #ClustervCPUpCPURatio = $ClustervCPUpCPURatio
    #ClusterEffectiveMemoryGB = $ClusterEffectiveMemoryGB
    #ClusterAllocatedMemoryGB = $ClusterAllocatedMemoryGB
    #ClusterActiveMemoryPercentage = $ClusterActiveMemoryPercentage
    ClusterFreeDiskspaceGB = $ClusterFreeDiskspaceGB
    ClusterCPUUsageMHz = $ClusterCPUUsageMHz
    ClusterCPUTotalMHz = $ClusterCPUTotalMHz
    ClusterFreeCPUGHz = $ClusterFreeCPUGHz
    ClusterFreeCPUCore = $ClusterFreeCPUCore
    ClusterTotalMemory = $ClusterTotalMemory
    ClusterUsedMemory = $ClusterUsedMemory
    ClusterFreeMemoryGB = $ClusterFreeMemoryGB


    }
    }
    }
   
Get-Cluster | Get-ClusterCapacityCheck | Select-Object Cluster,ClusterFreeDiskspaceGB,ClusterFreeCPUCore,ClusterFreeMemoryGB
    
