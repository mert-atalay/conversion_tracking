<?php
/**
 * Focused Attribution Bridge envelope contract tests.
 *
 * @package CEFA_Conversion_Tracking
 */

define( 'ABSPATH', __DIR__ . '/' );
define( 'CEFA_CONVERSION_TRACKING_FORM_ID', 4 );
define( 'MINUTE_IN_SECONDS', 60 );

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
	public const EVENT_ID_META_KEY = 'cefa_conversion_tracking_event_id';

	public static $mode        = 'shadow';
	public static $crm_enabled = false;
	public static $payload_v2  = false;

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

	public static function crm_identity_enabled() {
		return self::$crm_enabled;
	}

	public static function payload_v2_enabled() {
		return self::$payload_v2;
	}

	public static function payload_v2_secret() {
		return 'payload-test-secret';
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

if ( ! function_exists( 'esc_url_raw' ) ) {
	function esc_url_raw( $value ) {
		return filter_var( $value, FILTER_SANITIZE_URL );
	}
}

if ( ! function_exists( 'rgar' ) ) {
	function rgar( $array, $key ) {
		return is_array( $array ) && array_key_exists( $key, $array ) ? $array[ $key ] : null;
	}
}

if ( ! function_exists( 'sanitize_key' ) ) {
	function sanitize_key( $value ) {
		return preg_replace( '/[^a-z0-9_\-]/', '', strtolower( (string) $value ) );
	}
}

if ( ! function_exists( 'current_time' ) ) {
	function current_time( $type, $gmt = false ) {
		unset( $type, $gmt );
		return gmdate( 'Y-m-d H:i:s' );
	}
}

if ( ! function_exists( 'wp_generate_uuid4' ) ) {
	function wp_generate_uuid4() {
		static $counter = 0;
		++$counter;
		return sprintf( '00000000-0000-4000-8000-%012d', $counter );
	}
}

/**
 * Minimal wpdb substitute with primary-key behavior.
 */
final class CEFA_Test_WPDB {
	public $prefix = 'wp_';
	public $rows   = array();

	public function insert( $table, $data, $formats ) {
		unset( $table, $formats );
		if ( isset( $this->rows[ $data['event_id'] ] ) ) {
			return false;
		}
		$this->rows[ $data['event_id'] ] = $data;
		return 1;
	}

	public function update( $table, $data, $where, $formats, $where_formats ) {
		unset( $table, $formats, $where_formats );
		if ( ! isset( $this->rows[ $where['event_id'] ] ) ) {
			return false;
		}
		$this->rows[ $where['event_id'] ] = array_merge( $this->rows[ $where['event_id'] ], $data );
		return 1;
	}
}

$GLOBALS['cefa_test_meta']         = array();
$GLOBALS['cefa_test_meta_updates'] = 0;
$GLOBALS['cefa_test_transients']   = array();

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

if ( ! function_exists( 'set_transient' ) ) {
	function set_transient( $key, $value, $ttl ) {
		$GLOBALS['cefa_test_transients'][ $key ] = array( 'value' => $value, 'ttl' => $ttl );
		return true;
	}
}

if ( ! function_exists( 'get_transient' ) ) {
	function get_transient( $key ) {
		return isset( $GLOBALS['cefa_test_transients'][ $key ] ) ? $GLOBALS['cefa_test_transients'][ $key ]['value'] : false;
	}
}

if ( ! function_exists( 'delete_transient' ) ) {
	function delete_transient( $key ) {
		unset( $GLOBALS['cefa_test_transients'][ $key ] );
		return true;
	}
}

require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-entry-attribution.php';
require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-attribution.php';
require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-event-id.php';
require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-event-id-registry.php';
require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-submission-identity.php';
require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking-duplicate-guard.php';

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

$_COOKIE['_ga'] = 'GA1.1.123456789.987654321';
CEFA_Conversion_Tracking_Config::$mode        = 'shadow';
CEFA_Conversion_Tracking_Config::$crm_enabled = true;
$_POST = array( 'input_35' => 'legacy-source' );
$parent_fields = array(
	'id'                 => 4,
	'attribution_fields' => array(
		'utm_source'         => '35',
		'utm_medium'         => '36',
		'utm_campaign'       => '37',
		'utm_term'           => '38',
		'utm_content'        => '39',
		'gclid'              => '40',
		'gbraid'             => '41',
		'wbraid'             => '42',
		'fbclid'             => '43',
		'msclkid'            => '44',
		'first_landing_page' => '45',
		'first_referrer'     => '46',
	),
);
CEFA_Conversion_Tracking_Attribution::apply_primary_compatibility_fields( $parent_fields );
cefa_assert( 'legacy-source' === $_POST['input_35'], 'Shadow mode overwrote a parent compatibility field.' );

CEFA_Conversion_Tracking_Config::$mode = 'primary';
CEFA_Conversion_Tracking_Config::$crm_enabled = false;
CEFA_Conversion_Tracking_Attribution::apply_primary_compatibility_fields( $parent_fields );
cefa_assert( 'legacy-source' === $_POST['input_35'], 'Disabled CRM adapter overwrote a parent field.' );

CEFA_Conversion_Tracking_Config::$crm_enabled = true;
CEFA_Conversion_Tracking_Attribution::apply_primary_compatibility_fields( $parent_fields );
cefa_assert( 'google' === $_POST['input_35'], 'Primary parent source adapter failed.' );
cefa_assert( 'test-gclid' === $_POST['input_40'], 'Primary parent GCLID adapter failed.' );
cefa_assert( 'https://cefa.ca/' === $_POST['input_45'], 'Primary parent landing adapter failed.' );

$franchise_fields = array(
	'id'                 => 1,
	'attribution_fields' => array(
		'lc_source'    => '14',
		'lc_medium'    => '15',
		'lc_campaign'  => '16',
		'lc_content'   => '17',
		'lc_term'      => '18',
		'lc_channel'   => '19',
		'lc_landing'   => '20',
		'lc_referrer'  => '21',
		'fc_source'    => '22',
		'fc_medium'    => '23',
		'fc_campaign'  => '24',
		'fc_content'   => '25',
		'fc_term'      => '26',
		'fc_channel'   => '27',
		'fc_referrer'  => '28',
		'gclid'        => '29',
		'ga_client_id' => '30',
	),
);
CEFA_Conversion_Tracking_Attribution::apply_primary_compatibility_fields( $franchise_fields );
cefa_assert( 'google' === $_POST['input_14'] && 'google' === $_POST['input_22'], 'Franchise first/last source adapter failed.' );
cefa_assert( 'test-gclid' === $_POST['input_29'], 'Franchise GCLID adapter failed.' );
cefa_assert( '123456789.987654321' === $_POST['input_30'], 'Franchise GA client adapter failed.' );

$GLOBALS['wpdb'] = new CEFA_Test_WPDB();
$reserved_ids    = array();

for ( $index = 0; $index < 10000; ++$index ) {
	$reserved_id = CEFA_Conversion_Tracking_Event_ID_Registry::generate_and_reserve( 'parent', 4, $index + 1 );
	cefa_assert( '' !== $reserved_id, 'Registry failed to reserve a generated ID.' );
	cefa_assert( ! isset( $reserved_ids[ $reserved_id ] ), 'Registry generated a duplicate ID.' );
	$reserved_ids[ $reserved_id ] = true;
}
cefa_assert( 10000 === count( $reserved_ids ), 'Registry did not produce 10,000 unique IDs.' );

CEFA_Conversion_Tracking_Config::$mode = 'shadow';
$_POST = array( 'input_32_4' => 'browser-attempt-shadow' );
$identity_form = array(
	'id'                 => 4,
	'event_id_fields'    => array( '32.4' ),
	'event_id_post_keys' => array( 'input_32_4' ),
);
CEFA_Conversion_Tracking_Submission_Identity::prepare_before_submission( $identity_form );
$shadow_identity = CEFA_Conversion_Tracking_Submission_Identity::finalize_after_submission(
	array( 'id' => 201, 'form_id' => 4, 'status' => 'active' ),
	$identity_form
);
cefa_assert( 'browser-attempt-shadow' === $_POST['input_32_4'], 'Shadow mode replaced the operational event ID.' );
cefa_assert( ! empty( $shadow_identity[ CEFA_Conversion_Tracking_Submission_Identity::SERVER_EVENT_ID_META_KEY ] ), 'Shadow server event ID was not saved.' );
cefa_assert( 'browser-attempt-shadow' === $shadow_identity[ CEFA_Conversion_Tracking_Submission_Identity::ATTEMPT_ID_META_KEY ], 'Shadow attempt ID was not preserved.' );

CEFA_Conversion_Tracking_Config::$mode = 'primary';
$_POST = array( 'input_32_4' => 'browser-attempt-primary' );
CEFA_Conversion_Tracking_Submission_Identity::prepare_before_submission( $identity_form );
$primary_operational_id = $_POST['input_32_4'];
$primary_identity = CEFA_Conversion_Tracking_Submission_Identity::finalize_after_submission(
	array( 'id' => 202, 'form_id' => 4, 'status' => 'active', '32.4' => $primary_operational_id ),
	$identity_form
);
cefa_assert( 'browser-attempt-primary' !== $primary_operational_id, 'Primary mode kept the browser attempt as final identity.' );
cefa_assert( $primary_operational_id === $primary_identity[ CEFA_Conversion_Tracking_Submission_Identity::SERVER_EVENT_ID_META_KEY ], 'Primary server ID did not remain consistent after save.' );
cefa_assert( 'browser-attempt-primary' === $primary_identity[ CEFA_Conversion_Tracking_Submission_Identity::ATTEMPT_ID_META_KEY ], 'Primary attempt ID was not retained separately.' );

$payload = array(
	'event'        => 'school_inquiry_submit',
	'event_id'     => '00000000-0000-4000-8000-000000099999',
	'site_context' => 'parent',
);
CEFA_Conversion_Tracking_Config::$payload_v2 = true;
$signed_token = CEFA_Conversion_Tracking_Duplicate_Guard::store_payload( $payload );
cefa_assert( false !== strpos( $signed_token, '.' ), 'V2 payload did not receive a signed token.' );
cefa_assert( $payload === CEFA_Conversion_Tracking_Duplicate_Guard::consume_payload( $signed_token ), 'First signed payload read failed.' );
cefa_assert( $payload === CEFA_Conversion_Tracking_Duplicate_Guard::consume_payload( $signed_token ), 'Signed payload was not replay-safe.' );
cefa_assert( null === CEFA_Conversion_Tracking_Duplicate_Guard::consume_payload( $signed_token . 'x' ), 'Tampered payload token was accepted.' );
cefa_assert( $payload === CEFA_Conversion_Tracking_Duplicate_Guard::consume_payload_by_event_id( $payload['event_id'] ), 'Event-ID alias did not retain the signed payload.' );

CEFA_Conversion_Tracking_Config::$payload_v2 = false;
$legacy_token = CEFA_Conversion_Tracking_Duplicate_Guard::store_payload( $payload );
cefa_assert( false === strpos( $legacy_token, '.' ), 'Legacy payload unexpectedly received a V2 token.' );
cefa_assert( $payload === CEFA_Conversion_Tracking_Duplicate_Guard::consume_payload( $legacy_token ), 'Legacy payload read failed.' );
cefa_assert( null === CEFA_Conversion_Tracking_Duplicate_Guard::consume_payload( $legacy_token ), 'Legacy payload was not consumed once.' );

echo "Attribution, identity, adapter, and payload tests passed.\n";
