
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Polyfill fetch if needed (Node 18+ has it globally)
const fetch = global.fetch || require('node-fetch');

const envPath = path.resolve(__dirname, '.env');

async function checkSchemas() {
    // 1. Load Env
    const envVars = {};
    if (fs.existsSync(envPath)) {
        const fileStream = fs.createReadStream(envPath);
        const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });

        for await (const line of rl) {
            const trimmedLine = line.trim();
            if (!trimmedLine || trimmedLine.startsWith('#')) continue;
            const parts = trimmedLine.split('=');
            if (parts.length >= 2) {
                const key = parts[0].trim();
                let value = parts.slice(1).join('=').trim();
                if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
                    value = value.slice(1, -1);
                }
                envVars[key] = value;
            }
        }
    }

    const supabaseUrl = envVars.VITE_SUPABASE_URL || envVars.SUPABASE_URL;
    const supabaseKey = envVars.SUPABASE_SERVICE_ROLE_KEY || envVars.VITE_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseKey) {
        console.error('Missing configuration in .env');
        return;
    }

    const supabase = createClient(supabaseUrl, supabaseKey);

    console.log('Checking strategy_monitoring columns...');
    const { data: mData, error: mError } = await supabase
        .from('strategy_monitoring')
        .select('*')
        .limit(1);

    if (mError) {
        console.error('Error:', mError);
    } else if (mData && mData.length > 0) {
        console.log('Columns found:', Object.keys(mData[0]));
    } else {
        console.log('No data found in strategy_monitoring to infer columns.');
    }

    console.log('\nChecking trading_signals columns...');
    const { data: sData, error: sError } = await supabase
        .from('trading_signals')
        .select('*')
        .limit(1);

    if (sError) {
        console.error('Error:', sError);
    } else if (sData && sData.length > 0) {
        console.log('Columns found:', Object.keys(sData[0]));
    } else {
        console.log('No data found in trading_signals to infer columns.');
    }
}

checkSchemas();
