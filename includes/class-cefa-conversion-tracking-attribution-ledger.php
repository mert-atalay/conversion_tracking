<?php
/**
 * Server-side attribution ledger with opaque signed browser handles.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Persists canonical attribution server-side without changing conversion flow.
 */
final class CEFA_Conversion_Tracking_Attribution_Ledger {
	public const CAPTURE_ID_META_KEY = 'cefa_conversion_tracking_capture_id';
	public const STATUS_META_KEY     = 'cefa_conversion_tracking_ledger_status';

	private const DB_VERSION        = '1';
	private const DB_VERSION_OPTION = 'cefa_ct_attribution_ledger_db_version';
	private const COOKIE_TTL        = 7776000;
	private const FORM_TOKEN_TTL    = 1800;
	private const TOKEN_VERSION     = '1.0';
	private const CLEANUP_TRANSIENT = 'cefa_ct_attribution_ledger_cleanup';

	/**
	 * Install the ledger during plugin activation.
	 *
	 * @return void
	 */
	public static function activate(): void {
		if ( 'off' === CEFA_Conversion_Tracking_Config::ledger_mode() || '' === CEFA_Conversion_Tracking_Config::ledger_secret() ) {
			return;
		}

		self::install();
	}

	/**
	 * Lazily install only when the guarded ledger is enabled.
	 *
	 * @return void
	 */
	public static function maybe_install(): void {
		if ( 'off' === CEFA_Conversion_Tracking_Config::ledger_mode() || '' === CEFA_Conversion_Tracking_Config::ledger_secret() ) {
			return;
		}

		if ( self::DB_VERSION !== (string) get_option( self::DB_VERSION_OPTION, '' ) ) {
			self::install();
		}

		self::maybe_cleanup();
	}

	/**
	 * Store canonical attribution and issue opaque browser/form handles.
	 *
	 * @param array<string, mixed> $envelope Canonical attribution envelope.
	 * @param array<string, mixed> $cookies  Current request cookies.
	 * @return array<string, string|bool>
	 */
	public static function capture( array $envelope, array $cookies ): array {
		$mode         = CEFA_Conversion_Tracking_Config::ledger_mode();
		$secret       = CEFA_Conversion_Tracking_Config::ledger_secret();
		$site_context = CEFA_Conversion_Tracking_Config::site_context();
		$cookie_name  = CEFA_Conversion_Tracking_Config::ledger_cookie_name();

		if ( 'off' === $mode || '' === $secret || 'unknown' === $site_context || '' === $cookie_name || empty( $envelope ) ) {
			return array();
		}

		$capture_id = '';

		if ( isset( $cookies[ $cookie_name ] ) ) {
			$verified   = self::verify_token( (string) $cookies[ $cookie_name ], 'cookie', $site_context, $secret );
			$capture_id = (string) ( $verified['capture_id'] ?? '' );
		}

		if ( '' === $capture_id ) {
			$capture_id = wp_generate_uuid4();
		}

		if ( ! self::valid_uuid( $capture_id ) || ! self::upsert( $capture_id, $site_context, $envelope ) ) {
			return array();
		}

		$cookie_token = self::issue_token( $capture_id, 'cookie', $site_context, self::COOKIE_TTL, $secret );
		$form_token   = self::issue_token( $capture_id, 'form', $site_context, self::FORM_TOKEN_TTL, $secret );
		$cookie_set   = self::set_capture_cookie( $cookie_name, $cookie_token );

		if ( '' === $cookie_token || '' === $form_token || ! $cookie_set ) {
			return array();
		}

		return array(
			'capture_id'    => $capture_id,
			'capture_token' => $form_token,
			'cookie_set'    => true,
			'mode'          => $mode,
		);
	}

	/**
	 * Resolve canonical attribution from the opaque cookie or form fallback.
	 *
	 * @param array<string, mixed> $cookies Current request cookies.
	 * @param array<string, mixed> $post    Current form POST values.
	 * @return array<string, mixed>
	 */
	public static function resolve( array $cookies, array $post ): array {
		$mode         = CEFA_Conversion_Tracking_Config::ledger_mode();
		$secret       = CEFA_Conversion_Tracking_Config::ledger_secret();
		$site_context = CEFA_Conversion_Tracking_Config::site_context();
		$cookie_name  = CEFA_Conversion_Tracking_Config::ledger_cookie_name();
		$candidates   = array();

		if ( 'off' === $mode || '' === $secret || 'unknown' === $site_context || '' === $cookie_name ) {
			return array();
		}

		if ( isset( $cookies[ $cookie_name ] ) ) {
			$candidates[] = array(
				'token'   => (string) $cookies[ $cookie_name ],
				'purpose' => 'cookie',
				'source'  => 'opaque_cookie',
			);
		}

		if ( isset( $post['cefa_capture_token'] ) && ! is_array( $post['cefa_capture_token'] ) ) {
			$candidates[] = array(
				'token'   => sanitize_text_field( wp_unslash( $post['cefa_capture_token'] ) ),
				'purpose' => 'form',
				'source'  => 'signed_form_fallback',
			);
		}

		foreach ( $candidates as $candidate ) {
			$verified   = self::verify_token(
				(string) $candidate['token'],
				(string) $candidate['purpose'],
				$site_context,
				$secret
			);
			$capture_id = (string) ( $verified['capture_id'] ?? '' );

			if ( '' === $capture_id ) {
				continue;
			}

			$envelope = self::load( $capture_id, $site_context );

			if ( empty( $envelope ) ) {
				continue;
			}

			return array(
				'capture_id' => $capture_id,
				'envelope'   => $envelope,
				'source'     => (string) $candidate['source'],
				'mode'       => $mode,
			);
		}

		return array();
	}

	/**
	 * Persist the opaque capture reference beside a Gravity Forms entry.
	 *
	 * @param int                  $entry_id Entry ID.
	 * @param int                  $form_id  Form ID.
	 * @param array<string, mixed> $resolved Resolved ledger record.
	 * @return void
	 */
	public static function persist_entry_reference( int $entry_id, int $form_id, array $resolved ): void {
		$capture_id = (string) ( $resolved['capture_id'] ?? '' );
		$source     = sanitize_key( (string) ( $resolved['source'] ?? '' ) );
		$mode       = sanitize_key( (string) ( $resolved['mode'] ?? '' ) );

		if ( $entry_id < 1 || ! self::valid_uuid( $capture_id ) || ! function_exists( 'gform_update_meta' ) ) {
			return;
		}

		gform_update_meta( $entry_id, self::CAPTURE_ID_META_KEY, $capture_id, $form_id );
		gform_update_meta( $entry_id, self::STATUS_META_KEY, $mode . '_' . $source, $form_id );
	}

	/**
	 * Issue a signed opaque token.
	 *
	 * @param string $capture_id  Capture UUID.
	 * @param string $purpose     `cookie` or `form`.
	 * @param string $site_context Site context.
	 * @param int    $ttl         Lifetime in seconds.
	 * @param string $secret      Signing secret.
	 * @param int    $now         Testable Unix timestamp.
	 * @return string
	 */
	public static function issue_token( string $capture_id, string $purpose, string $site_context, int $ttl, string $secret, int $now = 0 ): string {
		$now = $now > 0 ? $now : time();

		if ( ! self::valid_uuid( $capture_id ) || ! in_array( $purpose, array( 'cookie', 'form' ), true ) || '' === $secret || $ttl < 1 ) {
			return '';
		}

		$payload = wp_json_encode(
			array(
				'v'            => self::TOKEN_VERSION,
				'capture_id'   => $capture_id,
				'site_context' => sanitize_key( $site_context ),
				'purpose'      => $purpose,
				'exp'          => $now + $ttl,
			),
			JSON_UNESCAPED_SLASHES
		);

		if ( ! is_string( $payload ) ) {
			return '';
		}

		$encoded   = self::base64url_encode( $payload );
		$signature = self::base64url_encode( hash_hmac( 'sha256', $encoded, $secret, true ) );

		return $encoded . '.' . $signature;
	}

	/**
	 * Verify one opaque token and return its bounded claims.
	 *
	 * @param string $token        Signed token.
	 * @param string $purpose      Expected purpose.
	 * @param string $site_context Expected site context.
	 * @param string $secret       Signing secret.
	 * @param int    $now          Testable Unix timestamp.
	 * @return array<string, mixed>
	 */
	public static function verify_token( string $token, string $purpose, string $site_context, string $secret, int $now = 0 ): array {
		$parts = explode( '.', $token );
		$now   = $now > 0 ? $now : time();

		if ( 2 !== count( $parts ) || '' === $secret || strlen( $token ) > 1024 ) {
			return array();
		}

		$expected = self::base64url_encode( hash_hmac( 'sha256', $parts[0], $secret, true ) );

		if ( ! hash_equals( $expected, $parts[1] ) ) {
			return array();
		}

		$decoded = self::base64url_decode( $parts[0] );
		$claims  = is_string( $decoded ) ? json_decode( $decoded, true ) : null;

		if (
			! is_array( $claims ) ||
			self::TOKEN_VERSION !== (string) ( $claims['v'] ?? '' ) ||
			! self::valid_uuid( (string) ( $claims['capture_id'] ?? '' ) ) ||
			(string) ( $claims['purpose'] ?? '' ) !== $purpose ||
			sanitize_key( $site_context ) !== (string) ( $claims['site_context'] ?? '' ) ||
			(int) ( $claims['exp'] ?? 0 ) <= $now
		) {
			return array();
		}

		return array(
			'capture_id' => (string) $claims['capture_id'],
			'exp'        => (int) $claims['exp'],
		);
	}

	/**
	 * Insert or update one ledger row.
	 *
	 * @param string               $capture_id  Capture UUID.
	 * @param string               $site_context Site context.
	 * @param array<string, mixed> $envelope    Canonical envelope.
	 * @return bool
	 */
	private static function upsert( string $capture_id, string $site_context, array $envelope ): bool {
		global $wpdb;

		if ( ! isset( $wpdb ) || ! is_object( $wpdb ) ) {
			return false;
		}

		$encoded = wp_json_encode( $envelope, JSON_UNESCAPED_SLASHES );

		if ( ! is_string( $encoded ) || '' === $encoded ) {
			return false;
		}

		$now     = current_time( 'mysql', true );
		$expires = gmdate( 'Y-m-d H:i:s', time() + self::COOKIE_TTL );
		// The table name is generated internally from the trusted WordPress prefix; values still use placeholders.
		// phpcs:disable WordPress.DB.PreparedSQL.NotPrepared
		$sql    = $wpdb->prepare(
			'INSERT INTO ' . self::table_name() . ' (capture_id, site_context, envelope_json, created_at, updated_at, expires_at)
			VALUES (%s, %s, %s, %s, %s, %s)
			ON DUPLICATE KEY UPDATE envelope_json = VALUES(envelope_json), updated_at = VALUES(updated_at), expires_at = VALUES(expires_at)',
			$capture_id,
			sanitize_key( $site_context ),
			$encoded,
			$now,
			$now,
			$expires
		);
		$result = $wpdb->query( $sql ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery,WordPress.DB.DirectDatabaseQuery.NoCaching -- Durable attribution ledger write.
		// phpcs:enable WordPress.DB.PreparedSQL.NotPrepared

		return false !== $result;
	}

	/**
	 * Load one unexpired ledger envelope.
	 *
	 * @param string $capture_id  Capture UUID.
	 * @param string $site_context Site context.
	 * @return array<string, mixed>
	 */
	private static function load( string $capture_id, string $site_context ): array {
		global $wpdb;

		if ( ! isset( $wpdb ) || ! is_object( $wpdb ) ) {
			return array();
		}

		// The table name is generated internally from the trusted WordPress prefix; values still use placeholders.
		// phpcs:disable WordPress.DB.PreparedSQL.NotPrepared
		$encoded = $wpdb->get_var( // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery,WordPress.DB.DirectDatabaseQuery.NoCaching -- Ledger identity must be read durably.
			$wpdb->prepare(
				'SELECT envelope_json FROM ' . self::table_name() . ' WHERE capture_id = %s AND site_context = %s AND expires_at >= %s',
				$capture_id,
				sanitize_key( $site_context ),
				current_time( 'mysql', true )
			)
		);
		// phpcs:enable WordPress.DB.PreparedSQL.NotPrepared
		$envelope = is_string( $encoded ) ? json_decode( $encoded, true ) : null;

		return is_array( $envelope ) ? $envelope : array();
	}

	/**
	 * Set the opaque host-only capture cookie.
	 *
	 * @param string $cookie_name Cookie name.
	 * @param string $token       Signed opaque token.
	 * @return bool
	 */
	private static function set_capture_cookie( string $cookie_name, string $token ): bool {
		if ( headers_sent() || '' === $cookie_name || '' === $token ) {
			return false;
		}

		return setcookie(
			$cookie_name,
			$token,
			array(
				'expires'  => time() + self::COOKIE_TTL,
				'path'     => '/',
				'secure'   => is_ssl(),
				'httponly' => true,
				'samesite' => 'Lax',
			)
		);
	}

	/**
	 * Create or upgrade the ledger table.
	 *
	 * @return void
	 */
	private static function install(): void {
		global $wpdb;

		if ( ! isset( $wpdb ) || ! is_object( $wpdb ) || ! defined( 'ABSPATH' ) ) {
			return;
		}

		require_once ABSPATH . 'wp-admin/includes/upgrade.php';

		$charset_collate = $wpdb->get_charset_collate();
		$table           = self::table_name();
		$sql             = "CREATE TABLE {$table} (
			capture_id char(36) NOT NULL,
			site_context varchar(32) NOT NULL,
			envelope_json longtext NOT NULL,
			created_at datetime NOT NULL,
			updated_at datetime NOT NULL,
			expires_at datetime NOT NULL,
			PRIMARY KEY  (capture_id),
			KEY context_expiry (site_context, expires_at),
			KEY updated_at (updated_at)
		) {$charset_collate};";

		dbDelta( $sql );
		update_option( self::DB_VERSION_OPTION, self::DB_VERSION, false );
	}

	/**
	 * Delete expired rows at most once per day.
	 *
	 * @return void
	 */
	private static function maybe_cleanup(): void {
		global $wpdb;

		if ( get_transient( self::CLEANUP_TRANSIENT ) || ! isset( $wpdb ) || ! is_object( $wpdb ) ) {
			return;
		}

		set_transient( self::CLEANUP_TRANSIENT, '1', DAY_IN_SECONDS );
		// The table name is generated internally from the trusted WordPress prefix; values still use placeholders.
		// phpcs:disable WordPress.DB.PreparedSQL.NotPrepared
		$wpdb->query( // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery,WordPress.DB.DirectDatabaseQuery.NoCaching -- Bounded daily retention cleanup.
			$wpdb->prepare(
				'DELETE FROM ' . self::table_name() . ' WHERE expires_at < %s',
				current_time( 'mysql', true )
			)
		);
		// phpcs:enable WordPress.DB.PreparedSQL.NotPrepared
	}

	/**
	 * Validate a UUID without accepting arbitrary identifiers.
	 *
	 * @param string $value Candidate value.
	 * @return bool
	 */
	private static function valid_uuid( string $value ): bool {
		return 1 === preg_match( '/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i', $value );
	}

	/**
	 * Base64url encode a byte string.
	 *
	 * @param string $value Raw value.
	 * @return string
	 */
	private static function base64url_encode( string $value ): string {
		return rtrim( strtr( base64_encode( $value ), '+/', '-_' ), '=' ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_encode -- Required for compact signed tokens.
	}

	/**
	 * Base64url decode a string.
	 *
	 * @param string $value Encoded value.
	 * @return string|false
	 */
	private static function base64url_decode( string $value ) {
		$padding = strlen( $value ) % 4;

		if ( $padding > 0 ) {
			$value .= str_repeat( '=', 4 - $padding );
		}

		return base64_decode( strtr( $value, '-_', '+/' ), true ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_decode -- Required for compact signed tokens.
	}

	/**
	 * Return the prefixed ledger table name.
	 *
	 * @return string
	 */
	private static function table_name(): string {
		global $wpdb;

		return $wpdb->prefix . 'cefa_ct_attribution_ledger';
	}
}
