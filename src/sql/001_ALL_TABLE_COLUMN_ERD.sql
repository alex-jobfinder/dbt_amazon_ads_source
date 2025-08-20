-- database: /home/alex/dbt_ads/z_dbt_ads_perf/final_DDL/sp_v3.db
-- begin
;

-- database: /home/alex/dbt_ads/z_dbt_ads_perf/final_DDL/sp_v3.db
begin;


drop table if exists schema_metadata; 
drop table if exists docs_table; 


-- Metadata table to describe schema
CREATE TABLE schema_metadata (
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    data_type TEXT,
    is_primary_key BOOLEAN DEFAULT 0,
    is_foreign_key BOOLEAN DEFAULT 0,
    references_table TEXT,
    references_column TEXT
);


CREATE TABLE IF NOT EXISTS docs_table (
    column_name TEXT PRIMARY KEY,
    column_description TEXT NOT NULL
);

INSERT OR REPLACE INTO docs_table (column_name, column_description) VALUES
('_fivetran_deleted', 'Boolean created by Fivetran to indicate whether the record has been deleted.'),
('_fivetran_id', 'Unique ID used by Fivetran to sync and dedupe data.'),
('_fivetran_synced', 'Timestamp of when a record was last synced.'),
('account_id', 'Identifier for sellers and vendors. Note that this value is not unique and may be the same across marketplaces.'),
('account_name', 'Account Name. Not currently populated for sellers.'),
('ad_group_id', 'The ID of the AdGroup.'),
('ad_group_name', 'The name of the AdGroup.'),
('ad_id', 'The ID of the Ad.'),
('ad_keyword_status', 'Current status of a keyword.'),
('advertised_asin', 'The ASIN associated to an advertised product.'),
('advertised_sku', 'The SKU being advertised.'),
('bid_keyword', 'Bid associated with this keyword.'),
('campaign_applicable_budget_rule_id', 'The ID associated to the active budget rule for a campaign.'),
('campaign_applicable_budget_rule_name', 'The name associated to the active budget rule for a campaign.'),
('campaign_bidding_strategy', 'The bidding strategy associated with a campaign.'),
('campaign_budget_amount', 'Total budget allocated to the campaign.'),
('campaign_budget_currency_code', 'The currency code associated with the campaign.'),
('campaign_budget_type', 'One of: daily or lifetime.'),
('campaign_id', 'The ID of the Campaign.'),
('campaign_name', 'The name of the Campaign.'),
('campaign_rule_based_budget_amount', 'The value of the rule-based budget for a campaign.'),
('clicks', 'Total number of ad clicks.'),
('cost', 'Total cost of ad clicks.'),
('country_code', 'The code for a given country.'),
('creation_date', 'The date of creation of the record.'),
('currency_code', 'The currency used for all monetary values for entities under this profile.'),
('default_bid', 'The default bid associated to the ad group.'),
('impressions', 'Total number of ad impressions.'),
('is_most_recent_record', 'Boolean indicating whether record was the most recent instance.'),
('keyword_bid', 'Bid associated with a keyword or targeting expression.'),
('keyword_id', 'The ID of the keyword.'),
('keyword_match_type', 'One of: BROAD, EXACT, or PHRASE.'),
('keyword_type', 'Type of matching for the keyword used in bid. One of: BROAD, PHRASE, or EXACT.'),
('last_updated_date', 'Date of last update to record.'),
('match_type', 'Type of matching for the keyword used in bid. One of: BROAD, PHRASE, or EXACT.'),
('negative_keyword_id', 'The ID of the negative keyword.'),
('portfolio_id', 'The ID of the Portfolio.'),
('portfolio_name', 'The name of the Portfolio.'),
('profile_id', 'The profile ID associated with your Amazon Ads account. Advertisers who operate in more than one marketplace will have one profile associated with each marketplace.'),
('report_date', 'The date of the report.'),
('search_term', 'The search term used by the customer.'),
('serving_status', 'The current serving status of the record.'),
('state', 'The state of the record (enabled, paused, or archived).'),
('targeting', 'A string representation of the expression object used in the targeting clause.'),
('source_relation', 'The source of the record if the unioning functionality is being used. If not this field will be empty.'),
('purchases_30_d', 'Number of attributed conversion events occurring within 30 days of an ad click.'),
('sales_30_d', 'Total value of sales occurring within 30 days of an ad click.');



INSERT INTO schema_metadata VALUES ('PROFILE', '_fivetran_id',                  'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'profile_id',                    'INTEGER', 0, 1,    'PROFILE',          'profile_id');
INSERT INTO schema_metadata VALUES ('PROFILE', 'asin',                          'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'estimated_impression_lower',    'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'estimated_impression_upper',    'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'strategy',                      'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'targeting_type',                'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'theme',                         'TEXT',    0, 0,    NULL,               NULL);




INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'id',                   'INTEGER', 1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'last_updated_date',    'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'ad_group_id',          'INTEGER', 0, 1, 'AD_GROUP_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'campaign_id',          'INTEGER', 0, 1, 'CAMPAIGN_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'bid',                  'REAL',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'creation_date',        'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'keyword_text',         'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'match_type',           'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'native_language_keyword','TEXT',  0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'native_language_locale','TEXT',   0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'serving_status',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'state',                'TEXT',    0, 0, NULL,               NULL);


INSERT INTO schema_metadata VALUES ('PRODUCT_AD_HISTORY',        'name',                 'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_HISTORY',        'product_ad_id',        'INTEGER', 1, 1, 'PRODUCT_AD_HISTORY','product_ad_id');
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_HISTORY',        'help_url',             'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_HISTORY',        'message',              'TEXT',    0, 0, NULL,               NULL);


INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'id',                   'INTEGER', 1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'last_updated_date',    'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'portfolio_id',         'INTEGER', 0, 1, 'PORTFOLIO_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'bidding_strategy',     'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'budget',               'REAL',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'effective_budget',     'REAL',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'budget_type',          'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'creation_date',        'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'end_date',             'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'name',                 'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'profile_id',           'INTEGER', 0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'serving_status',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'start_date',           'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'state',                'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'targeting_type',       'TEXT',    0, 0, NULL,               NULL);



INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'id',                   'INTEGER', 1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'last_updated_date',    'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'campaign_id',          'INTEGER', 0, 1, 'CAMPAIGN_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'ad_group_id',          'INTEGER', 0, 1, 'AD_GROUP_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'creation_date',        'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'keyword_text',         'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'match_type',           'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'native_language_keyword','TEXT',  0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'native_language_locale','TEXT',   0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'serving_status',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'state',                'TEXT',    0, 0, NULL,               NULL);



INSERT INTO schema_metadata VALUES ('PORTFOLIO_HISTORY', 'date',        'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PORTFOLIO_HISTORY', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('PORTFOLIO_HISTORY', '_metrics',    'TEXT',    0, 0,    NULL,               NULL);





INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_HISTORY', 'name',      'TEXT',    1, 0,    NULL,                        NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_HISTORY', 'target_id','INTEGER', 1, 1,    'TARGETING_CLAUSE_HISTORY','target_id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_HISTORY', 'help_url', 'TEXT',    0, 0,    NULL,                        NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_HISTORY', 'level',    'TEXT',    0, 0,    NULL,                        NULL);


INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_HISTORY', 'name',                 'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_HISTORY', 'keyword_id',           'INTEGER', 1, 1, 'KEYWORD_HISTORY',   'id');
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_HISTORY', 'help_url',             'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_HISTORY', 'message',              'TEXT',    0, 0, NULL,               NULL);

INSERT INTO schema_metadata VALUES ('TARGETING_CLAUSE_HISTORY', '_fivetran_id',        'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_CLAUSE_HISTORY', 'target_id',           'INTEGER', 0, 1, 'TARGETING_CLAUSE_HISTORY','target_id');
INSERT INTO schema_metadata VALUES ('TARGETING_CLAUSE_HISTORY', 'type',                'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_CLAUSE_HISTORY', 'value',               'TEXT',    0, 0, NULL,               NULL);


INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'id',                                 'INTEGER', 1, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'budget_increase_by_type',           'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'budget_increase_by_value',          'REAL',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'created_date',                      'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'date_range_type_duration_end_date',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'date_range_type_duration_start_date', 'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'event_type_rule_duration_end_date',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'event_type_rule_duration_event_id',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'event_type_rule_duration_event_name', 'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'event_type_rule_duration_start_date', 'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'last_updated_date',                  'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'name',                              'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'preformance_measure_comparison_operator', 'TEXT', 0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'preformance_measure_metric_name',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'preformance_measure_treshold',      'REAL',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'recurrence_type',                   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'state',                             'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'status',                            'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'type',                              'TEXT',    0, 0, NULL, NULL);














INSERT INTO schema_metadata VALUES ('CAMPAIGN_LEVEL_REPORT', 'date',      'TEXT',    1, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_LEVEL_REPORT', 'placement', 'TEXT',    1, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_LEVEL_REPORT', '_metrics',  'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', 'date',       'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', 'ad_group_id','INTEGER', 1, 1, 'AD_GROUP_HISTORY',   'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', 'campaign_id','INTEGER', 1, 1, 'CAMPAIGN_HISTORY',   'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', 'keyword_id','INTEGER',  1, 1, 'KEYWORD_HISTORY',    'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', '_metrics',   'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'date',       'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'search_term','TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'ad_group_id','INTEGER', 1, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'keyword_id','INTEGER',  1, 1,    'KEYWORD_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', '_metrics',   'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_AD_KEYWORD_REPORT', 'date',       'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_AD_KEYWORD_REPORT', 'ad_group_id','INTEGER', 1, 1, 'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_AD_KEYWORD_REPORT', '_metrics',   'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', 'date',        'TEXT',    1, 0, NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', 'ad_id',       'INTEGER', 1, 1, 'PRODUCT_AD_HISTORY',         'product_ad_id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', 'ad_group_id', 'INTEGER', 1, 1, 'AD_GROUP_HISTORY',           'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', 'campaign_id', 'INTEGER', 1, 1, 'CAMPAIGN_HISTORY',           'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', '_metrics',    'TEXT',    0, 0, NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'date',         'TEXT',    1, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'purchased_asin','TEXT',    1, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'ad_group_id',   'INTEGER', 1, 1, 'AD_GROUP_HISTORY','id');
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'campaign_id',   'INTEGER', 1, 1, 'CAMPAIGN_HISTORY','id');
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'keyword_id',    'INTEGER', 1, 1, 'KEYWORD_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', '_metrics',      'TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', 'date',        'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', 'search_term','TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', 'ad_group_id','INTEGER', 1, 1, 'AD_GROUP_HISTORY','id');
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', 'campaign_id','INTEGER', 1, 1, 'CAMPAIGN_HISTORY','id');
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', '_metrics',   'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', 'date',       'TEXT',    1, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', 'ad_group_id','INTEGER', 1, 1,    'AD_GROUP_HISTORY',           'id');
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY',           'id');
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', 'keyword_id','INTEGER', 1, 1,    'TARGETING_EXPRESSION',       'target_id');
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', '_metrics',  'TEXT',    0, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'date',          'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'purchased_asin','TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'ad_group_id',   'INTEGER', 1, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'campaign_id',   'INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'keyword_id',    'INTEGER', 1, 1,    'KEYWORD_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', '_metrics',      'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_TARGETING_REPORT', 'name',        'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_TARGETING_REPORT', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_TARGETING_REPORT', 'help_url',    'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_TARGETING_REPORT', 'message',     'TEXT',    0, 0,    NULL,               NULL);







INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', '_fivetran_id', 'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'campaign_id', 'INTEGER', 0, 1, 'CAMPAIGN_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'ad_group_id', 'INTEGER', 0, 1, 'AD_GROUP_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'keyword_text','TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'match_type',  'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'state',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_SUGGESTED_KEYWORD', '_fivetran_id','TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_SUGGESTED_KEYWORD', 'asin',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_SUGGESTED_KEYWORD', 'keyword_text','TEXT',   0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_SUGGESTED_KEYWORD', 'match_type', 'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'ad_id',               'INTEGER', 1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'last_updated_date',    'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'ad_group_id',          'INTEGER', 0, 1, 'AD_GROUP_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'campaign_id',          'INTEGER', 0, 1, 'CAMPAIGN_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'asin',                 'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'creation_date',        'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'custom_text',          'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'sku',                  'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'serving_status',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_SUGGESTED_KEYWORD',    'state',                'TEXT',    0, 0, NULL,               NULL);




INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'target_id',         'INTEGER', 1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'last_updated_date','TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'ad_group_id',      'INTEGER', 0, 1, 'AD_GROUP_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'campaign_id',      'INTEGER', 0, 1, 'CAMPAIGN_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'bid',              'REAL',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'creation_date',    'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'expression_type',  'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'serving_status',   'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_SERVING_STATUS_DETAIL', 'state',            'TEXT',    0, 0, NULL,               NULL);

INSERT INTO schema_metadata VALUES ('BUDGET_RULE', 'campaign_id', 'INTEGER', 1, 1, 'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('BUDGET_RULE', 'rule_id',     'INTEGER', 1, 1, 'BUDGET_RULE',     'rule_id');
INSERT INTO schema_metadata VALUES ('BUDGET_RULE_CAMPAIGN', 'day_of_week', 'TEXT',    1, 0, NULL,           NULL);
INSERT INTO schema_metadata VALUES ('BUDGET_RULE_CAMPAIGN', 'rule_id',     'INTEGER', 1, 1, 'BUDGET_RULE',   'rule_id');
INSERT INTO schema_metadata VALUES ('BUDGET_RULE_RECURRENCE_DAY', '_fivetran_id','TEXT',    1, 0, NULL,                                   NULL);
INSERT INTO schema_metadata VALUES ('BUDGET_RULE_RECURRENCE_DAY', 'target_id',   'INTEGER', 0, 1, 'NEGATIVE_TARGETING_CLAUSE_HISTORY','id');
INSERT INTO schema_metadata VALUES ('BUDGET_RULE_RECURRENCE_DAY', 'type',        'TEXT',    0, 0, NULL,                                   NULL);
INSERT INTO schema_metadata VALUES ('BUDGET_RULE_RECURRENCE_DAY', 'value',       'TEXT',    0, 0, NULL,                                   NULL);

















INSERT INTO schema_metadata VALUES ('CAMPAIGN_SERVING_STATUS_DETAIL', 'placement',  'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_SERVING_STATUS_DETAIL', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_SERVING_STATUS_DETAIL', 'percentage', 'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_BIDDING', 'name',        'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_BIDDING', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_BIDDING', 'value',       'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_TAG', 'name',        'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_TAG', 'ad_group_id','INTEGER', 1, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_TAG', 'help_url',    'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_TAG', 'message',     'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_SERVING_STATUS_DETAIL', 'name',       'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_SERVING_STATUS_DETAIL', 'keyword_id','INTEGER', 1, 1,    'KEYWORD_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_SERVING_STATUS_DETAIL', 'help_url',   'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_SERVING_STATUS_DETAIL', 'message',    'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_SERVING_STATUS_DETAIL', 'name',       'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_SERVING_STATUS_DETAIL', 'keyword_id','INTEGER', 1, 1,    'KEYWORD_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('KEYWORD_SERVING_STATUS_DETAIL', 'help_url',   'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_SERVING_STATUS_DETAIL', 'message',    'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'id',               'INTEGER', 1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'last_updated_date','TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'campaign_id',      'INTEGER', 0, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'creation_date',    'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'keyword_text',     'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'match_type',       'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'serving_status',   'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_SERVING_STATUS_DETAIL', 'state',            'TEXT',    0, 0,    NULL,               NULL);




INSERT INTO schema_metadata VALUES ('TARGETING_SERVING_STATUS_DETAIL', 'name',       'TEXT',    1, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_SERVING_STATUS_DETAIL', 'target_id',  'INTEGER', 1, 1,    'TARGETING_CLAUSE_HISTORY',  'target_id');
INSERT INTO schema_metadata VALUES ('TARGETING_SERVING_STATUS_DETAIL', 'help_url',   'TEXT',    0, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_SERVING_STATUS_DETAIL', 'level',      'TEXT',    0, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'id',                              'INTEGER', 1, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'account_id',                      'INTEGER', 0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'account_marketplace_string_id',  'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'account_name',                    'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'account_sub_type',                'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'account_type',                    'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'account_valid_payment_method',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'currency_code',                   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'country_code',                    'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'daily_budget',                    'REAL',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_SERVING_STATUS_DETAIL', 'timezone',                        'TEXT',    0, 0, NULL, NULL);

INSERT INTO schema_metadata VALUES ('ASIN_THEME_BASED_BID_RECOMMENDATION', 'parent_id',   'INTEGER', 1, 1, 'ASIN_THEME_BASED_BID_RECOMMENDATION', 'parent_id');
INSERT INTO schema_metadata VALUES ('ASIN_THEME_BASED_BID_RECOMMENDATION', 'index',       'INTEGER', 1, 0, NULL,                                    NULL);
INSERT INTO schema_metadata VALUES ('ASIN_THEME_BASED_BID_RECOMMENDATION', 'suggested_bid','REAL',    0, 0, NULL,                                    NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', '_fivetran_id',                 'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'profile_id',                   'INTEGER', 0, 1,    'PROFILE',          'profile_id');
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'asin',                         'TEXT',    0, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'bid',                          'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'estimated_impression_avg',     'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'estimated_impression_lower',   'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'estimated_impression_upper',   'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'placement',                    'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'strategy',                     'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'targeting_type',               'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'theme',                        'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_RECOMMENDATION_VALUE', 'type_of_bid',                  'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_ANALYSIS', '_fivetran_id',                 'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_ANALYSIS', 'ad_group_id',                  'INTEGER', 0, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('ASIN_BID_ANALYSIS', 'campaign_id',                  'INTEGER', 0, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('ASIN_BID_ANALYSIS', 'profile_id',                   'INTEGER', 0, 1,    'PROFILE',          'profile_id');
INSERT INTO schema_metadata VALUES ('ASIN_BID_ANALYSIS', 'estimated_impression_lower',   'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_ANALYSIS', 'estimated_impression_upper',   'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_ANALYSIS', 'targeting_type',               'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('ASIN_BID_ANALYSIS', 'theme',                        'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_THEME_BASED_BID_RECOMMENDATION', 'parent_id',   'INTEGER', 1, 1, 'AD_GROUP_THEME_BASED_BID_RECOMMENDATION', 'parent_id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_THEME_BASED_BID_RECOMMENDATION', 'index',       'INTEGER', 1, 0, NULL,                                    NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_THEME_BASED_BID_RECOMMENDATION', 'suggested_bid','REAL',    0, 0, NULL,                                    NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', '_fivetran_id',                'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'ad_group_id',                 'INTEGER', 0, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'campaign_id',                 'INTEGER', 0, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'profile_id',                  'INTEGER', 0, 1,    'PROFILE',          'profile_id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'bid',                         'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'estimated_impression_avg',    'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'estimated_impression_lower',  'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'estimated_impression_upper',  'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'placement',                   'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'targeting_type',              'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'theme',                       'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_RECOMMENDATION_VALUE', 'type_of_bid',                 'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', '_fivetran_id',                 'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'ad_group_id',                  'INTEGER', 0, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'campaign_id',                  'INTEGER', 0, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'profile_id',                   'INTEGER', 0, 1,    'PROFILE',          'profile_id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'bid',                          'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'estimated_impression_avg',     'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'estimated_impression_lower',   'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'estimated_impression_upper',   'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'placement',                    'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'targeting_type',               'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'theme',                        'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_BID_ANALYSIS', 'type_of_bid',                  'TEXT',    0, 0,    NULL,               NULL);






INSERT INTO schema_metadata VALUES ('TARGETING_EXPRESSION', '_fivetran_id', 'TEXT',    1, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_EXPRESSION', 'target_id',    'INTEGER', 0, 1,    'TARGETING_CLAUSE_HISTORY',  'target_id');
INSERT INTO schema_metadata VALUES ('TARGETING_EXPRESSION', 'type',         'TEXT',    0, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_EXPRESSION', 'value',        'TEXT',    0, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_RESOLVED_EXPRESSION', 'target_id',           'INTEGER', 1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_RESOLVED_EXPRESSION', 'last_updated_date',   'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_RESOLVED_EXPRESSION', 'ad_group_id',         'INTEGER', 0, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_RESOLVED_EXPRESSION', 'campaign_id',         'INTEGER', 0, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_RESOLVED_EXPRESSION', 'creation_date',       'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_RESOLVED_EXPRESSION', 'expression_type',     'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_RESOLVED_EXPRESSION', 'serving_status',      'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_RESOLVED_EXPRESSION', 'state',               'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_EXPRESSION', '_fivetran_id','TEXT',    1, 0, NULL,                                   NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_EXPRESSION', 'target_id',   'INTEGER', 0, 1, 'NEGATIVE_TARGETING_CLAUSE_HISTORY','id');
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_EXPRESSION', 'type',        'TEXT',    0, 0, NULL,                                   NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_EXPRESSION', 'value',       'TEXT',    0, 0, NULL,                                   NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'id',               'INTEGER', 1, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'last_update_date', 'TEXT',    1, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'profile_id',       'INTEGER', 0, 1, 'PROFILE',        'profile_id');
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'budget_amount',    'REAL',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'budget_currency_code','TEXT', 0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'budget_end_date',  'TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'budget_policy',    'TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'budget_start_date','TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'creation_date',    'TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'in_budget',        'TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'name',             'TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'serving_status',   'TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_RESOLVED_EXPRESSION', 'state',            'TEXT',    0, 0, NULL,             NULL);


-- Add column to schema_metadata
ALTER TABLE schema_metadata 
ADD COLUMN column_description TEXT;

-- Update column_description with matching docs_table entries
UPDATE schema_metadata
SET column_description = (
    SELECT d.column_description
    FROM docs_table d
    WHERE d.column_name = schema_metadata.column_name
)
WHERE column_name IN (SELECT column_name FROM docs_table);


end;