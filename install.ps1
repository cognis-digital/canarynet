# Comprehensive installer for cognis-digital/canarynet (Windows PowerShell).
# Tries: pipx -> uv -> pip (git+https) -> from source.
# canarynet is source-available and not on PyPI; all paths install from GitHub.
$ErrorActionPreference = "Stop"
$Repo = "canarynet"
$Url  = "git+https://github.com/cognis-digital/canarynet.git"
$Git  = "https://github.com/cognis-digital/canarynet.git"
function Say($m) { Write-Host "[$Repo] $m" -ForegroundColor Magenta }
function Have($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }

if (-not (Have python) -and -not (Have py)) {
  Say "Python 3.9+ is required but was not found. Install Python first."; exit 1
}
if (Have pipx) {
  Say "Installing with pipx (isolated, recommended)..."
  pipx install $Url; if ($LASTEXITCODE -eq 0) { Say "Done. Run: canarynet"; exit 0 }
}
if (Have uv) {
  Say "Installing with uv..."
  uv tool install $Url; if ($LASTEXITCODE -eq 0) { Say "Done. Run: canarynet"; exit 0 }
}
if (Have pip) {
  Say "Installing with pip (user site)..."
  pip install --user $Url; if ($LASTEXITCODE -eq 0) { Say "Done. Run: canarynet"; exit 0 }
}
Say "No packaging tool worked; falling back to a source clone."
$Tmp = Join-Path $env:TEMP "$Repo-src"
git clone --depth 1 $Git $Tmp
Say "Cloned to $Tmp - run: cd $Tmp; python -m pip install ."
