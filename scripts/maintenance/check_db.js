
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const envPath = path.resolve(__dirname, '../../.env');

async function processLineByLine() {
    if (!fs.existsSync(envPath)) {
        console.error('.env file not found');
        return;
    }

    const fileStream = fs.createReadStream(envPath);

    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    const envVars = {};

    for await (const line of rl) {
        if (line.includes('SUPABASE')) {
            console.log('Found SUPABASE line:', line);
        }

        const trimmedLine = line.trim();
        if (!trimmedLine || trimmedLine.startsWith('#')) continue;

        const parts = trimmedLine.split('=');
        if (parts.length >= 2) {
            const key = parts[0].trim();
            let value = parts.slice(1).join('=').trim();

            // Extract JWT token if present (starts with eyJ)
            const jwtMatch = value.match(/(eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+)/);
            if (jwtMatch) {
                value = jwtMatch[0];
            } else {
                if (value.includes(' #')) {
                    value = value.split(' #')[0].trim();
                }
            }

            if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
                value = value.slice(1, -1);
            }
            envVars[key] = value;
        }
    }

    const supabaseUrl = envVars.VITE_SUPABASE_URL || envVars.SUPABASE_URL;
    // Prioritize VITE key because we saw the other one is broken/commented
    const supabaseKey = envVars.VITE_SUPABASE_ANON_KEY || envVars.SUPABASE_SERVICE_ROLE_KEY || envVars.SUPABASE_SERVICE_KEY;

    if (!supabaseUrl || !supabaseKey) {
        console.error('Missing Supabase credentials');
        return;
    }

    console.log('Credentials found. Connecting to Supabase...');
    console.log('Key length:', supabaseKey.length);
    console.log('Key start:', supabaseKey.substring(0, 10));

    const supabase = createClient(supabaseUrl, supabaseKey);

    console.log('Checking active strategies...');
    const { data: strategies, error: strategyError } = await supabase
        .from('strategies')
        .select('*')
        .eq('is_active', true);

    if (strategyError) {
        console.error('Error fetching strategies:', strategyError);
    } else {
        console.log(`Found ${strategies.length} active strategies:`);
        strategies.forEach(s => console.log(`- [${s.id}] ${s.name} (Auto: ${s.auto_trade_enabled})`));
    }

    // Check RPC
    console.log('\nTesting RPC get_active_strategies_with_universe...');
    const { data: rpcData, error: rpcError } = await supabase
        .rpc('get_active_strategies_with_universe');

    if (rpcError) {
        console.error('Error calling RPC:', rpcError);
    } else {
        console.log(`RPC returned ${rpcData ? rpcData.length : 0} rows`);
        if (rpcData && rpcData.length > 0) {
            console.log('Sample row:', rpcData[0]);
        }
    }

    console.log('\nChecking kw_account_balance...');
    const { data: balance, error: balanceError } = await supabase
        .from('kw_account_balance')
        .select('*')
        .limit(1);

    if (balanceError) console.error(balanceError);
    else console.log('Balance:', balance);

    console.log('\nChecking kw_portfolio...');
    const { data: portfolio, error: portfolioError } = await supabase
        .from('kw_portfolio')
        .select('*')
        .limit(5);

    if (portfolioError) console.error(portfolioError);
    else console.log(`Portfolio items: ${portfolio.length}`);
}

processLineByLine();
