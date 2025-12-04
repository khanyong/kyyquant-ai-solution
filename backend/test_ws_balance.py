"""
Test Kiwoom WebSocket Balance
Connects to WebSocket, registers for balance, and listens for 10 seconds.
"""
import asyncio
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from api.kiwoom_websocket import get_websocket_client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logging.getLogger('websockets').setLevel(logging.INFO)  # Keep websockets noisy logs down
logger = logging.getLogger(__name__)

async def test_ws_balance():
    print("=" * 80)
    print("🧪 Testing Kiwoom WebSocket Balance")
    print("=" * 80)

    load_dotenv()

    async def on_balance_update(data):
        print(f"\n[CALLBACK] Received Balance Data:")
        print(f"  - Account: {data.get('account_number')}")
        print(f"  - Stock: {data.get('stock_name')} ({data.get('stock_code')})")
        print(f"  - Quantity: {data.get('quantity')}")
        print(f"  - Current Price: {data.get('current_price')}")
        print(f"  - Profit/Loss: {data.get('profit_loss_rate')}%")

    client = get_websocket_client(on_balance_update=on_balance_update)
    
    try:
        # Connect and Register
        await client.connect()
        
        print("\n⏳ Listening for 10 seconds...")
        
        # Listen for a short period
        # We need to run client.listen() but it's an infinite loop.
        # We'll run it in a task and cancel it.
        listen_task = asyncio.create_task(client.listen())
        
        await asyncio.sleep(10)
        
        print("\n🛑 Stopping listener...")
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\n✅ Test Finished")

if __name__ == "__main__":
    asyncio.run(test_ws_balance())
