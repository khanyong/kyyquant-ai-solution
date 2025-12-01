
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Load .env from root (../../.env)
const envPath = path.resolve(__dirname, '../../.env');
const envVars = {};

if (fs.existsSync(envPath)) {
    const content = fs.readFileSync(envPath, 'utf8');
    content.split('\n').forEach(line => {
        const parts = line.split('=');
        if (parts.length >= 2) {
            envVars[parts[0].trim()] = parts.slice(1).join('=').trim().replace(/['"]/g, '');
        }
    });
}

const supabaseUrl = envVars.VITE_SUPABASE_URL || envVars.SUPABASE_URL;
const supabaseKey = envVars.SUPABASE_SERVICE_ROLE_KEY || envVars.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing Supabase credentials');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkTables() {
    console.log('Checking "stocks" table...');
    const { data: stocksData, error: stocksError } = await supabase
        .from('stocks')
        .select('*')
        .eq('code', '108320');

    if (stocksError) {
        console.log('Error querying "stocks":', stocksError.message);
    } else {
        console.log('"stocks" result:', stocksData);
    }

    console.log('\nChecking "kw_stock_master" table...');
    const { data: kwData, error: kwError } = await supabase
        .from('kw_stock_master')
        .select('*')
        .eq('code', '108320');

    if (kwError) {
        console.log('Error querying "kw_stock_master":', kwError.message);
    } else {
        console.log('"kw_stock_master" result:', kwData);
    }
}

checkTables();
