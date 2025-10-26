# KrushiAI - Start All Backend Services
# This script starts all three backend APIs on different ports

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   KrushiAI - Starting All Services   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define service directories and ports
$services = @(
    @{
        Name = "Crop Recommendation"
        Dir = "KrushiAI-Crop-Recommendation"
        Port = 5000
        Script = "app.py"
    },
    @{
        Name = "Fertilizer Recommendation"
        Dir = "KrushiAI-Fertilizer-Recommendation"
        Port = 5001
        Script = "app.py"
    },
    @{
        Name = "Disease Recognition"
        Dir = "KrushiAI-Disease-Recognition\backend"
        Port = 5002
        Script = "app.py"
    }
)

$jobs = @()

# Start each service
foreach ($service in $services) {
    Write-Host "Starting $($service.Name) on port $($service.Port)..." -ForegroundColor Green
    
    $scriptBlock = {
        param($serviceDir, $port, $scriptName, $serviceName)
        
        $env:PORT = $port
        $env:FLASK_ENV = "development"
        
        Set-Location $serviceDir
        python $scriptName
    }
    
    $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList (Join-Path $PSScriptRoot $service.Dir), $service.Port, $service.Script, $service.Name
    $jobs += @{Job = $job; Name = $service.Name; Port = $service.Port}
    
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   All Services Started!              " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running on:" -ForegroundColor Yellow
Write-Host "  • Crop Recommendation:     http://localhost:5000" -ForegroundColor White
Write-Host "  • Fertilizer Recommendation: http://localhost:5001" -ForegroundColor White
Write-Host "  • Disease Recognition:     http://localhost:5002" -ForegroundColor White
Write-Host ""
Write-Host "Frontend URLs (open in browser):" -ForegroundColor Yellow
Write-Host "  • Crop:       file:///$PSScriptRoot/KrushiAI-Crop-Recommendation/index.html" -ForegroundColor White
Write-Host "  • Fertilizer: file:///$PSScriptRoot/KrushiAI-Fertilizer-Recommendation/frontend/index.html" -ForegroundColor White
Write-Host "  • Disease:    file:///$PSScriptRoot/KrushiAI-Disease-Recognition/frontend/index.html" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Red
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        foreach ($jobInfo in $jobs) {
            $job = $jobInfo.Job
            if ($job.State -eq "Failed" -or $job.State -eq "Stopped") {
                Write-Host "⚠ $($jobInfo.Name) service has stopped!" -ForegroundColor Red
                Receive-Job -Job $job
            }
        }
        Start-Sleep -Seconds 5
    }
}
finally {
    Write-Host ""
    Write-Host "Stopping all services..." -ForegroundColor Yellow
    foreach ($jobInfo in $jobs) {
        Stop-Job -Job $jobInfo.Job
        Remove-Job -Job $jobInfo.Job
    }
    Write-Host "All services stopped." -ForegroundColor Green
}
