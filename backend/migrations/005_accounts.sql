-- Customer current-account improvements.
-- Run after 004_market_sales.sql.
-- No new tables are required: account_transactions is the ledger.

ALTER TABLE account_transactions
  ADD INDEX idx_account_transactions_customer_type_created (customer_id, transaction_type, created_at);

-- Transaction semantics used by the application:
-- debit   = customer debt created by a sale/service
-- payment = payment received from customer (reduces debt)
-- credit  = future credit/discount/return adjustment (reduces debt)
