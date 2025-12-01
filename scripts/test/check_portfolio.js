
require('dotenv').config({ path: '.env' });
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error('Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing in .env');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkPortfolio() {
    console.log('Checking kw_portfolio table...');

    const { data, error } = await supabase
        .from('kw_portfolio')
        .select('*');

    if (error) {
        console.error('Error fetching portfolio:', error);
        return;
    }

    console.log(`Found ${data.length} records in kw_portfolio:`);
    if (data.length > 0) {
        console.table(data);
    } else {
        console.log('Table is empty.');
    }
}

checkPortfolio();
