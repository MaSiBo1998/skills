param(
  [string[]]$Skill = @(),

  [switch]$All,
  [switch]$CheckOnly,
  [switch]$RepairLinks,

  [string]$SourceRoot = "C:\Users\11731\Desktop\skills",

  [string[]]$RuntimeRoots = @(
    "C:\Users\11731\.codex\skills",
    "C:\Users\11731\.trae\skills",
    "C:\Users\11731\.claude\skills",
    "C:\Users\11731\.agents\skills"
  )
)

$ErrorActionPreference = "Stop"

if (-not $All -and $Skill.Count -eq 0) {
  throw "Specify -All or -Skill <skill-name>."
}

if ($CheckOnly -and $RepairLinks) {
  throw "Use either -CheckOnly or -RepairLinks, not both."
}

if (-not $CheckOnly -and -not $RepairLinks) {
  $RepairLinks = $true
}

function Get-FullPathSafe([string]$Path) {
  return [System.IO.Path]::GetFullPath($Path)
}

function Assert-PathInsideRoot([string]$Path, [string]$Root) {
  $fullPath = Get-FullPathSafe $Path
  $fullRoot = (Get-FullPathSafe $Root).TrimEnd('\')
  if ($fullPath -ne $fullRoot -and -not $fullPath.StartsWith($fullRoot + "\", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to operate outside runtime root. Path=$fullPath Root=$fullRoot"
  }
}

function Get-FileHashSafe([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return "MISSING" }
  return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash
}

function Get-SourceSkillEntries {
  $candidateDirs = @()

  if ($All) {
    Get-ChildItem -LiteralPath $SourceRoot -Directory -Force |
      Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") } |
      ForEach-Object {
        $candidateDirs += [pscustomobject]@{
          Name = $_.Name
          FullName = $_.FullName
          Priority = 0
        }
      }

    $auxiliarySourceRoot = Join-Path $SourceRoot ".agents\skills"
    if (Test-Path -LiteralPath $auxiliarySourceRoot) {
      Get-ChildItem -LiteralPath $auxiliarySourceRoot -Directory -Force |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") } |
        ForEach-Object {
          $candidateDirs += [pscustomobject]@{
            Name = $_.Name
            FullName = $_.FullName
            Priority = 1
          }
        }
    }
  } else {
    foreach ($skillName in @($Skill | Sort-Object -Unique)) {
      $rootCandidate = Join-Path $SourceRoot $skillName
      $auxiliaryCandidate = Join-Path (Join-Path $SourceRoot ".agents\skills") $skillName

      if (Test-Path -LiteralPath (Join-Path $rootCandidate "SKILL.md")) {
        $item = Get-Item -LiteralPath $rootCandidate
        $candidateDirs += [pscustomobject]@{
          Name = $item.Name
          FullName = $item.FullName
          Priority = 0
        }
      } elseif (Test-Path -LiteralPath (Join-Path $auxiliaryCandidate "SKILL.md")) {
        $item = Get-Item -LiteralPath $auxiliaryCandidate
        $candidateDirs += [pscustomobject]@{
          Name = $item.Name
          FullName = $item.FullName
          Priority = 1
        }
      } else {
        $candidateDirs += [pscustomobject]@{
          Name = $skillName
          FullName = $rootCandidate
          Priority = 0
        }
      }
    }
  }

  $entries = @()
  $seen = @{}
  foreach ($candidateDir in @($candidateDirs | Sort-Object Name, Priority, FullName)) {
    $skillName = $candidateDir.Name
    if ($seen.ContainsKey($skillName)) {
      continue
    }

    $seen[$skillName] = $true
    $entries += [pscustomobject]@{
      Name = $skillName
      Path = Get-FullPathSafe $candidateDir.FullName
    }
  }

  return $entries
}

function Get-RelativeSkillFiles([string]$SkillPath) {
  $files = @()
  foreach ($relativePath in @("SKILL.md", "agents\openai.yaml")) {
    if (Test-Path -LiteralPath (Join-Path $SkillPath $relativePath)) {
      $files += $relativePath
    }
  }

  $referenceDir = Join-Path $SkillPath "references"
  if (Test-Path -LiteralPath $referenceDir) {
    Get-ChildItem -LiteralPath $referenceDir -File -Filter "*.md" | Sort-Object Name | ForEach-Object {
      $files += ("references\" + $_.Name)
    }
  }

  return $files
}

function Get-HashDiffs([string]$Source, [string]$Target) {
  $diffs = @()
  foreach ($relativeFile in Get-RelativeSkillFiles $Source) {
    $sourceFile = Join-Path $Source $relativeFile
    $targetFile = Join-Path $Target $relativeFile
    $sourceHash = Get-FileHashSafe $sourceFile
    $targetHash = Get-FileHashSafe $targetFile
    if ($sourceHash -ne $targetHash) {
      $diffs += $relativeFile
    }
  }
  return $diffs
}

function Write-Status([string]$Status, [string]$SkillName, [string]$RuntimeRoot, [string]$Detail = "") {
  [pscustomobject]@{
    status = $Status
    skill = $SkillName
    runtime = $RuntimeRoot
    detail = $Detail
  }
}

function New-SourceJunction([string]$Target, [string]$Source, [string]$RuntimeRoot, [string]$SkillName) {
  Assert-PathInsideRoot -Path $Target -Root $RuntimeRoot
  New-Item -ItemType Junction -Path $Target -Target $Source | Out-Null
  Write-Status "created-junction" $SkillName $RuntimeRoot $Target
}

function Backup-And-RemoveTarget([string]$Target, [string]$RuntimeRoot, [string]$SkillName, [bool]$IsJunction) {
  Assert-PathInsideRoot -Path $Target -Root $RuntimeRoot

  if ($IsJunction) {
    Remove-Item -LiteralPath $Target -Force
    return "removed-junction"
  }

  $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $backupRoot = Join-Path $RuntimeRoot ".runtime-link-backups"
  $backupDir = Join-Path (Join-Path $backupRoot $timestamp) $SkillName
  Assert-PathInsideRoot -Path $backupDir -Root $RuntimeRoot
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupDir) | Out-Null
  Move-Item -LiteralPath $Target -Destination $backupDir
  return "backed-up-to $backupDir"
}

$sourceRootFull = Get-FullPathSafe $SourceRoot
if (-not (Test-Path -LiteralPath $sourceRootFull)) {
  throw "Source root not found: $sourceRootFull"
}

$sourceSkillEntries = Get-SourceSkillEntries
$results = @()

foreach ($sourceSkill in $sourceSkillEntries) {
  $skillName = $sourceSkill.Name
  $source = Get-FullPathSafe $sourceSkill.Path
  if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md"))) {
    throw "Source skill not found or missing SKILL.md: $source"
  }

  foreach ($runtimeRootRaw in $RuntimeRoots) {
    $runtimeRoot = Get-FullPathSafe $runtimeRootRaw
    $isAgentsRuntime = $runtimeRoot.EndsWith("\.agents\skills", [System.StringComparison]::OrdinalIgnoreCase)

    if (-not (Test-Path -LiteralPath $runtimeRoot)) {
      if ($isAgentsRuntime) {
        $results += Write-Status "skipped-runtime" $skillName $runtimeRoot "runtime does not exist"
        continue
      }

      if ($CheckOnly) {
        $results += Write-Status "missing-runtime" $skillName $runtimeRoot "runtime does not exist"
        continue
      }

      New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null
    }

    $target = Join-Path $runtimeRoot $skillName
    Assert-PathInsideRoot -Path $target -Root $runtimeRoot

    if (-not (Test-Path -LiteralPath $target)) {
      $results += Write-Status "missing" $skillName $runtimeRoot $target
      if ($RepairLinks) {
        $results += New-SourceJunction -Target $target -Source $source -RuntimeRoot $runtimeRoot -SkillName $skillName
      }
      continue
    }

    $item = Get-Item -Force -LiteralPath $target
    $targetText = @($item.Target) -join ";"
    $isSourceJunction = $item.LinkType -eq "Junction" -and @($item.Target) -contains $source

    if ($isSourceJunction) {
      $results += Write-Status "ok-junction" $skillName $runtimeRoot $targetText
      continue
    }

    if ($item.LinkType -eq "Junction") {
      $results += Write-Status "wrong-target" $skillName $runtimeRoot $targetText
      if ($RepairLinks) {
        $backupResult = Backup-And-RemoveTarget -Target $target -RuntimeRoot $runtimeRoot -SkillName $skillName -IsJunction $true
        $results += Write-Status $backupResult $skillName $runtimeRoot $target
        $results += New-SourceJunction -Target $target -Source $source -RuntimeRoot $runtimeRoot -SkillName $skillName
      }
      continue
    }

    $results += Write-Status "copied-dir" $skillName $runtimeRoot $target
    foreach ($diff in Get-HashDiffs -Source $source -Target $target) {
      $results += Write-Status "hash-diff" $skillName $runtimeRoot $diff
    }

    if ($RepairLinks) {
      $backupResult = Backup-And-RemoveTarget -Target $target -RuntimeRoot $runtimeRoot -SkillName $skillName -IsJunction $false
      $results += Write-Status $backupResult $skillName $runtimeRoot $target
      $results += New-SourceJunction -Target $target -Source $source -RuntimeRoot $runtimeRoot -SkillName $skillName
    }
  }
}

$results | Format-Table -AutoSize
