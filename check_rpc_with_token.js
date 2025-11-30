
const { createClient } = require('@supabase/supabase-js');

// Config from user logs
const SUPABASE_URL = 'https://hznkyaomtrpzcayayayh.supabase.co';
const SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjU1MDAwOSwiZXhwIjoyMDcyMTI2MDA5fQ.KAF1lMwtH1VTknteieCmaolCTFkESgrzLJYuqiUlDrM';

async function checkRpcWithToken() {
    console.log('Initializing Supabase client with Service Role Key...');
    const supabase = createClient(SUPABASE_URL, SERVICE_KEY);

    console.log('Calling RPC get_active_strategies_with_universe...');

    const { data, error } = await supabase.rpc('get_active_strategies_with_universe');

    if (error) {
        console.error('RPC Call Failed!');
        console.error('Message:', error.message);
        console.error('Details:', error.details);
        console.error('Hint:', error.hint);
        console.error('Code:', error.code);
    } else {
        console.log(`RPC Returned ${data ? data.length : 0} rows.`);
        if (data && data.length > 0) {
            console.log('First row sample:', JSON.stringify(data[0], null, 2));
        } else {
            console.log('No data returned. The strategy might be inactive or the role check failed.');
        }
    }
}

checkRpcWithToken();
