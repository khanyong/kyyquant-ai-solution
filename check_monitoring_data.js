
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Polyfill fetch
const fetch = global.fetch || require('node-fetch');

const envPath = path.resolve(__dirname, '.env');

async function checkMonitoringData() {
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
    // Try all possible key names and TRIM whitespace
    let supabaseKey = envVars.SUPABASE_SERVICE_KEY || envVars.SUPABASE_SERVICE_ROLE_KEY || envVars.VITE_SUPABASE_ANON_KEY;
    if (supabaseKey) supabaseKey = supabaseKey.trim();

    if (!supabaseUrl || !supabaseKey) {
        console.error('Missing configuration in .env');
        console.log('URL:', supabaseUrl);
        console.log('Key found?', !!supabaseKey);
        return;
    }

    console.log(`Using Key (Length: ${supabaseKey.length})`);
    const supabase = createClient(supabaseUrl, supabaseKey);

    console.log('Checking strategy_monitoring table...');

    // Get all rows for the strategy (we saw the ID in previous logs: 57fe4599...)
    // But let's just get all to be safe
    const { data, error } = await supabase
        .from('strategy_monitoring')
        .select('*')
        .order('updated_at', { ascending: false })
        .limit(10);

    if (error) {
        console.error('Error fetching monitoring data:', error);
    } else {
        console.log(`Found ${data.length} rows.`);
        if (data.length > 0) {
            console.log('Most recent update:', data[0].updated_at);
            console.log('Sample Row:', JSON.stringify(data[0], null, 2));
        } else {
            console.log('Table is empty.');
        }
    }
}

checkMonitoringData();
