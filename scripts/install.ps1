param(
    [string]$Harness = ""
)

# Install the TYF skills, and place Windows launchers for the `tyf` helper on PATH.
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 codex
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 claude
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 cursor
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 C:\path\to\skills
#
# Set BIN_DIR to choose where the `tyf` launchers are written.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Src = Join-Path $Root "skills"
$BinDir = if ($env:BIN_DIR) { $env:BIN_DIR } else { Join-Path $HOME ".local\bin" }

function Resolve-Target([string]$Name) {
    switch ($Name) {
        "claude" { return (Join-Path $HOME ".claude\skills") }
        "codex" {
            if ($env:CODEX_HOME) {
                return (Join-Path $env:CODEX_HOME "skills")
            }
            return (Join-Path $HOME ".codex\skills")
        }
        "cursor" { return (Join-Path $HOME ".cursor\skills") }
        "" { return "" }
        default { return $Name }
    }
}

function Context-File-For([string]$Name) {
    switch ($Name) {
        "claude" { return "CLAUDE.md" }
        "codex" { return "AGENTS.md" }
        "cursor" { return "AGENTS.md" }
        default { return "CLAUDE.md / AGENTS.md / GEMINI.md" }
    }
}

$Target = Resolve-Target $Harness
if (-not $Target) {
    Write-Host "Pick a harness: claude | codex | cursor | <explicit path>"
    $Harness = Read-Host
    $Target = Resolve-Target $Harness
}

if (-not $Target) {
    throw "No target resolved. Aborting."
}

New-Item -ItemType Directory -Force -Path $Target | Out-Null
Write-Host "Installing TYF skills into: $Target"
$Count = 0
Get-ChildItem -Path $Src -Directory | ForEach-Object {
    $Destination = Join-Path $Target $_.Name
    if (Test-Path -LiteralPath $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    Copy-Item -LiteralPath $_.FullName -Destination $Destination -Recurse
    Write-Host "  installed: $($_.Name)"
    $script:Count += 1
}
Write-Host "  $Count skills installed."

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
$TyfPy = Join-Path $Root "scripts\tyf.py"
$EscapedRoot = $Root.Replace("'", "''")
$EscapedTyfPy = $TyfPy.Replace("'", "''")
$CmdPath = Join-Path $BinDir "tyf.cmd"
$Ps1Path = Join-Path $BinDir "tyf.ps1"

$Cmd = @"
@echo off
setlocal
set "TYF_PACK_ROOT=$Root"
where python >nul 2>nul
if not errorlevel 1 (
  python "$TyfPy" %*
) else (
  py "$TyfPy" %*
)
"@
Set-Content -LiteralPath $CmdPath -Value $Cmd -Encoding ASCII

$Ps1 = @"
`$env:TYF_PACK_ROOT = '$EscapedRoot'
`$python = Get-Command python -ErrorAction SilentlyContinue
if (`$python) {
    & `$python.Source '$EscapedTyfPy' @args
} else {
    & py '$EscapedTyfPy' @args
}
exit `$LASTEXITCODE
"@
Set-Content -LiteralPath $Ps1Path -Value $Ps1 -Encoding UTF8

Write-Host ""
Write-Host "Installed helper launchers:"
Write-Host "  $CmdPath"
Write-Host "  $Ps1Path"
if (($env:PATH -split ";") -notcontains $BinDir) {
    Write-Host "  NOTE: $BinDir is not on your PATH. Add it for future shells:"
    Write-Host "        `$current = [Environment]::GetEnvironmentVariable('Path', 'User')"
    Write-Host "        [Environment]::SetEnvironmentVariable('Path', `"$BinDir;`$current`", 'User')"
}

Write-Host ""
Write-Host "Book workspace context:"
Write-Host '  For a book workspace, run `tyf init` in the book folder, or `tyf init <book-folder>` near it.'
Write-Host "  Use the generated context files."
Write-Host "  Do not copy the pack development context into a book workspace."
Write-Host "  Clean author-context templates are available at: $Root\author-context\"
Write-Host ""
Write-Host "Contributor context for working on this TYF pack:"
Write-Host "  $Root\$(Context-File-For $Harness)"
Write-Host ""
Write-Host "Then verify: ask the agent to list its TYF skills; it should route through 'using-tyf' first."
