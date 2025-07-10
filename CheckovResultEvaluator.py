#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

# Get the filename from command line arguments
if len(sys.argv) > 1:
    results_file = sys.argv[1]  # This will contain $BITBUCKET_CLONE_DIR/twistlock/scan-results.json
else:
    results_file = 'scan-results.json'  # Default filename if no argument is provided

# Load ignore list from .twistlock.ignore.json if it exists
ignore_list = {}
valid_ignores = {}
expired_ignores = {}
ignore_file_path = '.github/workflows/.twistlock.ignore.json'

# Current date for checking if ignores are still valid
current_date = datetime.now()

if os.path.exists(ignore_file_path):
    try:
        with open(ignore_file_path, 'r') as ignore_file:
            ignore_list = json.load(ignore_file)
            
        # Process the ignore list to separate valid and expired entries
        for cve_id, expiry_date_str in ignore_list.items():
            try:
                # Parse the expiry date
                expiry_date = datetime.strptime(expiry_date_str, '%d-%m-%Y')
                
                # Check if the ignore is still valid
                if expiry_date >= current_date:
                    valid_ignores[cve_id] = expiry_date_str
                else:
                    expired_ignores[cve_id] = expiry_date_str
            except ValueError:
                print(f"Warning: Invalid date format for {cve_id}: {expiry_date_str}. Expected format: DD-MM-YYYY")
                # If date format is invalid, don't add to valid ignores
        
        print(f"Loaded ignore list with {len(ignore_list)} entries")
        print(f"  - {len(valid_ignores)} valid")
        print(f"  - {len(expired_ignores)} expired ignores")
        
    except Exception as e:
        print(f"Warning: Could not load ignore list: {e}")

# Load Checkov results
with open(results_file, 'r') as f:
    try:
        results = json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON output from Checkov")
        sys.exit(0)  # Don't fail on parsing errors

# Track if we need to fail the build
should_fail = False
fixable_vulnerabilities = []
skipped_vulnerabilities = []
expired_vulnerability_ignores = []

# Process each check result
for result in results.get('results', []):
    print(f"Processing result for {result.get('id', 'unknown')}...")
    for vulnerability in result.get('vulnerabilities', []):
        status = vulnerability.get('status')
        packagePath = vulnerability.get('packagePath', 'unknown')
        
        if packagePath.endswith("twistlock/twistcli"):
            continue

        # Skip if not a vulnerability or no details
        if not status:
            continue
            
        # Check if fixed versions are available
        fixed_versions = "fixed" in status
        if fixed_versions:
            package_name = vulnerability.get('packageName', 'unknown')
            current_version = vulnerability.get('packageVersion', 'unknown')
            cve_id = vulnerability.get('id', 'unknown')
            severity = vulnerability.get('severity', 'unknown').upper()
            
            vuln_info = {
                'package': package_name,
                'current': current_version,
                'fixed_in': status,
                'cve': cve_id,
                'severity': severity
            }
            
            # Check if this vulnerability should be ignored (and ignore is valid)
            if cve_id in valid_ignores:
                # Add to skipped list but don't fail the build
                skipped_vulnerabilities.append({
                    **vuln_info,
                    'ignored_until': valid_ignores[cve_id]
                })
            # Check if this is an expired ignore
            elif cve_id in expired_ignores:
                # Add to expired list and mark to fail the build
                should_fail = True
                expired_vulnerability_ignores.append({
                    **vuln_info, 
                    'expired_on': expired_ignores[cve_id]
                })
                fixable_vulnerabilities.append(vuln_info)
            else:
                # Not in ignore list, add to fixable and fail the build
                should_fail = True
                fixable_vulnerabilities.append(vuln_info)

# Display summary of skipped vulnerabilities
if skipped_vulnerabilities:
    print("\n⚠️ SKIPPED VULNERABILITIES (IGNORED) ⚠️")
    print("=========================================")
    print(f"Skipped {len(skipped_vulnerabilities)} vulnerabilities based on ignore list:")
    
    for vuln in skipped_vulnerabilities:
        print(f"  - {vuln['package']} {vuln['current']} → {vuln['fixed_in']} ({vuln['cve']}) - Ignored until {vuln['ignored_until']}")

# Display summary of expired ignores
if expired_vulnerability_ignores:
    print("\n⏰ EXPIRED IGNORE ENTRIES FOUND ⏰")
    print("=================================")
    print(f"Found {len(expired_vulnerability_ignores)} vulnerabilities with expired ignore entries:")
    
    for vuln in expired_vulnerability_ignores:
        print(f"  - {vuln['package']} {vuln['current']} → {vuln['fixed_in']} ({vuln['cve']}) - Ignore expired on {vuln['expired_on']}")
    
    print("\nPlease update the ignore dates or fix these vulnerabilities.")

# Display summary of fixable vulnerabilities
if fixable_vulnerabilities:
    print("\n🚨 FIXABLE SECURITY VULNERABILITIES FOUND 🚨")
    print("=============================================")
    print(f"Found {len(fixable_vulnerabilities)} vulnerabilities with available fixes:")
    
    # Group by severity for better reporting
    by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
    for vuln in fixable_vulnerabilities:
        by_severity.get(vuln['severity'], []).append(vuln)
    
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        vulns = by_severity.get(severity, [])
        if vulns:
            print(f"\n{severity} Severity ({len(vulns)}):")
            for vuln in vulns:
                print(f"  - {vuln['package']} {vuln['current']} → {vuln['fixed_in']} ({vuln['cve']})")
    
    # Exit with error if we should fail
    if should_fail:
        print("\n❌ Build failed due to fixable security vulnerabilities")
        sys.exit(1)
elif skipped_vulnerabilities:
    print("\n✅ All vulnerabilities are in the ignore list with valid dates")
else:
    print("✅ No fixable vulnerabilities found")
    
sys.exit(0)