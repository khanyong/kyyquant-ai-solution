
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Polyfill fetch if needed (Node 18+ has it globally)
const fetch = global.fetch || require('node-fetch');

const envPath = path.resolve(__dirname, '.env');

async function checkBalance() {
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
                // Simple unquote
                if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
                    value = value.slice(1, -1);
                }
                // Remove comments
                if (value.includes(' #')) value = value.split(' #')[0].trim();

                envVars[key] = value;
            }
        }
    }

    const supabaseUrl = envVars.VITE_SUPABASE_URL || envVars.SUPABASE_URL;
    // Prioritize Service Role Key for debugging to bypass RLS
    const supabaseKey = envVars.SUPABASE_SERVICE_ROLE_KEY || envVars.VITE_SUPABASE_ANON_KEY;

    // Revert to Kiwoom URL as requested
    const kiwoomBaseUrl = 'https://mockapi.kiwoom.com';

    if (!supabaseUrl || !supabaseKey) {
        console.error('Missing configuration in .env');
        return;
    }

    const supabase = createClient(supabaseUrl, supabaseKey);

    console.log('--- CONNECTION DEBUG ---');
    console.log('Supabase URL:', supabaseUrl);
    console.log('Using Service Role Key:', !!envVars.SUPABASE_SERVICE_ROLE_KEY);
    console.log('------------------------');

    console.log('Checking kw_account_balance table...');
    const { data: checkBalance, error: checkError } = await supabase
        .from('kw_account_balance')
        .select('*');

    if (checkError) {
        console.error('Read verification failed:', checkError);
    } else {
        console.log(`Found ${checkBalance.length} rows in kw_account_balance:`);
        checkBalance.forEach(row => {
            console.log(`User ID: ${row.user_id}, Total Asset: ${row.total_asset}`);
        });
    }

    console.log('\nChecking strategies table...');
    const { data: strategies, error: stratError } = await supabase
        .from('strategies')
        .select('user_id, name');

    if (stratError) {
        console.error('Strategies check failed:', stratError);
    } else {
        console.log(`Found ${strategies.length} rows in strategies:`);
        strategies.forEach(row => {
            console.log(`User ID: ${row.user_id}, Name: ${row.name}`);
        });
    }
}

checkBalance();
