# Maritime Knowledge Batch Factory (Windows PowerShell)
# Automatically processes all PDFs in the inbox through the High-Fidelity Pipeline.

Write-Host "==========================================" -ForegroundColor Green
Write-Host "   MARITIME KNOWLEDGE BATCH FACTORY v1.0  " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$inbox = "inbox"
$processed = "processed"
$temp = "temp_pages"

if (-not (Test-Path $processed)) { New-Item -ItemType Directory $processed }
if (-not (Test-Path $temp)) { New-Item -ItemType Directory $temp }

$files = Get-ChildItem "$inbox/*.pdf"

if ($files.Count -eq 0) {
    Write-Host "[!] No PDF files found in $inbox. Exiting." -ForegroundColor Yellow
    exit
}

Write-Host "[*] Found $($files.Count) files to process."

foreach ($file in $files) {
    $baseName = $file.BaseName
    $outputPdf = "$processed/${baseName}_searchable.pdf"
    
    Write-Host "`n>>> Processing: $($file.Name)" -ForegroundColor Cyan
    
    # Step 1: Rasterize to Flatten (To bypass archive protection)
    Write-Host "    [1/2] Rasterizing to Flattened PDF..."
    py rasterize_pdf.py "$($file.FullName)" "$temp"
    
    # Step 2: OCR and Optimize
    Write-Host "    [2/2] Running Optimized OCR Pipeline..."
    powershell -ExecutionPolicy Bypass -File .\docker-ocr.ps1 -InputFile "$temp/flattened_input.pdf" -OutputFile "$outputPdf"
    
    if (Test-Path $outputPdf) {
        Write-Host "[+] SUCCESS: $outputPdf is ready for NotebookLM." -ForegroundColor Green
        # Cleanup temp
        Remove-Item "$temp/*" -Force
    } else {
        Write-Host "[-] FAILED to process $($file.Name)" -ForegroundColor Red
    }
}

Write-Host "`n[***] BATCH COMPLETE [***]" -ForegroundColor Green
