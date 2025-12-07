const fs = require('fs');

const filePath = 'd:/Dev/auto_stock/src/components/common/RoadmapDialog.tsx';
const content = fs.readFileSync(filePath, 'utf8');

let stack = [];
let lineNum = 1;

for (let i = 0; i < content.length; i++) {
    const char = content[i];
    if (char === '\n') {
        lineNum++;
    }

    if (char === '{' || char === '[' || char === '(') {
        stack.push({ char, line: lineNum });
    } else if (char === '}' || char === ']' || char === ')') {
        if (stack.length === 0) {
            console.log(`Error: Unmatched ${char} at line ${lineNum}`);
            process.exit(1);
        }
        const last = stack.pop();
        if ((char === '}' && last.char !== '{') ||
            (char === ']' && last.char !== '[') ||
            (char === ')' && last.char !== '(')) {
            console.log(`Error: Mismatched ${char} at line ${lineNum}. Expected matches ${last.char} from line ${last.line}`);
            process.exit(1);
        }
    }
}

if (stack.length > 0) {
    const last = stack[stack.length - 1];
    console.log(`Error: Unclosed ${last.char} from line ${last.line}`);
} else {
    console.log('All braces matched correctly.');
}
