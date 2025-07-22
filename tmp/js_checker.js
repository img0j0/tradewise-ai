#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Simple JavaScript syntax checker and common error detector
function checkJavaScript(code, filename) {
    const errors = [];
    const warnings = [];
    
    // Check for syntax errors by trying to parse
    try {
        new Function(code);
    } catch (e) {
        errors.push(`Syntax Error: ${e.message}`);
    }
    
    // Common error patterns
    const commonIssues = [
        { pattern: /\bawait\b(?![^(]*\))/g, message: "Await used outside async function", type: "error" },
        { pattern: /\.then\(\s*async/g, message: "Async function in .then() - consider using await", type: "warning" },
        { pattern: /console\.log\(/g, message: "Console.log found - consider removing for production", type: "info" },
        { pattern: /debugger;/g, message: "Debugger statement found", type: "warning" },
        { pattern: /\bvar\b/g, message: "Using 'var' - consider 'let' or 'const'", type: "warning" },
        { pattern: /==(?!=)/g, message: "Using '==' - consider '==='", type: "warning" },
        { pattern: /!=(?!=)/g, message: "Using '!=' - consider '!=='", type: "warning" },
        { pattern: /\beval\(/g, message: "Using eval() - security risk", type: "error" },
        { pattern: /document\.write/g, message: "Using document.write - not recommended", type: "warning" },
        { pattern: /setTimeout\(\s*"[^"]*"/g, message: "setTimeout with string - use function", type: "warning" },
        { pattern: /\bwith\b/g, message: "Using 'with' statement - not recommended", type: "error" },
        { pattern: /function\s+\w+\s*\([^)]*\)\s*{[^}]*return[^}]*}\s*function/g, message: "Potential unreachable code", type: "warning" }
    ];
    
    commonIssues.forEach(issue => {
        let match;
        let lineNum = 1;
        const lines = code.split('\n');
        
        lines.forEach((line, index) => {
            if (issue.pattern.test(line)) {
                const msg = `Line ${index + 1}: ${issue.message}`;
                if (issue.type === 'error') {
                    errors.push(msg);
                } else {
                    warnings.push(msg);
                }
            }
        });
    });
    
    // Check for missing semicolons (simple heuristic)
    const lines = code.split('\n');
    lines.forEach((line, index) => {
        const trimmed = line.trim();
        if (trimmed.length > 0 && 
            !trimmed.endsWith(';') && 
            !trimmed.endsWith('{') && 
            !trimmed.endsWith('}') && 
            !trimmed.startsWith('//') && 
            !trimmed.startsWith('/*') && 
            !trimmed.includes('*/') &&
            !trimmed.endsWith(',') &&
            !/^(if|for|while|switch|try|catch|finally|else|function|class|const|let|var)\b/.test(trimmed) &&
            !/^\s*(return|break|continue|throw)\b/.test(trimmed) &&
            trimmed !== '' && 
            trimmed !== '}' && 
            trimmed !== '{') {
            warnings.push(`Line ${index + 1}: Possible missing semicolon: "${trimmed}"`);
        }
    });
    
    return { errors, warnings, filename };
}

// Check if running as script
if (require.main === module) {
    const filename = process.argv[2];
    if (!filename) {
        console.log('Usage: node js_checker.js <filename>');
        process.exit(1);
    }
    
    try {
        const code = fs.readFileSync(filename, 'utf8');
        const result = checkJavaScript(code, filename);
        
        console.log(`\n=== JavaScript Analysis for ${result.filename} ===`);
        
        if (result.errors.length > 0) {
            console.log('\n🔴 ERRORS:');
            result.errors.forEach(error => console.log(`  ${error}`));
        }
        
        if (result.warnings.length > 0) {
            console.log('\n🟡 WARNINGS:');
            result.warnings.forEach(warning => console.log(`  ${warning}`));
        }
        
        if (result.errors.length === 0 && result.warnings.length === 0) {
            console.log('\n✅ No issues found!');
        }
        
        console.log(`\nSummary: ${result.errors.length} errors, ${result.warnings.length} warnings\n`);
        
    } catch (err) {
        console.error(`Error reading file: ${err.message}`);
        process.exit(1);
    }
}

module.exports = { checkJavaScript };