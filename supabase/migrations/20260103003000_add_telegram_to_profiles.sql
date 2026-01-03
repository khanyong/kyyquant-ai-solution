
-- Add Telegram Chat ID and Notification Settings to profiles
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS telegram_chat_id TEXT,
ADD COLUMN IF NOT EXISTS notification_settings JSONB DEFAULT '{"telegram": true, "email": false}'::jsonb;

-- Comment
COMMENT ON COLUMN profiles.telegram_chat_id IS 'Telegram Chat ID for notifications';
