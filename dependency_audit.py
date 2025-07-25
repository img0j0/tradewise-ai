#!/usr/bin/env python3
"""
Dependency Security Audit for TradeWise AI
Analyzes and validates production dependencies for security vulnerabilities
"""

import subprocess
import json
import sys
from pathlib import Path
import pkg_resources
from datetime import datetime

class DependencyAuditor:
    """Security auditor for Python dependencies"""
    
    def __init__(self):
        self.project_root = Path('.')
        self.pyproject_path = self.project_root / 'pyproject.toml'
        self.requirements_path = self.project_root / 'requirements.txt'
        
    def audit_dependencies(self):
        """Comprehensive dependency security audit"""
        print("🔍 Starting dependency security audit...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'installed_packages': self._get_installed_packages(),
            'security_vulnerabilities': self._check_vulnerabilities(),
            'outdated_packages': self._check_outdated(),
            'dependency_tree': self._analyze_dependency_tree(),
            'recommendations': []
        }
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        # Save audit report
        self._save_audit_report(results)
        
        return results
    
    def _get_installed_packages(self):
        """Get list of currently installed packages"""
        try:
            result = subprocess.run(['pip', 'list', '--format=json'], 
                                  capture_output=True, text=True, check=True)
            packages = json.loads(result.stdout)
            
            return {
                'count': len(packages),
                'packages': {pkg['name']: pkg['version'] for pkg in packages}
            }
        except Exception as e:
            return {'error': str(e), 'packages': {}}
    
    def _check_vulnerabilities(self):
        """Check for known security vulnerabilities"""
        try:
            # Try to use pip-audit if available
            result = subprocess.run(['pip-audit', '--format=json', '--no-deps'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                return {
                    'tool': 'pip-audit',
                    'vulnerabilities_found': len(vulnerabilities),
                    'details': vulnerabilities
                }
            else:
                # Fallback to safety if pip-audit not available
                return self._check_with_safety()
                
        except FileNotFoundError:
            return self._check_with_safety()
    
    def _check_with_safety(self):
        """Fallback vulnerability check with safety"""
        try:
            result = subprocess.run(['safety', 'check', '--json'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'tool': 'safety',
                    'vulnerabilities_found': 0,
                    'details': []
                }
            else:
                # Parse safety output
                vulnerabilities = json.loads(result.stdout) if result.stdout else []
                return {
                    'tool': 'safety',
                    'vulnerabilities_found': len(vulnerabilities),
                    'details': vulnerabilities
                }
                
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'tool': 'manual',
                'vulnerabilities_found': 0,
                'details': [],
                'note': 'No vulnerability scanning tools available'
            }
    
    def _check_outdated(self):
        """Check for outdated packages"""
        try:
            result = subprocess.run(['pip', 'list', '--outdated', '--format=json'], 
                                  capture_output=True, text=True, check=True)
            outdated = json.loads(result.stdout)
            
            return {
                'count': len(outdated),
                'packages': {pkg['name']: {
                    'current': pkg['version'],
                    'latest': pkg['latest_version']
                } for pkg in outdated}
            }
        except Exception as e:
            return {'error': str(e), 'packages': {}}
    
    def _analyze_dependency_tree(self):
        """Analyze dependency relationships"""
        try:
            # Get dependency tree
            result = subprocess.run(['pipdeptree', '--json'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                tree = json.loads(result.stdout)
                
                # Count direct vs transitive dependencies
                direct_deps = len([pkg for pkg in tree if not pkg.get('dependencies')])
                total_deps = len(tree)
                
                return {
                    'total_packages': total_deps,
                    'direct_dependencies': direct_deps,
                    'transitive_dependencies': total_deps - direct_deps,
                    'tree_available': True
                }
            else:
                return {'tree_available': False, 'note': 'pipdeptree not available'}
                
        except FileNotFoundError:
            return {'tree_available': False, 'note': 'pipdeptree not installed'}
    
    def _generate_recommendations(self, results):
        """Generate security and maintenance recommendations"""
        recommendations = []
        
        # Vulnerability recommendations
        if results['security_vulnerabilities']['vulnerabilities_found'] > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Security',
                'issue': f"{results['security_vulnerabilities']['vulnerabilities_found']} security vulnerabilities found",
                'action': 'Update vulnerable packages immediately',
                'command': 'pip install --upgrade <package_names>'
            })
        
        # Outdated package recommendations
        outdated_count = results['outdated_packages']['count']
        if outdated_count > 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Maintenance',
                'issue': f"{outdated_count} packages are outdated",
                'action': 'Review and update outdated packages',
                'command': 'pip install --upgrade <package_names>'
            })
        
        # Dependency management recommendations
        if not self.pyproject_path.exists() and not self.requirements_path.exists():
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Dependency Management',
                'issue': 'No dependency file found',
                'action': 'Create requirements.txt or pyproject.toml',
                'command': 'pip freeze > requirements.txt'
            })
        
        # Security tools recommendations
        if results['security_vulnerabilities']['tool'] == 'manual':
            recommendations.append({
                'priority': 'LOW',
                'category': 'Tooling',
                'issue': 'No security scanning tools available',
                'action': 'Install security audit tools',
                'command': 'pip install pip-audit safety'
            })
        
        return recommendations
    
    def _save_audit_report(self, results):
        """Save audit report to file"""
        report_file = f"dependency_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Audit report saved to: {report_file}")
    
    def clean_unused_dependencies(self):
        """Identify potentially unused dependencies"""
        print("🧹 Analyzing potentially unused dependencies...")
        
        try:
            # Use pip-autoremove or pipreqs to identify unused packages
            result = subprocess.run(['pip-autoremove', '--list'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                unused = result.stdout.strip().split('\n')
                return {
                    'tool': 'pip-autoremove',
                    'unused_packages': [pkg.strip() for pkg in unused if pkg.strip()],
                    'count': len(unused)
                }
            else:
                return {'tool': 'manual', 'note': 'pip-autoremove not available'}
                
        except FileNotFoundError:
            return {'tool': 'manual', 'note': 'No cleanup tools available'}
    
    def pin_dependencies(self):
        """Generate pinned dependency file for production"""
        print("📌 Generating pinned dependencies...")
        
        try:
            # Generate exact version requirements
            result = subprocess.run(['pip', 'freeze'], 
                                  capture_output=True, text=True, check=True)
            
            # Filter out development packages
            production_packages = []
            dev_packages = {
                'pytest', 'pytest-cov', 'black', 'flake8', 'mypy',
                'pip-audit', 'safety', 'pipdeptree', 'pip-autoremove'
            }
            
            for line in result.stdout.strip().split('\n'):
                if line and not any(dev_pkg in line.lower() for dev_pkg in dev_packages):
                    production_packages.append(line)
            
            # Save production requirements
            with open('requirements_production.txt', 'w') as f:
                f.write('\n'.join(production_packages))
            
            print(f"✅ Production requirements saved to requirements_production.txt")
            print(f"📦 {len(production_packages)} production dependencies pinned")
            
            return {
                'file': 'requirements_production.txt',
                'package_count': len(production_packages),
                'excluded_dev_packages': len(dev_packages)
            }
            
        except Exception as e:
            return {'error': str(e)}

def main():
    """Main audit execution"""
    print("🔐 TradeWise AI - Dependency Security Audit")
    print("=" * 50)
    
    auditor = DependencyAuditor()
    
    # Run comprehensive audit
    results = auditor.audit_dependencies()
    
    # Print summary
    print("\n📋 AUDIT SUMMARY")
    print("-" * 30)
    print(f"Total packages: {results['installed_packages']['count']}")
    print(f"Security vulnerabilities: {results['security_vulnerabilities']['vulnerabilities_found']}")
    print(f"Outdated packages: {results['outdated_packages']['count']}")
    print(f"Recommendations: {len(results['recommendations'])}")
    
    # Print high priority recommendations
    high_priority = [r for r in results['recommendations'] if r['priority'] == 'HIGH']
    if high_priority:
        print(f"\n🚨 HIGH PRIORITY ACTIONS ({len(high_priority)})")
        print("-" * 40)
        for rec in high_priority:
            print(f"• {rec['issue']}")
            print(f"  Action: {rec['action']}")
            print(f"  Command: {rec['command']}\n")
    
    # Clean unused dependencies
    cleanup_results = auditor.clean_unused_dependencies()
    if cleanup_results.get('unused_packages'):
        print(f"🧹 Found {len(cleanup_results['unused_packages'])} potentially unused packages")
    
    # Generate production requirements
    pin_results = auditor.pin_dependencies()
    
    print("\n✅ Dependency audit completed successfully!")
    
    # Return non-zero exit code if vulnerabilities found
    if results['security_vulnerabilities']['vulnerabilities_found'] > 0:
        print("⚠️  Security vulnerabilities detected - review required")
        sys.exit(1)
    
    return results

if __name__ == '__main__':
    main()