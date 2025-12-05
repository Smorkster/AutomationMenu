<#  ScriptInfo
# Description - Test message written to stderr then stdout in PowerShell
# Synopsis - Test error and output in PS
# State - Prod
# DisableMinimizeOnRunning
# Author - Smorkster (smorkster)
ScriptInfoEnd #>

Write-Output "$( 1+1 )"
Wait-Debugger
Write-Error 'Test Error'
Write-Output 'Test Output'