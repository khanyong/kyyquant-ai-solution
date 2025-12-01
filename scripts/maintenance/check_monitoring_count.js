
const { createClient } = require('@supabase/supabase-js');

// Config from user logs
const SUPABASE_URL = 'https://hznkyaomtrpzcayayayh.supabase.co';
const SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjU1MDAwOSwiZXhwIjoyMDcyMTI2MDA5fQ.KAF1lMwtH1VTknteieCmaolCTFkESgrzLJYuqiUlDrM';

async function checkMonitoringCount() {
    console.log('Initializing Supabase client...');
    const supabase = createClient(SUPABASE_URL, SERVICE_KEY);

    console.log('Checking strategy_monitoring table count...');

    const { count, error } = await supabase
        .from('strategy_monitoring')
        .select('*', { count: 'exact', head: true });

    if (error) {
        console.error('Error checking count:', error);
    } else {
        console.log(`Total rows in strategy_monitoring: ${count}`);
    }

    // Also get a sample to see if it's recent
    const { data: sample } = await supabase
        .from('strategy_monitoring')
        .select('updated_at, stock_code, condition_match_score')
        .order('updated_at', { ascending: false })
        .limit(1);

    if (sample && sample.length > 0) {
        console.log('Most recent update:', sample[0]);
    }
}

checkMonitoringCount();
