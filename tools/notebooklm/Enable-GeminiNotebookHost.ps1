[CmdletBinding()]
param(
    [string]$UvToolDirectory
)

$ErrorActionPreference = 'Stop'

function Get-UvNotebookLmPackageDirectory {
    param([string]$ToolDirectory)

    if ([string]::IsNullOrWhiteSpace($ToolDirectory)) {
        $uv = Get-Command uv -ErrorAction Stop
        # uv emite códigos ANSI mesmo com stdout redirecionado; removê-los evita que
        # sobrem em $ToolDirectory e quebrem o Join-Path subsequente.
        $ansiPattern = [char]27 + '\[[0-9;]*m'
        $ToolDirectory = ((& $uv.Source tool dir) -replace $ansiPattern, '').Trim()
    }

    $packageDirectory = Join-Path $ToolDirectory 'notebooklm-py\Lib\site-packages\notebooklm'
    if (-not (Test-Path -LiteralPath $packageDirectory -PathType Container)) {
        throw "Pacote NotebookLM do uv não encontrado em '$packageDirectory'. Instale-o com: uv tool install --force --python <python.exe> notebooklm-py[browser]"
    }

    return $packageDirectory
}

function Backup-Once {
    param([string]$Path)

    $backup = "$Path.salomaoai-backup"
    if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) {
        Copy-Item -LiteralPath $Path -Destination $backup -ErrorAction Stop
    }
}

function Update-TextFile {
    param(
        [string]$Path,
        [string]$OldText,
        [string]$NewText,
        [string]$PresentText,
        [string]$Description
    )

    $content = Get-Content -Raw -LiteralPath $Path
    if ($content.Contains($PresentText)) {
        return
    }
    if (-not $content.Contains($OldText)) {
        throw "Não foi possível aplicar a compatibilidade do Gemini Notebook: âncora ausente em '$Path' ($Description). Revise a versão do notebooklm-py antes de continuar."
    }

    Backup-Once -Path $Path
    $content = $content.Replace($OldText, $NewText)
    Set-Content -LiteralPath $Path -Value $content -Encoding UTF8 -NoNewline
}

$packageDirectory = Get-UvNotebookLmPackageDirectory -ToolDirectory $UvToolDirectory
$envFile = Join-Path $packageDirectory '_env.py'
$cookiePolicyFile = Join-Path $packageDirectory '_auth\cookie_policy.py'

# A partir do notebooklm-py 0.8.x o upstream passou a suportar
# notebook.google.com nativamente (PERSONAL_BASE_HOST), então o patch
# abaixo (necessário só em versões antigas) fica obsoleto. Detectamos o
# suporte nativo e pulamos o patch em vez de falhar por âncora ausente.
$envContent = Get-Content -Raw -LiteralPath $envFile
if ($envContent.Contains('PERSONAL_BASE_HOST = "notebook.google.com"')) {
    Write-Host 'notebook.google.com já é suportado nativamente pelo notebooklm-py instalado; nenhum patch necessário.'
    return
}

Update-TextFile -Path $envFile `
    -OldText 'ENTERPRISE_BASE_HOST = "notebooklm.cloud.google.com"' `
    -NewText "ENTERPRISE_BASE_HOST = `"notebooklm.cloud.google.com`"`r`nGEMINI_NOTEBOOK_BASE_HOST = `"notebook.google.com`"" `
    -PresentText 'GEMINI_NOTEBOOK_BASE_HOST = "notebook.google.com"' `
    -Description 'host Gemini Notebook'

Update-TextFile -Path $envFile `
    -OldText '_ALLOWED_BASE_HOSTS = frozenset({PERSONAL_BASE_HOST, ENTERPRISE_BASE_HOST})' `
    -NewText "_ALLOWED_BASE_HOSTS = frozenset(`r`n    {PERSONAL_BASE_HOST, ENTERPRISE_BASE_HOST, GEMINI_NOTEBOOK_BASE_HOST}`r`n)" `
    -PresentText 'ENTERPRISE_BASE_HOST, GEMINI_NOTEBOOK_BASE_HOST' `
    -Description 'allowlist de host'

Update-TextFile -Path $cookiePolicyFile `
    -OldText '        "notebooklm.cloud.google.com",' `
    -NewText "        `"notebooklm.cloud.google.com`",`r`n        `".notebook.google.com`",`r`n        `"notebook.google.com`"," `
    -PresentText '        "notebook.google.com",' `
    -Description 'cookies do Gemini Notebook'

Update-TextFile -Path $cookiePolicyFile `
    -OldText "    if domain == `"notebooklm.google.com`":`r`n        return 2" `
    -NewText "    if domain == `"notebooklm.google.com`":`r`n        return 2`r`n    if domain == `".notebook.google.com`":`r`n        return 3`r`n    if domain == `"notebook.google.com`":`r`n        return 2" `
    -PresentText '    if domain == "notebook.google.com":' `
    -Description 'prioridade de cookies do Gemini Notebook'

Write-Host 'Compatibilidade notebook.google.com aplicada ao notebooklm-py do uv.'
