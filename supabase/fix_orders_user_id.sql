-- Make user_id nullable in orders table
-- n8n 워크플로우에서는 user_id 없이 자동 매매 주문을 생성하므로 nullable로 변경

ALTER TABLE public.orders
ALTER COLUMN user_id DROP NOT NULL;

-- Add comment
COMMENT ON COLUMN public.orders.user_id IS '사용자 ID (자동 매매의 경우 NULL 가능)';
