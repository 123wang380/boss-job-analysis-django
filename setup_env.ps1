<#
setup_env.ps1
PowerShell helper script to create a virtual environment and install packages from requirements.txt.
Usage examples (from project root):
  .\setup_env.ps1            # create .venv and install using default PyPI
  .\setup_env.ps1 -UseTunaMirror  # use TUNA mirror (faster in China)
#>
param(
    [switch]$UseTunaMirror
)

$ErrorActionPreference = 'Stop'
$venvName = '.venv'

Write-Host "Creating virtual environment '$venvName'..."
python -m venv $venvName

Write-Host "Allowing script execution in this session (temporary)..."
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null

Write-Host "Activating virtual environment..."
& "$venvName\Scripts\Activate.ps1"

Write-Host "Upgrading pip, setuptools and wheel..."
python -m pip install --upgrade pip setuptools wheel

$req = Join-Path -Path (Get-Location) -ChildPath 'requirements.txt'
if (-Not (Test-Path $req)) {
    Write-Error "requirements.txt not found in current directory: $req"
    exit 1
}

$installArgs = "--prefer-binary -r `"$req`""
if ($UseTunaMirror) {
    Write-Host "Installing packages using TUNA mirror (may be faster) -- this may take several minutes..."
    pip install $installArgs -i https://pypi.tuna.tsinghua.edu.cn/simple
} else {
    Write-Host "Installing packages from PyPI (may be slower) -- this may take several minutes..."
    pip install $installArgs
}

Write-Host "Installation finished. To activate the virtual environment later run:`n  .\$venvName\Scripts\Activate.ps1"

