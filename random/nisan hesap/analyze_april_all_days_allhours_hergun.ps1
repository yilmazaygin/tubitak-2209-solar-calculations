# PowerShell script to analyze ALL APRIL DAYS solar energy data for ALL HOURS
# Calculate averages for UTC times: 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23
# For each day from April 1st to April 30th

Write-Host "Reading CSV file for ALL APRIL DAYS analysis - ALL HOURS..." -ForegroundColor Green

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

# Parse ALL April data
$aprilData = @()
$totalRecords = 0

for ($i = $dataStart; $i -lt $content.Length; $i++) {
    $line = $content[$i].Trim()
    if ($line -and $line.Contains(",")) {
        $totalRecords++
        $parts = $line.Split(",")
        if ($parts.Length -ge 6) {
            $timeStr = $parts[0]
            # Check if it's April data (format: YYYY04DD:HHMM)
            if ($timeStr -match "^\d{4}04\d{2}:\d{4}$") {
                try {
                    $gI = [double]$parts[1]
                    $hSun = [double]$parts[2]
                    $t2m = [double]$parts[3]
                    $ws10m = [double]$parts[4]
                    $intensity = [double]$parts[5]
                    
                    # Extract day and hour from time string
                    $day = [int]$timeStr.Substring(6,2)
                    $hour = [int]$timeStr.Split(":")[1].Substring(0,2)
                    
                    $aprilData += @{
                        Time = $timeStr
                        Day = $day
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
Write-Host "April records found: $($aprilData.Count)" -ForegroundColor Yellow

if ($aprilData.Count -eq 0) {
    Write-Host "No April data found!" -ForegroundColor Red
    exit
}

# All hours from 00 to 23
$allHours = @(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)
# All days from 01 to 30
$allDays = @(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30)

Write-Host "April records for all hours (00-23): $($aprilData.Count)" -ForegroundColor Yellow

# Calculate averages for each day and each hour
Write-Host "`n=== ALL APRIL DAYS SOLAR ENERGY PRODUCTION AVERAGES - ALL HOURS ===" -ForegroundColor Cyan

$allResults = @{}

foreach ($day in $allDays) {
    Write-Host "`n--- APRIL $($day.ToString("D2")) ---" -ForegroundColor Magenta
    
    $dayData = $aprilData | Where-Object { $_.Day -eq $day }
    
    if ($dayData.Count -eq 0) {
        Write-Host "No data found for April $($day.ToString("D2"))" -ForegroundColor Red
        continue
    }
    
    Write-Host "UTC Time | G(i) Avg | H_sun Avg | T2m Avg | WS10m Avg | Int Avg | Count" -ForegroundColor White
    Write-Host ("-" * 80) -ForegroundColor White
    
    $dayResults = @{}
    
    foreach ($hour in $allHours) {
        $hourData = $dayData | Where-Object { $_.Hour -eq $hour }
        
        if ($hourData.Count -gt 0) {
            $gIAvg = ($hourData | Measure-Object -Property GI -Average).Average
            $hSunAvg = ($hourData | Measure-Object -Property HSun -Average).Average
            $t2mAvg = ($hourData | Measure-Object -Property T2m -Average).Average
            $ws10mAvg = ($hourData | Measure-Object -Property WS10m -Average).Average
            $intAvg = ($hourData | Measure-Object -Property Intensity -Average).Average
            
            $dayResults[$hour] = @{
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
    
    $allResults[$day] = $dayResults
    
    # Find peak production hour for this day
    $peakHour = $dayResults.GetEnumerator() | Sort-Object Value.GI -Descending | Select-Object -First 1
    if ($peakHour) {
        Write-Host ("Peak production: UTC {0:D2}:00 - G(i): {1,6:F2} W/m²" -f $peakHour.Key, $peakHour.Value.GI) -ForegroundColor Yellow
    }
}

# Summary statistics
$uniqueYears = $aprilData | ForEach-Object { $_.Time.Substring(0,4) } | Sort-Object -Unique
$uniqueDays = $aprilData | ForEach-Object { $_.Day } | Sort-Object -Unique

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Total April days analyzed: $($uniqueDays.Count)" -ForegroundColor White
Write-Host "Days covered: $($uniqueDays -join ', ')" -ForegroundColor White
Write-Host "Years covered: $($uniqueYears -join ', ')" -ForegroundColor White

# Find overall peak production day and hour
$overallPeak = $null
$overallPeakValue = 0
$overallPeakDay = 0
$overallPeakHour = 0

foreach ($day in $allResults.Keys) {
    foreach ($hour in $allResults[$day].Keys) {
        $value = $allResults[$day][$hour].GI
        if ($value -gt $overallPeakValue) {
            $overallPeakValue = $value
            $overallPeakDay = $day
            $overallPeakHour = $hour
        }
    }
}

Write-Host "`n=== OVERALL PEAK PRODUCTION ===" -ForegroundColor Cyan
Write-Host "Peak: April $($overallPeakDay.ToString("D2")) UTC $($overallPeakHour.ToString("D2")):00 - G(i): $($overallPeakValue.ToString("F2")) W/m²" -ForegroundColor White

# Save results to file
$outputFile = "april_all_days_allhours_results_hergun.txt"
$output = @()
$output += "=== ALL APRIL DAYS SOLAR ENERGY PRODUCTION AVERAGES - ALL HOURS ==="

foreach ($day in $allDays) {
    $output += ""
    $output += "--- APRIL $($day.ToString("D2")) ---"
    
    if ($allResults.ContainsKey($day)) {
        $dayResults = $allResults[$day]
        $output += "UTC Time | G(i) Avg | H_sun Avg | T2m Avg | WS10m Avg | Int Avg | Count"
        $output += ("-" * 80)
        
        foreach ($hour in $allHours) {
            if ($dayResults.ContainsKey($hour)) {
                $result = $dayResults[$hour]
                $output += ("   {0:D2}   | {1,8:F2} | {2,8:F2} | {3,6:F2} | {4,8:F2} | {5,6:F2} | {6,5:D}" -f $hour, $result.GI, $result.HSun, $result.T2m, $result.WS10m, $result.Intensity, $result.Count)
            }
        }
        
        # Add peak production for this day
        $peakHour = $dayResults.GetEnumerator() | Sort-Object Value.GI -Descending | Select-Object -First 1
        if ($peakHour) {
            $output += ("Peak production: UTC {0:D2}:00 - G(i): {1,6:F2} W/m²" -f $peakHour.Key, $peakHour.Value.GI)
        }
    }
    else {
        $output += "No data found for April $($day.ToString("D2"))"
    }
}

$output += ""
$output += "=== SUMMARY ==="
$output += "Total April days analyzed: $($uniqueDays.Count)"
$output += "Days covered: $($uniqueDays -join ', ')"
$output += "Years covered: $($uniqueYears -join ', ')"

$output += ""
$output += "=== OVERALL PEAK PRODUCTION ==="
$output += "Peak: April $($overallPeakDay.ToString("D2")) UTC $($overallPeakHour.ToString("D2")):00 - G(i): $($overallPeakValue.ToString("F2")) W/m²"

$output | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "`nResults saved to: $outputFile" -ForegroundColor Green
Write-Host "Analysis completed!" -ForegroundColor Green
