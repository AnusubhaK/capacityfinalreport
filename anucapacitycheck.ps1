$ClusterName = $args[0]
Get-Cluster -Name $ClusterName |
Get-VMHost|
Select Name,
@{N='Total CPU(GHz)';E={[math]::Round($_.CpuTotalMhz/1000,2)}},
@{N='Total CPU(/Core)';E={$_.NumCpu}},
#@{N='Clock Speed';E={[math]::Round($_.CpuTotalMhz/(1000*$_.NumCpu),2)}},
@{N='Used CPU(GHz)';E={[math]::Round($_.CpuUsageMhz/1000,2)}},
@{N='Free CPU(GHz)';E={[math]::Round(($_.CpuTotalMhz - $_.CpuUsageMhz)/1000,2)}},
@{N='Free CPU(/Core)';E={[math]::Round(((($_.CpuTotalMhz - $_.CpuUsageMhz)/1000)/($_.CpuTotalMhz/(1000*$_.NumCpu))),0)}},
@{N='Total Memory(GB)';E={[math]::Round($_.MemoryTotalGB,2)}},
#@{N='Memory Used GB';E={[math]::Round($_.MemoryUsageGB,2)}},
@{N='Free Memory(GB)';E={[math]::Round(($_.MemoryTotalGB - $_.MemoryUsageGB),2)}} |
Export-Csv -Path C:\report.csv -NoTypeInformation -UseCulture
