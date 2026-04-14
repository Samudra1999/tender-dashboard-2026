# Disable AMD Audio Devices to prevent conflicts with Realtek
Get-PnpDevice -FriendlyName "*AMD High Definition Audio*" -ErrorAction SilentlyContinue | Disable-PnpDevice -Confirm:$false
Get-PnpDevice -FriendlyName "*AMD Streaming Audio*" -ErrorAction SilentlyContinue | Disable-PnpDevice -Confirm:$false

# Disable USB Selective Suspend (AC and DC) to prevent micro-stutters
powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bea73fc56d 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
powercfg /SETDCVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bea73fc56d 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0

# Disable PCI Express Link State Power Management (AC and DC) to prevent DPC latency spikes
powercfg /SETACVALUEINDEX SCHEME_CURRENT 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a558cb4 0
powercfg /SETDCVALUEINDEX SCHEME_CURRENT 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a558cb4 0

# Apply Power Settings
powercfg /S SCHEME_CURRENT

Write-Host "Fixes applied! You can close this window now. Please restart your PC afterwards."
Start-Sleep -Seconds 5
