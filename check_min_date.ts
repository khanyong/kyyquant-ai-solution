
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

const supabaseUrl = process.env.VITE_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing Supabase URL or Key in .env file');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkMinDate() {
    console.log('Checking minimum trade_date in kw_price_daily...');

    const { data, error } = await supabase
        .from('kw_price_daily')
        .select('trade_date')
        .order('trade_date', { ascending: true })
        .limit(1);

    if (error) {
        console.error('Error fetching data:', error);
    } else {
        if (data && data.length > 0) {
            console.log('Minimum trade_date:', data[0].trade_date);
        } else {
            console.log('No data found in kw_price_daily');
        }
    }
}

checkMinDate();
