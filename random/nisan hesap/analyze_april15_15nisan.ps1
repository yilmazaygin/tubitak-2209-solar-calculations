# PowerShell script to analyze April 15th solar energy data
# Calculate averages for UTC times: 03, 06, 09, 12, 15 for April 15th only

Write-Host "Reading CSV file for April 15th analysis..." -ForegroundColor Green

# Read the CSV file
$content = Get-Content "timeseri.csv"

# Find where data starts
$dataStart = 0
for ($i = 0; $i -lt $content.Length; $i++) {
    if ($content[$i] -match "^time,G\(i\),H_sun,T2m,WS10m,Int") {
        $dataStart = $i + 1
        break
    }
}

Write-Host "Data starts at line $dataStart" -ForegroundColor Yellow

# Parse April 15th data only
$april15Data = @()
$totalRecords = 0

for ($i = $dataStart; $i -lt $content.Length; $i++) {
    $line = $content[$i].Trim()
    if ($line -and $line.Contains(",")) {
        $totalRecords++
        $parts = $line.Split(",")
        if ($parts.Length -ge 6) {
            $timeStr = $parts[0]
            # Check if it's April 15th data (format: YYYY0415:HHMM)
            if ($timeStr -match "^\d{4}0415:\d{4}$") {
                try {
                    $gI = [double]$parts[1]
                    $hSun = [double]$parts[2]
                    $t2m = [double]$parts[3]
                    $ws10m = [double]$parts[4]
                    $intensity = [double]$parts[5]
                    
                    # Extract hour from time string
                    $hour = [int]$timeStr.Split(":")[1].Substring(0,2)
                    
                    $april15Data += @{
                        Time = $timeStr
                        Hour = $hour
                        GI = $gI
                        HSun = $hSun
                        T2m = $t2m
                        WS10m = $ws10m
                        Intensity = $intensity
                    }
                }
                catch {
                    # Skip invalid data
                }
            }
        }
    }
}

Write-Host "Total records processed: $totalRecords" -ForegroundColor Yellow
Write-Host "April 15th records found: $($april15Data.Count)" -ForegroundColor Yellow

if ($april15Data.Count -eq 0) {
    Write-Host "No April 15th data found!" -ForegroundColor Red
    exit
}

# Filter for target hours
$targetHours = @(3, 6, 9, 12, 15)
$filteredData = $april15Data | Where-Object { $_.Hour -in $targetHours }

Write-Host "April 15th records for target hours (03, 06, 09, 12, 15): $($filteredData.Count)" -ForegroundColor Yellow

# Calculate averages for each hour
Write-Host "`n=== APRIL 15TH SOLAR ENERGY PRODUCTION AVERAGES ===" -ForegroundColor Cyan
Write-Host "UTC Time | G(i) Avg | H_sun Avg | T2m Avg | WS10m Avg | Int Avg | Count" -ForegroundColor White
Write-Host ("-" * 80) -ForegroundColor White

$results = @{}

foreach ($hour in $targetHours) {
    $hourData = $filteredData | Where-Object { $_.Hour -eq $hour }
    
    if ($hourData.Count -gt 0) {
        $gIAvg = ($hourData | Measure-Object -Property GI -Average).Average
        $hSunAvg = ($hourData | Measure-Object -Property HSun -Average).Average
        $t2mAvg = ($hourData | Measure-Object -Property T2m -Average).Average
        $ws10mAvg = ($hourData | Measure-Object -Property WS10m -Average).Average
        $intAvg = ($hourData | Measure-Object -Property Intensity -Average).Average
        
        $results[$hour] = @{
            GI = $gIAvg
            HSun = $hSunAvg
            T2m = $t2mAvg
            WS10m = $ws10mAvg
            Intensity = $intAvg
            Count = $hourData.Count
        }
        
        Write-Host ("   {0:D2}   | {1,8:F2} | {2,8:F2} | {3,6:F2} | {4,8:F2} | {5,6:F2} | {6,5:D}" -f $hour, $gIAvg, $hSunAvg, $t2mAvg, $ws10mAvg, $intAvg, $hourData.Count) -ForegroundColor White
    }
    else {
        Write-Host ("   {0:D2}   | No data found" -f $hour) -ForegroundColor Red
    }
}

# Summary statistics
$uniqueYears = $april15Data | ForEach-Object { $_.Time.Substring(0,4) } | Sort-Object -Unique

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Total April 15th days analyzed: $($april15Data.Count)" -ForegroundColor White
Write-Host "Years covered: $($uniqueYears -join ', ')" -ForegroundColor White

# Show sample of data for verification
Write-Host "`n=== SAMPLE DATA (All April 15th records) ===" -ForegroundColor Cyan
foreach ($record in $april15Data) {
    Write-Host ("{0} | G(i): {1,6:F2} | H_sun: {2,6:F2} | T2m: {3,6:F2} | WS10m: {4,6:F2} | Int: {5,6:F2}" -f $record.Time, $record.GI, $record.HSun, $record.T2m, $record.WS10m, $record.Intensity) -ForegroundColor White
}

# Save results to file
$outputFile = "april15_results_15nisan.txt"
$output = @()
$output += "=== APRIL 15TH SOLAR ENERGY PRODUCTION AVERAGES ==="
$output += "UTC Time | G(i) Avg | H_sun Avg | T2m Avg | WS10m Avg | Int Avg | Count"
$output += ("-" * 80)

foreach ($hour in $targetHours) {
    if ($results.ContainsKey($hour)) {
        $result = $results[$hour]
        $output += ("   {0:D2}   | {1,8:F2} | {2,8:F2} | {3,6:F2} | {4,8:F2} | {5,6:F2} | {6,5:D}" -f $hour, $result.GI, $result.HSun, $result.T2m, $result.WS10m, $result.Intensity, $result.Count)
    }
}

$output += ""
$output += "=== SUMMARY ==="
$output += "Total April 15th days analyzed: $($april15Data.Count)"
$output += "Years covered: $($uniqueYears -join ', ')"

$output | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "`nResults saved to: $outputFile" -ForegroundColor Green
Write-Host "Analysis completed!" -ForegroundColor Green
