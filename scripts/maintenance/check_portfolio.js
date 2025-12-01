
const { createClient } = require('@supabase/supabase-js');

// Config from user logs
const SUPABASE_URL = 'https://hznkyaomtrpzcayayayh.supabase.co';
const SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjU1MDAwOSwiZXhwIjoyMDcyMTI2MDA5fQ.KAF1lMwtH1VTknteieCmaolCTFkESgrzLJYuqiUlDrM';
const USER_ID = 'f912da32-897f-4dbb-9242-3a438e9733a8';

async function checkPortfolio() {
    console.log('Initializing Supabase client...');
    const supabase = createClient(SUPABASE_URL, SERVICE_KEY);

    console.log(`Checking kw_portfolio for user: ${USER_ID}`);

    const { data, error } = await supabase
        .from('kw_portfolio')
        .select('*')
        .eq('user_id', USER_ID);

    if (error) {
        console.error('Error fetching portfolio:', error);
    } else {
        console.log(`Found ${data.length} portfolio items.`);
        if (data.length > 0) {
            console.log('Sample item:', JSON.stringify(data[0], null, 2));
        } else {
            console.log('Portfolio is empty for this user.');
        }
    }
}

checkPortfolio();
