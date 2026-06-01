param(
  [string]$WebsiteRoot = (Split-Path -Parent $PSScriptRoot),
  [string[]]$VerifyUrl = @("https://leadcore.by/"),
  [string[]]$ProductionAliases = @("leadcore.by", "www.leadcore.by"),
  [string[]]$RequiredContent = @(),
  [string[]]$ForbiddenContent = @(),
  [int]$MaxAttempts = 24,
  [int]$DelaySeconds = 5
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Invoke-HttpCheck {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Url
  )

  try {
    $response = Invoke-WebRequest -Uri $Url -Method Get -MaximumRedirection 5 -UseBasicParsing
    return [pscustomobject]@{
      ok = ($response.StatusCode -eq 200)
      statusCode = [int]$response.StatusCode
      statusDescription = [string]$response.StatusDescription
      finalUrl = [string]$response.BaseResponse.ResponseUri.AbsoluteUri
    }
  } catch {
    $statusCode = 0
    $statusDescription = $_.Exception.Message
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
      $statusCode = [int]$_.Exception.Response.StatusCode
      $statusDescription = [string]$_.Exception.Response.StatusDescription
    }
    return [pscustomobject]@{
      ok = $false
      statusCode = $statusCode
      statusDescription = $statusDescription
      finalUrl = $Url
      missingContent = @()
      forbiddenContent = @()
    }
  }
}

function Invoke-ContentCheck {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Url,
    [string[]]$RequiredContent = @(),
    [string[]]$ForbiddenContent = @()
  )

  $check = Invoke-HttpCheck -Url $Url
  if (-not $check.ok) {
    return $check
  }

  $response = Invoke-WebRequest -Uri $Url -Method Get -MaximumRedirection 5 -UseBasicParsing
  $html = [string]$response.Content
  $missing = @($RequiredContent | Where-Object { -not $html.Contains($_) })
  $forbidden = @($ForbiddenContent | Where-Object { $html.Contains($_) })

  return [pscustomobject]@{
    ok = ($check.ok -and $missing.Count -eq 0 -and $forbidden.Count -eq 0)
    statusCode = $check.statusCode
    statusDescription = $check.statusDescription
    finalUrl = $check.finalUrl
    missingContent = $missing
    forbiddenContent = $forbidden
  }
}

function Copy-FileWithRetry {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Source,
    [Parameter(Mandatory = $true)]
    [string]$Destination,
    [int]$Attempts = 8,
    [int]$DelayMilliseconds = 350
  )

  for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
    try {
      if (Test-Path $Destination) {
        $sourceItem = Get-Item -LiteralPath $Source
        $destinationItem = Get-Item -LiteralPath $Destination
        if ($sourceItem.Length -eq $destinationItem.Length) {
          $sourceHash = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
          $destinationHash = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash
          if ($sourceHash -eq $destinationHash) {
            return
          }
        }
      }

      Copy-Item -LiteralPath $Source -Destination $Destination -Force
      return
    } catch {
      if ($attempt -eq $Attempts) {
        throw
      }
      Start-Sleep -Milliseconds $DelayMilliseconds
    }
  }
}

function Sync-LandingPrebuiltOutput {
  param(
    [Parameter(Mandatory = $true)]
    [string]$WebsiteRoot
  )

  $prebuiltStaticRoot = Join-Path $WebsiteRoot ".vercel\output\static"
  if (-not (Test-Path $prebuiltStaticRoot)) {
    return
  }

  $landingSource = Join-Path $WebsiteRoot "landing\index.html"
  if (-not (Test-Path $landingSource)) {
    return
  }

  $landingTargetDir = Join-Path $prebuiltStaticRoot "landing"
  $landingTarget = Join-Path $landingTargetDir "index.html"
  New-Item -ItemType Directory -Path $landingTargetDir -Force | Out-Null
  Copy-FileWithRetry -Source $landingSource -Destination $landingTarget

  $landingHtml = Get-Content -LiteralPath $landingSource -Raw
  $assetMatches = [regex]::Matches($landingHtml, '/assets/([^"''\s>]+)')
  $assetRelativePaths = $assetMatches | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique

  foreach ($relativeAssetPath in $assetRelativePaths) {
    $sourceAsset = Join-Path $WebsiteRoot ("assets\" + ($relativeAssetPath -replace '/', '\'))
    if (-not (Test-Path $sourceAsset)) {
      continue
    }

    $targetAsset = Join-Path $prebuiltStaticRoot ("assets\" + ($relativeAssetPath -replace '/', '\'))
    $targetDir = Split-Path -Parent $targetAsset
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

    $sourceItem = Get-Item -LiteralPath $sourceAsset
    if (Test-Path $targetAsset) {
      $targetItem = Get-Item -LiteralPath $targetAsset
      if ($targetItem.Length -eq $sourceItem.Length -and $targetItem.LastWriteTimeUtc -ge $sourceItem.LastWriteTimeUtc) {
        continue
      }
    }

    Copy-FileWithRetry -Source $sourceAsset -Destination $targetAsset
  }
}

Push-Location $WebsiteRoot
try {
  Sync-LandingPrebuiltOutput -WebsiteRoot $WebsiteRoot

  $whoami = (& cmd /d /c "vercel whoami 2>&1" | Out-String).Trim()
  $whoamiExit = $LASTEXITCODE
  if ($whoamiExit -ne 0) {
    throw "Vercel CLI is not authenticated. Output:`n$whoami"
  }

  $buildText = (& cmd /d /c "vercel build --prod 2>&1" | Out-String).Trim()
  $buildExit = $LASTEXITCODE
  if ($buildExit -ne 0) {
    throw "Vercel production prebuild failed.`n$buildText"
  }

  Sync-LandingPrebuiltOutput -WebsiteRoot $WebsiteRoot

  $deployText = (& cmd /d /c "vercel deploy --prebuilt --prod --yes 2>&1" | Out-String).Trim()
  $deployExit = $LASTEXITCODE
  if ($deployExit -ne 0) {
    throw "Vercel deploy failed.`n$deployText"
  }
  $deploymentUrl = ""
  $matches = [regex]::Matches($deployText, 'https://[^\s"]+')
  if ($matches.Count -gt 0) {
    $preferred = @($matches.Value | Where-Object { $_ -match "vercel\.app|leadcore\.by" })
    if ($preferred.Count -gt 0) {
      $deploymentUrl = $preferred[$preferred.Count - 1]
    } else {
      $deploymentUrl = $matches[$matches.Count - 1].Value
    }
  }

  if ($deploymentUrl) {
    $deploymentHost = ([Uri]$deploymentUrl).Host
    foreach ($alias in $ProductionAliases) {
      if ([string]::IsNullOrWhiteSpace($alias)) {
        continue
      }

      $aliasText = (& cmd /d /c "vercel alias set $deploymentHost $alias 2>&1" | Out-String).Trim()
      $aliasExit = $LASTEXITCODE
      if ($aliasExit -ne 0) {
        throw "Vercel alias failed for $alias.`n$aliasText"
      }
    }
  }

  $verified = @()
  foreach ($url in $VerifyUrl) {
    $check = $null
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
      $check = Invoke-ContentCheck -Url $url -RequiredContent $RequiredContent -ForbiddenContent $ForbiddenContent
      if ($check.ok) {
        break
      }
      Start-Sleep -Seconds $DelaySeconds
    }

    $verified += [pscustomobject]@{
      url = $url
      ok = $check.ok
      statusCode = $check.statusCode
      statusDescription = $check.statusDescription
      finalUrl = $check.finalUrl
    }
  }

  $failed = $verified | Where-Object { -not $_.ok }
  $summary = [pscustomobject]@{
    deployedAt = (Get-Date).ToString("o")
    websiteRoot = $WebsiteRoot
    deploymentUrl = $deploymentUrl
    verify = $verified
  }

  $summary | ConvertTo-Json -Depth 5

  if ($failed) {
    throw "Public URL verification failed."
  }
} finally {
  Pop-Location
}
