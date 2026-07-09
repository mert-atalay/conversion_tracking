<?php
/**
 * Focused Attribution Bridge envelope contract tests.
 *
 * @package CEFA_Conversion_Tracking
 */

define( 'ABSPATH', __DIR__ . '/' );

if ( ! function_exists( 'wp_json_encode' ) ) {
	/**
	 * Minimal WordPress JSON helper for isolated contract tests.
	 *
	 * @param mixed $value Value.
	 * @param int   $flags JSON flags.
	 * @return string|false
	 */
	function wp_json_encode( $value, $flags = 0 ) {
		return json_encode( $value, $flags ); // phpcs:ignore WordPress.WP.AlternativeFunctions.json_encode_json_encode -- This function is the isolated test substitute.
	}
}

if ( ! function_exists( 'wp_parse_url' ) ) {
	/**
	 * Minimal WordPress URL helper for isolated contract tests.
	 *
	 * @param string $url       URL.
	 * @param int    $component URL component.
	 * @return mixed
	 */
	function wp_parse_url( $url, $component = -1 ) {
		return parse_url( $url, $component ); // phpcs:ignore WordPress.WP.AlternativeFunctions.parse_url_parse_url -- This function is the isolated test substitute.
	}
}

require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-attribution-envelope.php';

/**
 * Fail an isolated contract test.
 *
 * @param bool   $condition Assertion result.
 * @param string $message   Failure message.
 * @return void
 * @throws RuntimeException When the assertion fails.
 */
function cefa_assert( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message ); // phpcs:ignore WordPress.Security.EscapeOutput.ExceptionNotEscaped -- CLI-only contract test.
	}
}

$now    = 1783641600;
$server = array(
	'HTTP_HOST'    => 'cefa.ca',
	'REQUEST_URI'  => '/?ignored=pii',
	'HTTP_REFERER' => 'https://www.google.com/search?q=private',
);
$query  = array(
	'utm_source'        => 'GOOGLE',
	'utm_medium'        => 'CPC',
	'utm_campaign'      => '14995905347',
	'utm_id'            => '14995905347',
	'utm_content'       => '623792611812',
	'utm_term'          => 'cefa',
	'gclid'             => 'test-gclid',
	'google_adgroup_id' => '134287144491',
	'email'             => 'must-not-save@example.com',
);

$envelope = CEFA_Conversion_Tracking_Attribution_Envelope::capture( $query, $server, 'parent', array(), $now );
cefa_assert( 'google' === $envelope['first_touch']['source'], 'Google source classification failed.' );
cefa_assert( 'cpc' === $envelope['first_touch']['medium'], 'Google medium classification failed.' );
cefa_assert( '14995905347' === $envelope['first_touch']['campaign_id'], 'Campaign ID was not captured.' );
cefa_assert( '/' === $envelope['first_touch']['landing_path'], 'Landing query string leaked into the path.' );
cefa_assert( ! isset( $envelope['email'] ), 'Unapproved query key was retained.' );
cefa_assert( 'test-gclid' === $envelope['click_ids']['gclid'], 'GCLID was not retained in the restricted object.' );

$token   = CEFA_Conversion_Tracking_Attribution_Envelope::encode( $envelope, 'test-secret' );
$decoded = CEFA_Conversion_Tracking_Attribution_Envelope::decode( $token, 'test-secret', 'parent', $now );
cefa_assert( $decoded === $envelope, 'Signed envelope round trip failed.' );
cefa_assert( array() === CEFA_Conversion_Tracking_Attribution_Envelope::decode( $token . 'x', 'test-secret', 'parent', $now ), 'Tampered token was accepted.' );
cefa_assert( array() === CEFA_Conversion_Tracking_Attribution_Envelope::decode( $token, 'test-secret', 'franchise_us', $now ), 'Cross-context token was accepted.' );
cefa_assert( array() === CEFA_Conversion_Tracking_Attribution_Envelope::decode( $token, 'test-secret', 'parent', $now + 7776001 ), 'Expired token was accepted.' );

$direct = CEFA_Conversion_Tracking_Attribution_Envelope::capture(
	array(),
	array(
		'HTTP_HOST'    => 'cefa.ca',
		'REQUEST_URI'  => '/find-a-school/',
		'HTTP_REFERER' => 'https://cefa.ca/',
	),
	'parent',
	$envelope,
	$now + 60
);
cefa_assert( $direct === $envelope, 'Internal/direct navigation overwrote attribution.' );

$braid = CEFA_Conversion_Tracking_Attribution_Envelope::capture(
	array( 'gbraid' => 'new-gbraid' ),
	array(
		'HTTP_HOST'   => 'cefa.ca',
		'REQUEST_URI' => '/find-a-school/',
	),
	'parent',
	$envelope,
	$now + 120
);
cefa_assert( ! isset( $braid['click_ids']['gclid'] ) && 'new-gbraid' === $braid['click_ids']['gbraid'], 'Google click-ID family replacement failed.' );

$agency = CEFA_Conversion_Tracking_Attribution_Envelope::capture(
	array(
		'utm_source'       => 'meta',
		'utm_medium'       => 'paid_social',
		'cefa_agency_test' => 'in_house',
	),
	array(
		'HTTP_HOST'   => 'www.franchisecefa.com',
		'REQUEST_URI' => '/',
	),
	'franchise_us',
	array(),
	$now
);
cefa_assert( 'fr_us_in_house' === $agency['experiment']['agency_test'], 'Approved in-house marker normalization failed.' );

echo "Attribution envelope tests passed.\n";
