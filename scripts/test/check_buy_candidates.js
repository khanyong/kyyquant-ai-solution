
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkCandidates() {
    console.log('Checking strategy_monitoring table...');

    // 1. Check total count
    const { count, error: countError } = await supabase
        .from('strategy_monitoring')
        .select('*', { count: 'exact', head: true });

    if (countError) {
        console.error('Error counting records:', countError);
        return;
    }
    console.log(`Total records in strategy_monitoring: ${count}`);

    // 2. Check records with score > 0
    const { data: scoredData, error: scoredError } = await supabase
        .from('strategy_monitoring')
        .select('stock_code, stock_name, condition_match_score, is_near_entry, updated_at')
        .gt('condition_match_score', 0)
        .limit(5);

    if (scoredError) {
        console.error('Error fetching scored records:', scoredError);
    } else {
        console.log('Records with score > 0:', scoredData);
    }

    // 3. Check records with is_near_entry = true
    const { data: nearData, error: nearError } = await supabase
        .from('strategy_monitoring')
        .select('stock_code, stock_name, condition_match_score, is_near_entry, updated_at')
        .eq('is_near_entry', true)
        .limit(5);

    if (nearError) {
        console.error('Error fetching near entry records:', nearError);
    } else {
        console.log('Records with is_near_entry = true:', nearData);
    }

    // 4. Call the RPC directly
    const { data: rpcData, error: rpcError } = await supabase
        .rpc('get_buy_candidates', { min_score: 0 });

    if (rpcError) {
        console.error('Error calling get_buy_candidates RPC:', rpcError);
    } else {
        console.log('RPC get_buy_candidates(0) result:', rpcData);
    }
}

checkCandidates();
