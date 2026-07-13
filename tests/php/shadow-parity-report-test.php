<?php
/**
 * Read-only shadow parity report contract tests.
 *
 * @package CEFA_Conversion_Tracking
 */

define( 'ABSPATH', __DIR__ . '/' );
define( 'WP_CLI', false );

if ( ! function_exists( 'sanitize_text_field' ) ) {
	function sanitize_text_field( $value ) {
		return trim( strip_tags( (string) $value ) );
	}
}

require_once dirname( __DIR__, 2 ) . '/tools/wp-shadow-parity-report.php';

function cefa_shadow_report_assert( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message );
	}
}

cefa_shadow_report_assert(
	'match' === cefa_ct_shadow_core_comparison( 'utm_source', 'Google', 'google' ),
	'Source comparison is not case-normalized.'
);
cefa_shadow_report_assert(
	'match' === cefa_ct_shadow_core_comparison( 'utm_medium', 'CPC', 'cpc' ),
	'Medium comparison is not case-normalized.'
);
cefa_shadow_report_assert(
	'skip' === cefa_ct_shadow_core_comparison( 'first_landing_page', 'https://cefa.ca/old', 'https://cefa.ca/new' ),
	'First-context deployment-window difference was not excluded.'
);
cefa_shadow_report_assert(
	'skip' === cefa_ct_shadow_core_comparison( 'gbraid', 'stale-braid', '' ),
	'Stale legacy click-family value was not excluded.'
);
cefa_shadow_report_assert(
	'match' === cefa_ct_shadow_core_comparison( 'gclid', 'current-click', 'current-click' ),
	'Current canonical click ID did not match.'
);
cefa_shadow_report_assert(
	'mismatch' === cefa_ct_shadow_core_comparison( 'utm_campaign', 'legacy-campaign', 'canonical-campaign' ),
	'Comparable campaign mismatch was not reported.'
);
cefa_shadow_report_assert(
	'match' === cefa_ct_writeback_policy_comparison( 'utm_source', 'Google', 'google' ),
	'Writeback source comparison is not case-normalized.'
);
cefa_shadow_report_assert(
	'match' === cefa_ct_writeback_policy_comparison( 'fbclid', '', '' ),
	'Cleared competing click ID did not match writeback policy.'
);
cefa_shadow_report_assert(
	'mismatch' === cefa_ct_writeback_policy_comparison( 'gclid', 'historical-click', '' ),
	'Historical click ID was not rejected by writeback policy.'
);
cefa_shadow_report_assert(
	'skip' === cefa_ct_writeback_policy_comparison( 'first_referrer', 'https://legacy.example/', '' ),
	'Missing canonical first-touch context did not preserve the saved value.'
);

echo "Shadow parity report tests passed.\n";
