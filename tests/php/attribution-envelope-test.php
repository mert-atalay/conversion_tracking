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

$identified = CEFA_Conversion_Tracking_Attribution_Envelope::with_browser_ids(
	$braid,
	array(
		'_ga'          => 'GA1.1.123456789.987654321',
		'_ga_TEST'     => 'GS2.1.s1783641600$o3$g1$t1783641700$j60$l0$h0',
		'_fbp'         => 'fb.1.1783641600.123456789',
		'_fbc'         => 'fb.1.1783641600.testFbclid_123',
		'email_cookie' => 'must-not-save@example.com',
	)
);
cefa_assert( '123456789.987654321' === $identified['browser_ids']['ga_client_id'], 'GA client ID parsing failed.' );
cefa_assert( '1783641600' === $identified['browser_ids']['ga_session_id'], 'GA session ID parsing failed.' );
cefa_assert( 'fb.1.1783641600.123456789' === $identified['browser_ids']['fbp'], 'FBP parsing failed.' );
cefa_assert( 'fb.1.1783641600.testFbclid_123' === $identified['browser_ids']['fbc'], 'FBC parsing failed.' );
cefa_assert( ! isset( $identified['browser_ids']['email_cookie'] ), 'Unapproved browser cookie was retained.' );

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

/**
 * Minimal configuration substitute for entry persistence tests.
 */
final class CEFA_Conversion_Tracking_Config {
	public static $mode = 'shadow';

	public static function attribution_v2_mode() {
		return self::$mode;
	}

	public static function attribution_v2_secret() {
		return 'entry-test-secret';
	}

	public static function site_context() {
		return 'parent';
	}

	public static function attribution_cookie_name() {
		return 'cefa_parent_attr_v1';
	}
}

if ( ! function_exists( 'sanitize_text_field' ) ) {
	function sanitize_text_field( $value ) {
		return trim( strip_tags( (string) $value ) );
	}
}

if ( ! function_exists( 'wp_unslash' ) ) {
	function wp_unslash( $value ) {
		return $value;
	}
}

if ( ! function_exists( 'rgar' ) ) {
	function rgar( $array, $key ) {
		return is_array( $array ) && array_key_exists( $key, $array ) ? $array[ $key ] : null;
	}
}

$GLOBALS['cefa_test_meta']         = array();
$GLOBALS['cefa_test_meta_updates'] = 0;

if ( ! function_exists( 'gform_update_meta' ) ) {
	function gform_update_meta( $entry_id, $meta_key, $value, $form_id = 0 ) {
		unset( $form_id );
		$GLOBALS['cefa_test_meta'][ $entry_id ][ $meta_key ] = $value;
		++$GLOBALS['cefa_test_meta_updates'];
	}
}

if ( ! function_exists( 'gform_get_meta' ) ) {
	function gform_get_meta( $entry_id, $meta_key ) {
		return $GLOBALS['cefa_test_meta'][ $entry_id ][ $meta_key ] ?? '';
	}
}

require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-entry-attribution.php';

$entry_now      = time();
$entry_envelope = CEFA_Conversion_Tracking_Attribution_Envelope::capture( $query, $server, 'parent', array(), $entry_now );
$_COOKIE['cefa_parent_attr_v1'] = CEFA_Conversion_Tracking_Attribution_Envelope::encode( $entry_envelope, 'entry-test-secret' );
$entry = array(
	'id'      => 101,
	'form_id' => 4,
	'status'  => 'active',
	'35'      => 'legacy-google',
);
$saved = CEFA_Conversion_Tracking_Entry_Attribution::persist_after_submission( $entry, array( 'id' => 4 ) );
cefa_assert( 'legacy-google' === $saved['35'], 'Shadow persistence changed a legacy field.' );
cefa_assert( isset( $GLOBALS['cefa_test_meta'][101][ CEFA_Conversion_Tracking_Entry_Attribution::ATTRIBUTION_META_KEY ] ), 'Canonical entry attribution was not saved.' );
cefa_assert( 'attribution_shadow' === $GLOBALS['cefa_test_meta'][101][ CEFA_Conversion_Tracking_Entry_Attribution::STATUS_META_KEY ], 'Shadow status was not saved.' );
cefa_assert( $entry_envelope === CEFA_Conversion_Tracking_Entry_Attribution::from_entry( $saved ), 'Saved entry attribution round trip failed.' );

$updates = $GLOBALS['cefa_test_meta_updates'];
CEFA_Conversion_Tracking_Entry_Attribution::persist_after_submission( $saved, array( 'id' => 4 ) );
cefa_assert( $updates === $GLOBALS['cefa_test_meta_updates'], 'Repeated persistence was not idempotent.' );

CEFA_Conversion_Tracking_Config::$mode = 'off';
CEFA_Conversion_Tracking_Entry_Attribution::persist_after_submission( array( 'id' => 102, 'form_id' => 4 ), array( 'id' => 4 ) );
cefa_assert( ! isset( $GLOBALS['cefa_test_meta'][102] ), 'Off mode wrote entry attribution.' );

echo "Attribution envelope and entry tests passed.\n";
