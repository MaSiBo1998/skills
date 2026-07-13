[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$OutputDir,

  [ValidateRange(1, 168)]
  [int]$RefreshHours = 24,

  [ValidateRange(1, 50)]
  [int]$TopN = 20,

  [ValidateRange(4, 30)]
  [int]$MaxPages = 30,

  [ValidateRange(2000, 10000)]
  [int]$ActionTimeoutMs = 5000,

  [string]$BrowserArgs = '--no-sandbox',

  [ValidateRange(1, 8)]
  [int]$CategoryLimit = 6,

  [string[]]$Genres = @('都市日常', '都市脑洞', '都市种田', '现言脑洞', '年代', '古风世情'),

  [switch]$CaptureReviewScreenshots,

  [ValidateRange(10, 55)]
  [int]$ScanDeadlineSeconds = 35,

  [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-JsonFile {
  param([object]$Value, [string]$Path)
  $Value | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $Path -Encoding utf8
}

function Read-JsonFile {
  param([string]$Path)
  return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Invoke-AgentBrowser {
  param([string[]]$Arguments)

  if ($BrowserArgs -match '\s') {
    throw 'BrowserArgs must be a single browser-launch flag without whitespace.'
  }

  # Pass browser launch arguments only once. agent-browser emits a warning when
  # the session daemon already exists, and that warning would corrupt eval JSON.
  $prefix = @('--session', $script:Session, '--allowed-domains', 'fanqienovel.com')
  if ($script:PassBrowserArgs) {
    $prefix += @('--args', $BrowserArgs)
  }
  $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("webfiction-agent-browser-" + [guid]::NewGuid().ToString('N'))
  $stdoutPath = Join-Path $tempRoot 'stdout.txt'
  $stderrPath = Join-Path $tempRoot 'stderr.txt'
  New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null
  try {
    $process = Start-Process -FilePath $script:AgentBrowserExecutable -ArgumentList (($prefix + $Arguments) -join ' ') -PassThru -NoNewWindow -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    if (-not $process.WaitForExit($ActionTimeoutMs)) {
      Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
      throw "agent-browser action timed out after $ActionTimeoutMs ms."
    }
    $result = @(
      if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw }
      if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw }
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    $exitCode = $process.ExitCode
  } finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
  }
  if ($Arguments.Count -gt 0 -and $Arguments[0] -eq 'open') {
    $script:PassBrowserArgs = $false
  }
  $resultText = $result | Out-String
  # The Windows native CLI can return a non-zero process code after a completed
  # navigation, while still printing its normal success marker and URL. Treat
  # only those explicit success shapes as successful; real errors still flow to
  # the safe-degradation path.
  $hasExplicitSuccess = $resultText -match '(?m)^✓\s' -or $resultText -match 'https://fanqienovel\.com/' -or $resultText.TrimStart().StartsWith('{') -or $resultText.TrimStart().StartsWith('[')
  if ($exitCode -ne 0 -and -not $hasExplicitSuccess) {
    throw "agent-browser failed: $($result | Out-String)"
  }
  return ($result | Out-String).Trim()
}

function Invoke-BrowserEval {
  param([string]$JavaScript)
  # Base64 avoids a Windows PowerShell stdin-wrapper bug in agent-browser and
  # preserves multiline JavaScript without shell escaping.
  $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($JavaScript))
  $text = Invoke-AgentBrowser -Arguments @('eval', '--base64', $encoded)
  $text = (($text -split "`r?`n") | Where-Object { $_ -notmatch '^⚠\s+--args ignored:' }) -join "`n"
  if ([string]::IsNullOrWhiteSpace($text)) {
    throw 'agent-browser eval returned no data.'
  }
  return $text | ConvertFrom-Json
}

function Assert-ScanBudget {
  if ($script:PageCount -ge $MaxPages) {
    throw "Page budget exhausted at $MaxPages pages."
  }
  if ([DateTimeOffset]::UtcNow -gt $script:ScanDeadline) {
    throw "Scan deadline reached after $ScanDeadlineSeconds seconds."
  }
}

function Get-CategoryLinks {
  Assert-ScanBudget
  Invoke-AgentBrowser -Arguments @('open', 'https://fanqienovel.com/rank') | Out-Null
  $script:PageCount++
  $extractScript = @"
(() => {
  const normalize = (value) => (value || '').replace(/\s+/g, ' ').trim();
  const seen = new Set();
  const links = [];
  for (const link of Array.from(document.querySelectorAll('a[href*="/rank/"]'))) {
    const label = normalize(link.textContent);
    const url = link.href;
    const match = url.match(/\/rank\/([01])_([12])_(\d+)/);
    if (!match || !label || label.length > 24 || seen.has(url)) continue;
    seen.add(url);
    const gender = match[1] === '1' ? '男频' : '女频';
    const boardType = match[2] === '1' ? '新书榜' : '阅读榜';
    links.push({ label, url, board_name: gender + boardType, gender, board_type: boardType });
  }
  return { links };
})()
"@
  $payload = Invoke-BrowserEval -JavaScript $extractScript
  return @($payload.links)
}

function Get-Board {
  param([string]$Label, [string]$Url, [string]$BoardName)

  Assert-ScanBudget
  Invoke-AgentBrowser -Arguments @('open', $Url) | Out-Null
  $script:PageCount++

  $extractScript = @"
(() => {
  const normalize = (value) => (value || '').replace(/\s+/g, ' ').trim();
  const cleanLines = (value) => (value || '').split(/\n+/).map(normalize).filter(Boolean);
  const privateUseRatio = (value) => {
    const text = value || '';
    if (!text.length) return 0;
    return Array.from(text).filter((char) => /[\uE000-\uF8FF]/.test(char)).length / Array.from(text).length;
  };
  const findCard = (link) => {
    let node = link;
    for (let depth = 0; depth < 8 && node; depth++, node = node.parentElement) {
      const lines = cleanLines(node.innerText);
      if (lines.length >= 5 && lines.some((line) => /最近更新|已完结|连载中|在读/.test(line))) {
        return { node, lines };
      }
    }
    const fallbackNode = link.parentElement?.parentElement || link.parentElement || link;
    return { node: fallbackNode, lines: cleanLines(fallbackNode.innerText) };
  };
  const seen = new Set();
  const entries = [];
  for (const link of Array.from(document.querySelectorAll('a[href*="/page/"]'))) {
    const title = normalize(link.textContent);
    const url = link.href;
    if (!title || title.length > 120 || seen.has(url)) continue;
    seen.add(url);
    const { lines } = findCard(link);
    const author = lines.length > 1 ? lines[1] : null;
    const publicBlurb = lines.length > 2 ? lines[2].slice(0, 800) : '';
    const publicTags = Array.from(publicBlurb.matchAll(/【([^】]{1,120})】/g))
      .flatMap((match) => match[1].split(/[+＋、|]/))
      .map(normalize).filter(Boolean).slice(0, 20);
    const latestLine = lines.find((line) => line.startsWith('最近更新：')) || '';
    const statusLine = lines.find((line) => /^(已完结|连载中)$/.test(line)) || '';
    const completionStatus = statusLine === '已完结' || /完结|大结局|终章|全文完/.test(latestLine)
      ? 'completed'
      : statusLine === '连载中' ? 'serializing' : 'unknown';
    const readingLine = lines.find((line) => line.startsWith('在读：')) || '';
    const updatedAt = lines.find((line) => /^\d{4}-\d{2}-\d{2}/.test(line)) || null;
    const qualityText = [title, author || '', publicBlurb, latestLine].join(' ');
    const obfuscationRatio = privateUseRatio(qualityText);
    entries.push({
      rank: entries.length + 1,
      title,
      author,
      url,
      public_tags: publicTags,
      public_blurb: publicBlurb,
      latest_update: latestLine.replace(/^最近更新：/, '') || null,
      updated_at: updatedAt,
      reading_count: readingLine.replace(/^在读：/, '') || null,
      completion_status: completionStatus,
      evidence_method: 'public_rank_card',
      text_quality: {
        private_use_ratio: Number(obfuscationRatio.toFixed(3)),
        needs_visual_review: obfuscationRatio >= 0.08
      }
    });
    if (entries.length >= $TopN) break;
  }
  return {
    source_url: location.href,
    entries,
    page_text_obfuscated: entries.some((entry) => entry.text_quality.needs_visual_review)
  };
})()
"@

  for ($attempt = 0; $attempt -lt 2; $attempt++) {
    $payload = Invoke-BrowserEval -JavaScript $extractScript
    if ($payload.entries.Count -gt 0) {
      $reviewScreenshot = $null
      if ($CaptureReviewScreenshots -or $payload.page_text_obfuscated) {
        try {
          $safeName = (($BoardName + '-' + $Label) -replace '[^\p{L}\p{N}_-]', '-')
          $screenshotDir = Join-Path $OutputDir 'review-screenshots'
          New-Item -ItemType Directory -Force -Path $screenshotDir | Out-Null
          $tempScreenshot = Join-Path ([System.IO.Path]::GetTempPath()) ("fanqie-review-" + [guid]::NewGuid().ToString('N') + '.png')
          # A viewport screenshot is more reliable than full-body capture on the
          # virtualized rank list and is sufficient for reviewing the top cards.
          Invoke-AgentBrowser -Arguments @('screenshot', $tempScreenshot) | Out-Null
          $reviewScreenshot = Join-Path $screenshotDir ($safeName + '.png')
          Move-Item -LiteralPath $tempScreenshot -Destination $reviewScreenshot -Force
        } catch {
          Write-Warning "$BoardName/$Label 截图失败: $($_.Exception.Message)"
        }
      }
      return [ordered]@{
        name = $BoardName
        genre = $Label
        source_url = $payload.source_url
        entries = @($payload.entries)
        review_screenshot = $reviewScreenshot
        text_obfuscated = [bool]$payload.page_text_obfuscated
      }
    }
    Start-Sleep -Milliseconds 250
  }

  throw "No public rank entries were found for $Label."
}

if (-not (Get-Command agent-browser -ErrorAction SilentlyContinue)) {
  throw 'agent-browser is required. Install and initialize it before running this collector.'
}

$agentBrowserCommand = Get-Command agent-browser
$script:AgentBrowserExecutable = $agentBrowserCommand.Path
if ($script:AgentBrowserExecutable -like '*.ps1') {
  $binaryDirectory = Join-Path (Split-Path -Parent $agentBrowserCommand.Path) 'node_modules\agent-browser\bin'
  $nativeBinary = Get-ChildItem -LiteralPath $binaryDirectory -File -Filter 'agent-browser-*.exe' -ErrorAction SilentlyContinue |
    Select-Object -First 1
  if (-not $nativeBinary) {
    throw "Could not locate the native agent-browser executable below $binaryDirectory."
  }
  $script:AgentBrowserExecutable = $nativeBinary.FullName
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$currentSnapshotPath = Join-Path $OutputDir 'fanqie-current.json'
$previousSnapshot = $null
if (Test-Path -LiteralPath $currentSnapshotPath) {
  try {
    $previousSnapshot = Read-JsonFile -Path $currentSnapshotPath
  } catch {
    Write-Warning "Ignoring unreadable cache: $($_.Exception.Message)"
  }
}

if ($previousSnapshot -and -not $Force) {
  try {
    $capturedAt = [DateTimeOffset]::Parse([string]$previousSnapshot.captured_at)
    if (([DateTimeOffset]::UtcNow - $capturedAt).TotalHours -lt $RefreshHours) {
      $previousSnapshot.status = 'cached'
      $previousSnapshot.cache_checked_at = [DateTimeOffset]::UtcNow.ToString('o')
      Write-JsonFile -Value $previousSnapshot -Path $currentSnapshotPath
      Write-Output "Using cached public snapshot: $currentSnapshotPath"
      exit 0
    }
  } catch {
    Write-Warning "Cache timestamp is invalid; a fresh scan will be attempted."
  }
}

$script:Session = 'webfiction-public-scan'
$script:PageCount = 0
$script:PassBrowserArgs = $true
$script:ScanDeadline = [DateTimeOffset]::UtcNow.AddSeconds($ScanDeadlineSeconds)
$boards = @()
$notes = @()
$selectedLabels = @()
$previousBrowserTimeout = $env:AGENT_BROWSER_DEFAULT_TIMEOUT
$env:AGENT_BROWSER_DEFAULT_TIMEOUT = [string]$ActionTimeoutMs

try {
  # A previous interrupted scan can leave only this session's daemon alive.
  # Reset it before passing launch args so agent-browser does not turn a benign
  # warning into a failed first navigation. Other named sessions are untouched.
  $script:PassBrowserArgs = $false
  try { Invoke-AgentBrowser -Arguments @('close') | Out-Null } catch { }
  $script:PassBrowserArgs = $true
  $categories = @()
  try {
    $availableLinks = @(Get-CategoryLinks)
    foreach ($genre in $Genres) {
      if ($availableLinks.label -contains $genre -and $selectedLabels -notcontains $genre) {
        $selectedLabels += $genre
      }
      if ($selectedLabels.Count -ge $CategoryLimit) { break }
    }
    if ($selectedLabels.Count -lt $CategoryLimit) {
      foreach ($label in @($availableLinks.label | Select-Object -Unique)) {
        if ($selectedLabels -notcontains $label) { $selectedLabels += $label }
        if ($selectedLabels.Count -ge $CategoryLimit) { break }
      }
    }
    $categories = @($availableLinks | Where-Object { $selectedLabels -contains $_.label })
    if ($categories.Count -eq 0) {
      $notes += 'No public category links were found on the rank page.'
    }
  } catch {
    $notes += "分类目录: $($_.Exception.Message)"
  }
  foreach ($category in $categories) {
    try {
      $boards += Get-Board -Label $category.label -Url $category.url -BoardName $category.board_name
    } catch {
      $notes += "$($category.board_name)/$($category.label): $($_.Exception.Message)"
      if ($_.Exception.Message -match 'Auto-launch failed|Chrome exited early|timed out|deadline') {
        break
      }
    }
  }
} finally {
  # Closing only this isolated session prevents stale state from affecting later scans.
  try { Invoke-AgentBrowser -Arguments @('close') | Out-Null } catch { }
  if ($null -eq $previousBrowserTimeout) {
    Remove-Item Env:\AGENT_BROWSER_DEFAULT_TIMEOUT -ErrorAction SilentlyContinue
  } else {
    $env:AGENT_BROWSER_DEFAULT_TIMEOUT = $previousBrowserTimeout
  }
}

$capturedAt = [DateTimeOffset]::UtcNow.ToString('o')
$status = if ($boards.Count -gt 0) { 'fresh' } elseif ($previousSnapshot) { 'stale' } else { 'unavailable' }
$boardPayload = [object[]]@()
if ($boards.Count -gt 0) {
  $boardPayload = [object[]]$boards
} elseif ($previousSnapshot -and $previousSnapshot.boards) {
  $boardPayload = [object[]]@($previousSnapshot.boards)
}

$snapshot = [ordered]@{
  schema_version = 2
  captured_at = $capturedAt
  source = 'https://fanqienovel.com/rank'
  status = $status
  page_count = $script:PageCount
  sampled_genres = @($selectedLabels)
  board_definition = '番茄公开页当前提供男女频阅读榜与新书榜；完结样本由阅读榜卡片的公开完结状态识别，不声称存在独立完结榜。'
  boards = $boardPayload
  notes = @($notes)
}

$timestamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
$datedSnapshotPath = Join-Path $OutputDir "fanqie-$timestamp.json"
Write-JsonFile -Value $snapshot -Path $datedSnapshotPath
Write-JsonFile -Value $snapshot -Path $currentSnapshotPath

Write-Output "Public snapshot status=$status pages=$($script:PageCount) path=$currentSnapshotPath"
if ($status -ne 'fresh') {
  exit 1
}
