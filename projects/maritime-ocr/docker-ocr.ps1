# Pro-Level Optimized Docker OCRmyPDF for Windows PowerShell
# Usage: ./docker-ocr.ps1 -InputFile "xxx.pdf" -OutputFile "xxx_ocr.pdf" [-Pages "1-10"]

param (
    [Parameter(Mandatory=$true)] [string]$InputFile,
    [Parameter(Mandatory=$true)] [string]$OutputFile,
    [string]$Pages = ""  # Optional page range for testing
)

$currentDir = Get-Location
$workDir = "/home/docker"

Write-Host "[*] Starting PRO-Optimized OCR Factory..." -ForegroundColor Cyan
Write-Host "[*] Input: $InputFile"
Write-Host "[*] Output: $OutputFile"

$pageArg = if ($Pages -ne "") { "--pages $Pages" } else { "" }

# Use --optimize 3 for maximum compression (suitable for NotebookLM)
# Use --force-ocr because we usually use this after rasterization
docker run --rm -v "${currentDir}:${workDir}" jbarlow83/ocrmypdf `
    --language chi_sim `
    --force-ocr `
    --image-dpi 150 `
    --deskew `
    --clean `
    --optimize 3 `
    --jobs 8 `
    $pageArg `
    "${workDir}/$InputFile" `
    "${workDir}/$OutputFile"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] OCR & Optimization Complete: $OutputFile" -ForegroundColor Green
} else {
    Write-Host "[-] OCR Failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
