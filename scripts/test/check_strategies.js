
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

async function checkData() {
    console.log('Checking database state...');

    // 1. Check strategies
    const { data: strategies, error: stratError } = await supabase
        .from('strategies')
        .select('id, name, is_active, universe')
        .eq('is_active', true);

    if (stratError) {
        console.error('Error fetching strategies:', stratError);
    } else {
        console.log(`Active Strategies: ${strategies.length}`);
        for (const s of strategies) {
            console.log(`- Strategy: ${s.name} (${s.id})`);

            // Check strategy_universes
            const { data: universes, error: uniError } = await supabase
                .from('strategy_universes')
                .select('*')
                .eq('strategy_id', s.id);

            if (uniError) console.error('  Error fetching universes:', uniError);
            else {
                console.log(`  Linked Universes: ${universes.length}`);
                universes.forEach(u => console.log(`    - Filter ID: ${u.investment_filter_id}, Active: ${u.is_active}`));

                if (universes.length > 0) {
                    // Check filters
                    const filterIds = universes.map(u => u.investment_filter_id);
                    const { data: filters, error: filtError } = await supabase
                        .from('kw_investment_filters')
                        .select('id, name, is_active, filtered_stocks_count, filtered_stocks')
                        .in('id', filterIds);

                    if (filtError) console.error('  Error fetching filters:', filtError);
                    else {
                        filters.forEach(f => {
                            let stockCount = 0;
                            if (f.filtered_stocks) {
                                if (Array.isArray(f.filtered_stocks)) stockCount = f.filtered_stocks.length;
                                else if (typeof f.filtered_stocks === 'object') stockCount = Object.keys(f.filtered_stocks).length;
                            }
                            console.log(`    - Filter: ${f.name}, Active: ${f.is_active}, CountCol: ${f.filtered_stocks_count}, JSONCount: ${stockCount}`);
                            if (stockCount === 0) console.log('      WARNING: filtered_stocks JSON is empty!');
                        });
                    }
                }
            }
        }
    }

    // 2. Check strategy_monitoring count
    const { count, error: countError } = await supabase
        .from('strategy_monitoring')
        .select('*', { count: 'exact', head: true });

    console.log(`Total records in strategy_monitoring: ${count}`);
}

checkData();
