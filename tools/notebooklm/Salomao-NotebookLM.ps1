[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('login', 'check', 'list', 'run')]
    [string]$Action = 'check',

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$NotebookLmArguments
)

$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'Enable-GeminiNotebookHost.ps1')

$cli = Join-Path $env:USERPROFILE '.local\bin\notebooklm.exe'
if (-not (Test-Path -LiteralPath $cli -PathType Leaf)) {
    throw "Executável do uv não encontrado em '$cli'. Instale com: uv tool install --force --python <python.exe> notebooklm-py[browser]"
}

# O NotebookLM foi migrado para Gemini Notebook neste ambiente. Mantemos a
# configuração no escopo do processo, sem gravar variável global no Windows.
$env:NOTEBOOKLM_BASE_URL = 'https://notebook.google.com'

switch ($Action) {
    'login' {
        & $cli login --fresh @NotebookLmArguments
    }
    'check' {
        & $cli auth check --test --json @NotebookLmArguments
    }
    'list' {
        & $cli list --json @NotebookLmArguments
    }
    'run' {
        if ($NotebookLmArguments.Count -eq 0) {
            throw 'Em modo run, informe o comando do NotebookLM. Ex.: run source list -n <id>'
        }
        & $cli @NotebookLmArguments
    }
}

exit $LASTEXITCODE
