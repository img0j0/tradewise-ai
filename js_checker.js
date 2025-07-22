#!/usr/bin/env node

const fs = require('fs');

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
        { pattern: /\bawait\s+(?![\s\S]*async)/g, message: "Await used outside async function", type: "error" },
        { pattern: /\.then\(\s*async/g, message: "Async function in .then() - consider using await", type: "warning" },
        { pattern: /debugger;/g, message: "Debugger statement found", type: "warning" },
        { pattern: /\bvar\b/g, message: "Using 'var' - consider 'let' or 'const'", type: "warning" },
        { pattern: /==(?!=)/g, message: "Using '==' - consider '==='", type: "warning" },
        { pattern: /!=(?!=)/g, message: "Using '!=' - consider '!=='", type: "warning" },
        { pattern: /\beval\(/g, message: "Using eval() - security risk", type: "error" },
        { pattern: /document\.write/g, message: "Using document.write - not recommended", type: "warning" },
        { pattern: /\bwith\b/g, message: "Using 'with' statement - not recommended", type: "error" }
    ];
    
    const lines = code.split('\n');
    lines.forEach((line, index) => {
        commonIssues.forEach(issue => {
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
    
    return { errors, warnings, filename };
}

const filename = process.argv[2];
if (!filename) {
    console.log('Usage: node js_checker.js <filename>');
    process.exit(1);
}

try {
    const code = fs.readFileSync(filename, 'utf8');
    const result = checkJavaScript(code, filename);
    
    console.log(`=== JavaScript Analysis for ${result.filename} ===`);
    
    if (result.errors.length > 0) {
        console.log('\nERRORS:');
        result.errors.forEach(error => console.log(`  ${error}`));
    }
    
    if (result.warnings.length > 0) {
        console.log('\nWARNINGS:');
        result.warnings.forEach(warning => console.log(`  ${warning}`));
    }
    
    if (result.errors.length === 0 && result.warnings.length === 0) {
        console.log('\nNo issues found!');
    }
    
    console.log(`\nSummary: ${result.errors.length} errors, ${result.warnings.length} warnings\n`);
    
} catch (err) {
    console.error(`Error reading file: ${err.message}`);
    process.exit(1);
}