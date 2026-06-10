param(
  [string]$EvaluationPath = "C:\Users\11731\Desktop\skills\workflow-self-improvement\references\workflow-regression-evaluation.md",
  [double]$PassRatio = 0.88
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $EvaluationPath)) {
  throw "Evaluation file not found: $EvaluationPath"
}

$lines = Get-Content -LiteralPath $EvaluationPath
$inCases = $false
$cases = @()

foreach ($line in $lines) {
  if ($line -match "^##\s+评估样例") {
    $inCases = $true
    continue
  }

  if ($inCases -and $line -match "^##\s+") {
    break
  }

  if (-not $inCases) { continue }
  if ($line -notmatch "^\|") { continue }
  if ($line -match "^\|\s*类型\s*\|") { continue }
  if ($line -match "^\|\s*-+") { continue }

  $cells = $line.Trim("|").Split("|") | ForEach-Object { $_.Trim() }
  if ($cells.Count -ge 3 -and $cells[0]) {
    $cases += [pscustomobject]@{
      Type = $cells[0]
      Input = $cells[1]
      Expected = $cells[2]
    }
  }
}

$caseCount = $cases.Count
$totalScore = $caseCount * 5
$passScore = [Math]::Ceiling($totalScore * $PassRatio)

[pscustomobject]@{
  evaluation_path = $EvaluationPath
  case_count = $caseCount
  total_score = $totalScore
  pass_score = $passScore
  pass_ratio = $PassRatio
  case_types = @($cases | ForEach-Object { $_.Type })
} | ConvertTo-Json -Depth 4
