# NexusLEO Demo Happy Path

```powershell
docker compose -f nexusleo/docker-compose.yml up --build -d
Invoke-RestMethod -Method Get -Uri 'http://localhost:8000/version' | ConvertTo-Json -Depth 6
$seed = Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/_demo/seed'
Invoke-RestMethod -Method Post -Uri (('http://localhost:8000/cases/{0}/run' -f $seed.case_id)) -ContentType 'application/json' -Body (@{ document_id = $seed.document_id } | ConvertTo-Json) | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Get -Uri (('http://localhost:8000/cases/{0}/export?limit=100&offset=0' -f $seed.case_id)) | ConvertTo-Json -Depth 10
```
