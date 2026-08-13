# Starta AutomationMenu

$ReqPythonVersion = "3.14.6"
$PythonInstallerUrl = "https://www.python.org/ftp/python/$ReqPythonVersion/python-$ReqPythonVersion-amd64.exe"
$PythonExecLocation = "$( $env:APPDATA )\AutomationMenu\.venv"
$AutomationMenuRoot = "G:\AutomationTools\AutomationMenu"

$Desktop = [Environment]::GetFolderPath( "Desktop" )
$ShortcutPath = Join-Path $Desktop "AutomationMenu.lnk"

function Install-Python
{
    Write-Host "Downloading installation file"
    $DownloadPath = "$env:TEMP\python-installer.exe"

    Invoke-WebRequest -Uri $PythonInstallerUrl -OutFile $DownloadPath

    Write-Host "Perform silent installation"
    Start-Process $DownloadPath -ArgumentList @(
        "/quiet",
        "InstallAllUsers=1",
        "PrependPath=1",
        "Include_test=0"
    ) -Wait

    Remove-Item $DownloadPath -Force
}

function Install-PythonVenv
{
    <#
    .Synopsis Install a virtual environment that Python can run from
    This will be installed under user > AppData
    #>

    Write-Host "Creating run environment"
    python -m venv $PythonExecLocation

    & "$PythonExecLocation\Scripts\python.exe" -m pip install --upgrade pip
    & "$PythonExecLocation\Scripts\python.exe" -m pip install -r "$AutomationMenuRoot\requirements.txt"
}

function New-LaunchShortcut
{
    Write-Host "Creating Desktop shortcut"

    if ( -not ( Test-Path ( Join-Path -Path $AutomationMenuRoot -ChildPath "main.py" ) -ErrorAction Stop ) )
    {
        throw "AutomationMenu can not be found"
    }

    $WshShell = New-Object -ComObject WScript.Shell
    $ShortCut = $WshShell.CreateShortcut( $ShortcutPath )

    $ShortCut.TargetPath = "python.exe"
    $MainPyPath = ( Join-Path -Path $AutomationMenuRoot -ChildPath "main.py" )
    $ShortCut.Arguments = "`"$MainPyPath`""
    $ShortCut.WorkingDirectory = $AutomationMenuRoot
    $ShortCut.IconLocation = ( Join-Path -Path $AutomationMenuRoot -ChildPath "\automation_menu\assets\automation_menu.ico" )

    $ShortCut.Save()

    Write-Host "Shortcut was created on Desktop"
}

function Test-PythonInstalled
{
    try
    {
        $pvs = [Version] ( ( ( ( py -V  ) -split "\s" )[ 1 ] -split "\." ) -join '.' )
        $rpvs = [Version] $ReqPythonVersion

        return $rpvs -le $pvs
    }
    catch
    {
        return $false
    }
}

if ( -not ( Test-PythonInstalled ) )
{
    Install-Python
}

if ( -not ( Test-Path $PythonExecLocation ) )
{
    Write-Host "Could not find an run environment`nWill install here: $PythonExecLocation"
    Install-PythonVenv
}
else
{
    Write-Host "Python installed and run environment created"
}

if ( -not ( Test-Path $ShortcutPath ) )
{
    Write-Host "Found no Desktop shortcut."

    New-LaunchShortcut
}

Write-Host "Installation done"
