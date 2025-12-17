[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Error $Message
    exit 1
}

function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) {
        Fail $Message
    }
}

function Join-Url([string]$Base, [string]$Path) {
    $b = $Base.TrimEnd('/')
    $p = $Path
    if (-not $p.StartsWith('/')) { $p = "/$p" }
    return "$b$p"
}

try {
    $casePayload = @{ name = "PR9-10 Smoke" } | ConvertTo-Json
    $case = Invoke-RestMethod -Method Post -Uri (Join-Url $BaseUrl "/cases") -ContentType "application/json" -Body $casePayload

    Assert ($null -ne $case) "POST /cases returned null"
    Assert ($null -ne $case.id -and [string]$case.id -ne "") "POST /cases did not return an id"

    $caseId = [string]$case.id

    $draft = Invoke-RestMethod -Method Get -Uri (Join-Url $BaseUrl "/cases/$caseId/report_draft") -ContentType "application/json"
    Assert ($null -ne $draft) "GET /cases/{case_id}/report_draft returned null"
    Assert ($null -ne $draft.case) "report_draft missing .case"
    Assert (([string]$draft.case.id) -eq $caseId) "report_draft .case.id mismatch (expected $caseId, got $($draft.case.id))"

    $artifactPayload = @{ kind = "PHOTO"; label = "scene photo"; uri = "file://smoke-test"; sha256 = "abc" } | ConvertTo-Json
    $artifact = Invoke-RestMethod -Method Post -Uri (Join-Url $BaseUrl "/cases/$caseId/artifacts") -ContentType "application/json" -Body $artifactPayload

    Assert ($null -ne $artifact) "POST /cases/{case_id}/artifacts returned null"
    Assert ($null -ne $artifact.id -and [string]$artifact.id -ne "") "artifact create did not return an id"
    $artifactId = [string]$artifact.id

    $timeline = Invoke-RestMethod -Method Get -Uri (Join-Url $BaseUrl "/cases/$caseId/timeline?limit=50&offset=0") -ContentType "application/json"
    Assert ($null -ne $timeline) "GET /cases/{case_id}/timeline returned null"

    $hasArtifactAdded = $false
    $hasArtifactAudit = $false

    foreach ($item in $timeline) {
        if ($null -ne $item.item_type -and ([string]$item.item_type) -eq "ARTIFACT_ADDED") {
            $hasArtifactAdded = $true
        }
        if ($null -ne $item.item_type -and ([string]$item.item_type) -eq "AUDIT_EVENT") {
            if ($null -ne $item.audit -and $null -ne $item.audit.action -and ([string]$item.audit.action) -eq "artifact_added") {
                $hasArtifactAudit = $true
            }
        }
    }

    Assert $hasArtifactAdded "timeline missing item_type == ARTIFACT_ADDED"
    Assert $hasArtifactAudit "timeline missing AUDIT_EVENT with audit.action == artifact_added"

    Write-Host "PR9/PR10 smoke test: OK"
    Write-Host "case_id: $caseId"
    Write-Host "artifact_id: $artifactId"
    exit 0
} catch {
    $msg = $_.Exception.Message
    if ($null -ne $_.ErrorDetails -and $null -ne $_.ErrorDetails.Message -and $_.ErrorDetails.Message -ne "") {
        $msg = "$msg`n$($_.ErrorDetails.Message)"
    }
    Fail "Smoke test failed: $msg"
}
