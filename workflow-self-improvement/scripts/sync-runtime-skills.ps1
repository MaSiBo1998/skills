param(
  [Parameter(Mandatory=$true)]
  [string[]]$Skill,

  [string]$SourceRoot = "C:\Users\11731\Desktop\skills",

  [string[]]$RuntimeRoots = @(
    "C:\Users\11731\.agents\skills",
    "C:\Users\11731\.codex\skills",
    "C:\Users\11731\.trae\skills",
    "C:\Users\11731\.claude\skills"
  )
)

$ErrorActionPreference = "Stop"

function Get-FileHashSafe($Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return "MISSING" }
  return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash
}

foreach ($skillName in $Skill) {
  $source = Join-Path $SourceRoot $skillName
  if (-not (Test-Path -LiteralPath $source)) {
    throw "Source skill not found: $source"
  }

  foreach ($runtimeRoot in $RuntimeRoots) {
    New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null
    $target = Join-Path $runtimeRoot $skillName

    if (-not (Test-Path -LiteralPath $target)) {
      New-Item -ItemType Junction -Path $target -Target $source | Out-Null
      Write-Output "created-junction`t$target"
      continue
    }

    $item = Get-Item -Force -LiteralPath $target
    if ($item.LinkType -eq "Junction" -and $item.Target -contains $source) {
      Write-Output "ok-junction`t$target"
      continue
    }

    Get-ChildItem -LiteralPath $source -Force | Copy-Item -Destination $target -Recurse -Force
    Write-Output "synced-copy`t$target"
  }
}

foreach ($skillName in $Skill) {
  $source = Join-Path $SourceRoot $skillName
  $relativeFiles = @("SKILL.md", "agents\openai.yaml")
  $referenceDir = Join-Path $source "references"
  if (Test-Path -LiteralPath $referenceDir) {
    Get-ChildItem -LiteralPath $referenceDir -File -Filter "*.md" | ForEach-Object {
      $relativeFiles += ("references\" + $_.Name)
    }
  }

  foreach ($relativeFile in $relativeFiles) {
    $sourceFile = Join-Path $source $relativeFile
    $sourceHash = Get-FileHashSafe $sourceFile
    foreach ($runtimeRoot in $RuntimeRoots) {
      $targetFile = Join-Path (Join-Path $runtimeRoot $skillName) $relativeFile
      $targetHash = Get-FileHashSafe $targetFile
      if ($sourceHash -ne $targetHash) {
        Write-Output "DRIFT`t$skillName`t$relativeFile`t$runtimeRoot"
      }
    }
  }
}
