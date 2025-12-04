-- Check strategies data to find max_positions
SELECT id, name, config, position_size, allocated_capital, allocated_percent
FROM strategies
LIMIT 1;
