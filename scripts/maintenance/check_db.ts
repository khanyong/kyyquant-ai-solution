
import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'
import path from 'path'

dotenv.config({ path: path.resolve(__dirname, '.env') })

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing Supabase credentials')
    process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseKey)

async function checkData() {
    console.log('Checking active strategies...')
    const { data: strategies, error: strategyError } = await supabase
        .from('strategies')
        .select('*')
        .eq('is_active', true)

    if (strategyError) {
        console.error('Error fetching strategies:', strategyError)
    } else {
        console.log(`Found ${strategies.length} active strategies:`)
        strategies.forEach(s => console.log(`- [${s.id}] ${s.name} (Auto: ${s.auto_trade_enabled})`))
    }

    console.log('\nChecking strategy universes...')
    const { data: universes, error: universeError } = await supabase
        .from('strategy_universes')
        .select('*')
        .eq('is_active', true)

    if (universeError) {
        console.error('Error fetching universes:', universeError)
    } else {
        console.log(`Found ${universes.length} active universes:`)
        universes.forEach(u => console.log(`- Strategy: ${u.strategy_id}, Filter: ${u.filter_id}`))
    }

    console.log('\nTesting RPC get_active_strategies_with_universe...')
    const { data: rpcData, error: rpcError } = await supabase
        .rpc('get_active_strategies_with_universe')

    if (rpcError) {
        console.error('Error calling RPC:', rpcError)
    } else {
        console.log(`RPC returned ${rpcData ? rpcData.length : 0} rows`)
        if (rpcData && rpcData.length > 0) {
            console.log('Sample row:', rpcData[0])
        }
    }
}

checkData()
