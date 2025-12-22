import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

def verify_priority():
    print("=== Verifying Candidate Priority ===")
    
    # Call RPC with min_score 0 to get all potential candidates
    print("Fetching candidates...")
    rpc = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
    
    candidates = rpc.data if rpc.data else []
    count = len(candidates)
    print(f"Total Candidates: {count}")
    
    if count == 0:
        print("⚠️ No candidates found. Cannot verify sort order.")
        return

    # Check Sort Order
    scores = [float(c['condition_match_score']) for c in candidates]
    is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
    
    print("\nTop 5 Candidates:")
    for i, c in enumerate(candidates[:5]):
        print(f"  {i+1}. {c['stock_name']} ({c['stock_code']}) - Score: {c['condition_match_score']}")
        
    if is_sorted:
        print("\n✅ PASSED: Candidates are sorted by score (Descending).")
    else:
        print("\n❌ FAILED: Candidates are NOT sorted correctly!")
        print(f"Scores: {scores[:10]}...")

if __name__ == "__main__":
    verify_priority()
