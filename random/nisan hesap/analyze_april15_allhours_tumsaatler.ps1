# PowerShell script to analyze April 15th solar energy data for ALL HOURS
# Calculate averages for UTC times: 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23

Write-Host "Reading CSV file for April 15th analysis - ALL HOURS..." -ForegroundColor Green

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

# All hours from 00 to 23
$allHours = @(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)
$filteredData = $april15Data | Where-Object { $_.Hour -in $allHours }

Write-Host "April 15th records for all hours (00-23): $($filteredData.Count)" -ForegroundColor Yellow

# Calculate averages for each hour
Write-Host "`n=== APRIL 15TH SOLAR ENERGY PRODUCTION AVERAGES - ALL HOURS ===" -ForegroundColor Cyan
Write-Host "UTC Time | G(i) Avg | H_sun Avg | T2m Avg | WS10m Avg | Int Avg | Count" -ForegroundColor White
Write-Host ("-" * 80) -ForegroundColor White

$results = @{}

foreach ($hour in $allHours) {
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

# Find peak production hours
$peakHours = $results.GetEnumerator() | Sort-Object Value.GI -Descending | Select-Object -First 5
Write-Host "`n=== TOP 5 PEAK PRODUCTION HOURS ===" -ForegroundColor Cyan
foreach ($peak in $peakHours) {
    Write-Host ("UTC {0:D2}:00 - G(i): {1,6:F2} W/m²" -f $peak.Key, $peak.Value.GI) -ForegroundColor White
}

# Find minimum production hours
$minHours = $results.GetEnumerator() | Sort-Object Value.GI | Select-Object -First 5
Write-Host "`n=== TOP 5 MINIMUM PRODUCTION HOURS ===" -ForegroundColor Cyan
foreach ($min in $minHours) {
    Write-Host ("UTC {0:D2}:00 - G(i): {1,6:F2} W/m²" -f $min.Key, $min.Value.GI) -ForegroundColor White
}

# Save results to file
$outputFile = "april15_allhours_results_tumsaatler.txt"
$output = @()
$output += "=== APRIL 15TH SOLAR ENERGY PRODUCTION AVERAGES - ALL HOURS ==="
$output += "UTC Time | G(i) Avg | H_sun Avg | T2m Avg | WS10m Avg | Int Avg | Count"
$output += ("-" * 80)

foreach ($hour in $allHours) {
    if ($results.ContainsKey($hour)) {
        $result = $results[$hour]
        $output += ("   {0:D2}   | {1,8:F2} | {2,8:F2} | {3,6:F2} | {4,8:F2} | {5,6:F2} | {6,5:D}" -f $hour, $result.GI, $result.HSun, $result.T2m, $result.WS10m, $result.Intensity, $result.Count)
    }
}

$output += ""
$output += "=== SUMMARY ==="
$output += "Total April 15th days analyzed: $($april15Data.Count)"
$output += "Years covered: $($uniqueYears -join ', ')"

$output += ""
$output += "=== TOP 5 PEAK PRODUCTION HOURS ==="
foreach ($peak in $peakHours) {
    $output += ("UTC {0:D2}:00 - G(i): {1,6:F2} W/m²" -f $peak.Key, $peak.Value.GI)
}

$output += ""
$output += "=== TOP 5 MINIMUM PRODUCTION HOURS ==="
foreach ($min in $minHours) {
    $output += ("UTC {0:D2}:00 - G(i): {1,6:F2} W/m²" -f $min.Key, $min.Value.GI)
}

$output | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "`nResults saved to: $outputFile" -ForegroundColor Green
Write-Host "Analysis completed!" -ForegroundColor Green
