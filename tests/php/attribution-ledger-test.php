<?php
/**
 * Focused server-side attribution ledger contract tests.
 *
 * @package CEFA_Conversion_Tracking
 */

define( 'ABSPATH', __DIR__ . '/' );

if ( ! function_exists( 'wp_json_encode' ) ) {
	function wp_json_encode( $value, $flags = 0 ) {
		return json_encode( $value, $flags ); // phpcs:ignore WordPress.WP.AlternativeFunctions.json_encode_json_encode -- Isolated test substitute.
	}
}

if ( ! function_exists( 'sanitize_key' ) ) {
	function sanitize_key( $value ) {
		return preg_replace( '/[^a-z0-9_\-]/', '', strtolower( (string) $value ) );
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

if ( ! function_exists( 'wp_generate_uuid4' ) ) {
	function wp_generate_uuid4() {
		return '123e4567-e89b-42d3-a456-426614174000';
	}
}

if ( ! function_exists( 'current_time' ) ) {
	function current_time( $type, $gmt = false ) {
		unset( $type, $gmt );
		return gmdate( 'Y-m-d H:i:s' );
	}
}

if ( ! function_exists( 'is_ssl' ) ) {
	function is_ssl() {
		return true;
	}
}

/**
 * Minimal guarded configuration substitute.
 */
final class CEFA_Conversion_Tracking_Config {
	public static function ledger_mode() {
		return 'shadow';
	}

	public static function ledger_secret() {
		return 'ledger-test-secret';
	}

	public static function site_context() {
		return 'parent';
	}

	public static function ledger_cookie_name() {
		return 'cefa_parent_capture_v2';
	}
}

/**
 * Prepared SQL value for the isolated wpdb substitute.
 */
final class CEFA_Ledger_Test_Prepared_SQL {
	public $query;
	public $args;

	public function __construct( $query, $args ) {
		$this->query = $query;
		$this->args  = $args;
	}
}

/**
 * Minimal wpdb substitute for ledger writes and reads.
 */
final class CEFA_Ledger_Test_WPDB {
	public $prefix = 'wp_';
	public $rows   = array();

	public function prepare( $query, ...$args ) {
		return new CEFA_Ledger_Test_Prepared_SQL( $query, $args );
	}

	public function query( $prepared ) {
		if ( false === strpos( $prepared->query, 'INSERT INTO' ) ) {
			return 0;
		}

		$this->rows[ $prepared->args[0] ] = array(
			'site_context' => $prepared->args[1],
			'envelope_json' => $prepared->args[2],
			'expires_at'    => $prepared->args[5],
		);

		return 1;
	}

	public function get_var( $prepared ) {
		$row = $this->rows[ $prepared->args[0] ] ?? null;

		if ( ! is_array( $row ) || $row['site_context'] !== $prepared->args[1] || $row['expires_at'] < $prepared->args[2] ) {
			return null;
		}

		return $row['envelope_json'];
	}
}

$GLOBALS['cefa_ledger_test_meta'] = array();

if ( ! function_exists( 'gform_update_meta' ) ) {
	function gform_update_meta( $entry_id, $meta_key, $value, $form_id = 0 ) {
		$GLOBALS['cefa_ledger_test_meta'][ $entry_id ][ $meta_key ] = array(
			'value'   => $value,
			'form_id' => $form_id,
		);
	}
}

require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-attribution-ledger.php';

/**
 * Fail one isolated assertion.
 *
 * @param bool   $condition Assertion result.
 * @param string $message   Failure message.
 * @return void
 * @throws RuntimeException When the assertion fails.
 */
function cefa_ledger_assert( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message ); // phpcs:ignore WordPress.Security.EscapeOutput.ExceptionNotEscaped -- CLI-only contract test.
	}
}

$capture_id = '123e4567-e89b-42d3-a456-426614174000';
$now        = 1783641600;
$token      = CEFA_Conversion_Tracking_Attribution_Ledger::issue_token(
	$capture_id,
	'form',
	'parent',
	1800,
	'ledger-test-secret',
	$now
);

cefa_ledger_assert( '' !== $token, 'Form fallback token was not issued.' );
cefa_ledger_assert(
	$capture_id === CEFA_Conversion_Tracking_Attribution_Ledger::verify_token( $token, 'form', 'parent', 'ledger-test-secret', $now )['capture_id'],
	'Signed form fallback did not round trip.'
);
cefa_ledger_assert( array() === CEFA_Conversion_Tracking_Attribution_Ledger::verify_token( $token . 'x', 'form', 'parent', 'ledger-test-secret', $now ), 'Tampered ledger token was accepted.' );
cefa_ledger_assert( array() === CEFA_Conversion_Tracking_Attribution_Ledger::verify_token( $token, 'cookie', 'parent', 'ledger-test-secret', $now ), 'Form token was accepted as a cookie token.' );
cefa_ledger_assert( array() === CEFA_Conversion_Tracking_Attribution_Ledger::verify_token( $token, 'form', 'franchise_us', 'ledger-test-secret', $now ), 'Cross-context ledger token was accepted.' );
cefa_ledger_assert( array() === CEFA_Conversion_Tracking_Attribution_Ledger::verify_token( $token, 'form', 'parent', 'ledger-test-secret', $now + 1800 ), 'Expired ledger token was accepted.' );

$GLOBALS['wpdb'] = new CEFA_Ledger_Test_WPDB();
$envelope        = array(
	'v'                     => '1.0',
	'site_context'          => 'parent',
	'last_non_direct_touch' => array(
		'source'   => 'google',
		'medium'   => 'cpc',
		'campaign' => 'parent-search',
	),
);
$captured        = CEFA_Conversion_Tracking_Attribution_Ledger::capture( $envelope, array() );

cefa_ledger_assert( $capture_id === $captured['capture_id'], 'Ledger did not retain its opaque capture ID.' );
cefa_ledger_assert( 1 === count( $GLOBALS['wpdb']->rows ), 'Ledger did not persist exactly one canonical record.' );

$from_form = CEFA_Conversion_Tracking_Attribution_Ledger::resolve(
	array(),
	array( 'cefa_capture_token' => $captured['capture_token'] )
);
cefa_ledger_assert( $envelope === $from_form['envelope'], 'Signed form fallback did not resolve canonical attribution.' );
cefa_ledger_assert( 'signed_form_fallback' === $from_form['source'], 'Form fallback provenance was not recorded.' );

$cookie_token = CEFA_Conversion_Tracking_Attribution_Ledger::issue_token(
	$capture_id,
	'cookie',
	'parent',
	3600,
	'ledger-test-secret'
);
$from_cookie  = CEFA_Conversion_Tracking_Attribution_Ledger::resolve(
	array( 'cefa_parent_capture_v2' => $cookie_token ),
	array()
);
cefa_ledger_assert( $envelope === $from_cookie['envelope'], 'Opaque capture cookie did not resolve canonical attribution.' );
cefa_ledger_assert( 'opaque_cookie' === $from_cookie['source'], 'Opaque cookie provenance was not recorded.' );

CEFA_Conversion_Tracking_Attribution_Ledger::persist_entry_reference( 77, 4, $from_form );
cefa_ledger_assert(
	$capture_id === $GLOBALS['cefa_ledger_test_meta'][77][ CEFA_Conversion_Tracking_Attribution_Ledger::CAPTURE_ID_META_KEY ]['value'],
	'Entry did not retain its opaque capture reference.'
);
cefa_ledger_assert(
	'shadow_signed_form_fallback' === $GLOBALS['cefa_ledger_test_meta'][77][ CEFA_Conversion_Tracking_Attribution_Ledger::STATUS_META_KEY ]['value'],
	'Entry did not retain ledger fallback provenance.'
);

echo "Attribution ledger tests passed.\n";
