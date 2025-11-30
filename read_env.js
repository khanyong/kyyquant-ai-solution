const fs = require('fs');
const path = require('path');

try {
    const envPath = path.resolve(__dirname, '.env');
    const content = fs.readFileSync(envPath, 'utf8');
    const lines = content.split('\n');
    lines.forEach(line => {
        if (line.startsWith('VITE_SUPABASE_ANON_KEY=')) {
            console.log(line.split('=')[1].trim());
        }
    });
} catch (err) {
    console.error(err);
}
