
const { createClient } = require('@supabase/supabase-js');

// Config from user logs
const SUPABASE_URL = 'https://hznkyaomtrpzcayayayh.supabase.co';
const SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjU1MDAwOSwiZXhwIjoyMDcyMTI2MDA5fQ.KAF1lMwtH1VTknteieCmaolCTFkESgrzLJYuqiUlDrM';

async function testDbInsert() {
    console.log('Initializing Supabase client...');
    const supabase = createClient(SUPABASE_URL, SERVICE_KEY);

    const testData = {
        strategy_id: '57fe4599-9e3a-4be7-9a5c-97e9535cee79',
        stock_code: 'TEST01',
        stock_name: 'Test Stock',
        current_price: 1000,
        condition_match_score: 85,
        is_near_entry: true,
        updated_at: new Date().toISOString()
    };

    console.log('Attempting to insert test row into strategy_monitoring...');

    const { data, error } = await supabase
        .from('strategy_monitoring')
        .upsert(testData)
        .select();

    if (error) {
        console.error('Insert Failed:', error);
    } else {
        console.log('Insert Success:', data);
    }
}

testDbInsert();
