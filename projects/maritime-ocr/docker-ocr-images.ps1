# Docker OCRmyPDF optimization for Image Folders (Windows PowerShell)
# Usage: ./docker-ocr-images.ps1 -ImageDir "temp_pages" -OutputFile "inbox/duxiu_raster_test.pdf"

param (
    [Parameter(Mandatory=$true)] [string]$ImageDir,
    [Parameter(Mandatory=$true)] [string]$OutputFile
)

$currentDir = Get-Location
$workDir = "/home/docker"

# Get all images in the folder and map them to container paths
$imageFiles = Get-ChildItem "$ImageDir/*.png" | ForEach-Object { "$workDir/$ImageDir/" + $_.Name }
$imageArgs = $imageFiles -join " "

Write-Host "[*] Starting Raster-to-PDF OCR..." -ForegroundColor Cyan
Write-Host "[*] Source: $ImageDir"
Write-Host "[*] Total Images: $($imageFiles.Count)"
Write-Host "[*] Output: $OutputFile"

# Running OCR on the collection of images
# We use --image-dpi 300 because we know we rasterized at 300
docker run --rm -v "${currentDir}:${workDir}" jbarlow83/ocrmypdf `
    --language chi_sim+chi_tra `
    --image-dpi 300 `
    --optimize 1 `
    --jobs 8 `
    $imageFiles `
    "${workDir}/$OutputFile"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] OCR Complete: $OutputFile" -ForegroundColor Green
} else {
    Write-Host "[-] OCR Failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
