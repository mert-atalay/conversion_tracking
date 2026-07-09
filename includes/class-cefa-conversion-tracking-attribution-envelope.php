<?php
/**
 * Signed, hostname-scoped attribution envelope.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Captures bounded acquisition evidence without changing production form fields.
 */
final class CEFA_Conversion_Tracking_Attribution_Envelope {
	private const SCHEMA_VERSION = '1.0';
	private const COOKIE_TTL     = 7776000;
	private const MAX_TOUCHES    = 8;
	private const MAX_TOKEN_SIZE = 3800;

	private const QUERY_KEYS = array(
		'utm_source',
		'utm_medium',
		'utm_campaign',
		'utm_id',
		'utm_term',
		'utm_content',
		'gclid',
		'gbraid',
		'wbraid',
		'fbclid',
		'msclkid',
		'google_adgroup_id',
		'google_network',
		'google_device',
		'google_matchtype',
		'meta_campaign_id',
		'meta_adset_id',
		'meta_ad_id',
		'cefa_agency_test',
	);

	private const OWN_HOSTS = array(
		'cefa.ca',
		'www.cefa.ca',
		'cefamain.kinsta.cloud',
		'franchise.cefa.ca',
		'cefafranchise.kinsta.cloud',
		'franchisecefa.com',
		'www.franchisecefa.com',
		'cefafranusdev.wpenginepowered.com',
	);

	/**
	 * Capture the current request when shadow or primary mode is enabled.
	 *
	 * @return void
	 */
	public static function capture_request(): void {
		$mode = CEFA_Conversion_Tracking_Config::attribution_v2_mode();

		if ( 'off' === $mode || is_admin() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) {
			return;
		}

		$secret       = CEFA_Conversion_Tracking_Config::attribution_v2_secret();
		$site_context = CEFA_Conversion_Tracking_Config::site_context();
		$cookie_name  = CEFA_Conversion_Tracking_Config::attribution_cookie_name();

		if ( '' === $secret || 'unknown' === $site_context || '' === $cookie_name || headers_sent() ) {
			return;
		}

		$existing = array();

		if ( isset( $_COOKIE[ $cookie_name ] ) ) {
			$cookie_value = sanitize_text_field( wp_unslash( $_COOKIE[ $cookie_name ] ) ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended
			$existing     = self::decode(
				$cookie_value,
				$secret,
				$site_context
			);
		}

		$envelope = self::capture( $_GET, $_SERVER, $site_context, $existing ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended

		if ( empty( $envelope ) || $envelope === $existing ) {
			return;
		}

		$token = self::encode( $envelope, $secret );

		if ( '' === $token ) {
			return;
		}

		setcookie(
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
	 * Build a canonical envelope from allowlisted request evidence.
	 *
	 * @param array<string, mixed> $query        Request query.
	 * @param array<string, mixed> $server       Server values.
	 * @param string               $site_context Governed site context.
	 * @param array<string, mixed> $existing     Verified prior envelope.
	 * @param int                  $now          Testable Unix timestamp.
	 * @return array<string, mixed>
	 */
	public static function capture( array $query, array $server, string $site_context, array $existing = array(), int $now = 0 ): array {
		$now    = $now > 0 ? $now : time();
		$params = self::allowlisted_params( $query );
		$touch  = self::build_touch( $params, $server, $now );

		if ( empty( $touch ) ) {
			return $existing;
		}

		$envelope = self::valid_existing_shape( $existing, $site_context, $now ) ? $existing : self::empty_envelope( $site_context );

		if ( empty( $envelope['first_touch'] ) ) {
			$envelope['first_touch'] = $touch;
		}

		$envelope['last_non_direct_touch'] = $touch;
		$envelope['current_touch']         = $touch;
		$envelope['click_ids']             = self::merge_click_ids( (array) $envelope['click_ids'], $params );
		$envelope['platform_ids']          = self::platform_ids( $params, (array) $envelope['platform_ids'] );
		$envelope['experiment']            = self::experiment( $params, (array) $envelope['experiment'] );

		$history   = is_array( $envelope['touch_history'] ) ? $envelope['touch_history'] : array();
		$signature = self::touch_signature( $touch );
		$last      = end( $history );

		if ( ! is_array( $last ) || self::touch_signature( $last ) !== $signature ) {
			$history[] = $touch;
		}

		$envelope['touch_history'] = array_slice( $history, -self::MAX_TOUCHES );
		$envelope['touch_count']   = count( $envelope['touch_history'] );
		$envelope['captured_at']   = gmdate( 'c', $now );
		$envelope['expires_at']    = gmdate( 'c', $now + self::COOKIE_TTL );

		return self::fit_cookie_budget( $envelope );
	}

	/**
	 * Sign an envelope for host-only cookie storage.
	 *
	 * @param array<string, mixed> $envelope Canonical envelope.
	 * @param string               $secret   Server-only secret.
	 * @return string
	 */
	public static function encode( array $envelope, string $secret ): string {
		if ( '' === $secret || empty( $envelope ) ) {
			return '';
		}

		$json = wp_json_encode( $envelope, JSON_UNESCAPED_SLASHES );

		if ( ! is_string( $json ) ) {
			return '';
		}

		$payload   = self::base64url_encode( $json );
		$signature = self::base64url_encode( hash_hmac( 'sha256', $payload, $secret, true ) );
		$token     = $payload . '.' . $signature;

		return strlen( $token ) <= self::MAX_TOKEN_SIZE ? $token : '';
	}

	/**
	 * Verify and decode an envelope.
	 *
	 * @param string $token        Signed token.
	 * @param string $secret       Server-only secret.
	 * @param string $site_context Expected site context.
	 * @param int    $now          Testable Unix timestamp.
	 * @return array<string, mixed>
	 */
	public static function decode( string $token, string $secret, string $site_context, int $now = 0 ): array {
		$parts = explode( '.', $token );

		if ( 2 !== count( $parts ) || '' === $secret ) {
			return array();
		}

		$expected = self::base64url_encode( hash_hmac( 'sha256', $parts[0], $secret, true ) );

		if ( ! hash_equals( $expected, $parts[1] ) ) {
			return array();
		}

		$json = self::base64url_decode( $parts[0] );
		$data = is_string( $json ) ? json_decode( $json, true ) : null;

		return is_array( $data ) && self::valid_existing_shape( $data, $site_context, $now > 0 ? $now : time() ) ? $data : array();
	}

	/**
	 * Keep only approved, bounded query values.
	 *
	 * @param array<string, mixed> $query Query parameters.
	 * @return array<string, string>
	 */
	private static function allowlisted_params( array $query ): array {
		$output = array();

		foreach ( self::QUERY_KEYS as $key ) {
			if ( ! isset( $query[ $key ] ) || is_array( $query[ $key ] ) ) {
				continue;
			}

			$value = self::normalize_value( (string) $query[ $key ], 220 );

			if ( '' !== $value ) {
				$output[ $key ] = $value;
			}
		}

		return $output;
	}

	/**
	 * Build one meaningful non-direct acquisition touch.
	 *
	 * @param array<string, string> $params Allowlisted parameters.
	 * @param array<string, mixed>  $server Server values.
	 * @param int                   $now    Unix timestamp.
	 * @return array<string, string>
	 */
	private static function build_touch( array $params, array $server, int $now ): array {
		$referrer = self::safe_url_parts( (string) ( $server['HTTP_REFERER'] ?? '' ) );
		$landing  = self::landing_parts( $server );
		$source   = strtolower( (string) ( $params['utm_source'] ?? '' ) );
		$medium   = strtolower( (string) ( $params['utm_medium'] ?? '' ) );
		$channel  = '';
		$click    = self::current_click_id_type( $params );

		if ( in_array( $click, array( 'gclid', 'gbraid', 'wbraid' ), true ) ) {
			$source  = 'google';
			$medium  = 'cpc';
			$channel = 'paid_search';
		} elseif ( 'msclkid' === $click ) {
			$source  = 'bing';
			$medium  = 'cpc';
			$channel = 'paid_search';
		} elseif ( 'fbclid' === $click ) {
			$source  = in_array( $source, array( 'facebook', 'instagram', 'meta' ), true ) ? $source : 'facebook';
			$medium  = 'paid_social';
			$channel = 'paid_social';
		} elseif ( '' !== $source || '' !== $medium || self::has_explicit_utm( $params ) ) {
			$source  = '' !== $source ? $source : 'unknown';
			$medium  = '' !== $medium ? $medium : 'campaign';
			$channel = self::channel_from_medium( $source, $medium );
		} elseif ( ! empty( $referrer['host'] ) && ! self::is_own_host( $referrer['host'] ) ) {
			$source  = self::source_from_referrer( $referrer['host'] );
			$channel = self::referrer_channel( $referrer['host'] );
			$medium  = 'organic_search' === $channel ? 'organic' : 'referral';
		} else {
			return array();
		}

		return array_filter(
			array(
				'source'        => self::normalize_value( $source, 120 ),
				'medium'        => self::normalize_value( $medium, 80 ),
				'campaign'      => self::normalize_value( (string) ( $params['utm_campaign'] ?? '' ), 180 ),
				'campaign_id'   => self::normalize_value( (string) ( $params['utm_id'] ?? '' ), 120 ),
				'content'       => self::normalize_value( (string) ( $params['utm_content'] ?? '' ), 180 ),
				'term'          => self::normalize_value( (string) ( $params['utm_term'] ?? '' ), 180 ),
				'channel'       => $channel,
				'landing_host'  => (string) ( $landing['host'] ?? '' ),
				'landing_path'  => (string) ( $landing['path'] ?? '' ),
				'referrer_host' => (string) ( $referrer['host'] ?? '' ),
				'referrer_path' => (string) ( $referrer['path'] ?? '' ),
				'touch_at'      => gmdate( 'c', $now ),
				'click_id_type' => $click,
			),
			static function ( $value ): bool {
				return '' !== $value;
			}
		);
	}

	/**
	 * Initialize the canonical shape.
	 *
	 * @param string $site_context Site context.
	 * @return array<string, mixed>
	 */
	private static function empty_envelope( string $site_context ): array {
		return array(
			'schema_version'        => self::SCHEMA_VERSION,
			'site_context'          => $site_context,
			'captured_at'           => '',
			'expires_at'            => '',
			'first_touch'           => array(),
			'last_non_direct_touch' => array(),
			'current_touch'         => array(),
			'click_ids'             => array(),
			'platform_ids'          => array(),
			'experiment'            => array(),
			'touch_count'           => 0,
			'touch_history'         => array(),
		);
	}

	/**
	 * Validate the envelope identity and expiry.
	 *
	 * @param array<string, mixed> $envelope     Envelope.
	 * @param string               $site_context Expected context.
	 * @param int                  $now          Unix timestamp.
	 * @return bool
	 */
	private static function valid_existing_shape( array $envelope, string $site_context, int $now ): bool {
		$expires = strtotime( (string) ( $envelope['expires_at'] ?? '' ) );

		return self::SCHEMA_VERSION === ( $envelope['schema_version'] ?? '' )
			&& 0 === strcmp( $site_context, (string) ( $envelope['site_context'] ?? '' ) )
			&& false !== $expires
			&& $now <= $expires
			&& is_array( $envelope['touch_history'] ?? null );
	}

	/**
	 * Merge click IDs and keep only the newest Google click-ID family member.
	 *
	 * @param array<string, string> $existing Existing click IDs.
	 * @param array<string, string> $params   Current parameters.
	 * @return array<string, string>
	 */
	private static function merge_click_ids( array $existing, array $params ): array {
		$google_type = '';

		foreach ( array( 'gclid', 'gbraid', 'wbraid' ) as $key ) {
			if ( ! empty( $params[ $key ] ) ) {
				$google_type = $key;
				break;
			}
		}

		if ( '' !== $google_type ) {
			unset( $existing['gclid'], $existing['gbraid'], $existing['wbraid'] );
			$existing[ $google_type ] = $params[ $google_type ];
		}

		foreach ( array( 'fbclid', 'msclkid' ) as $key ) {
			if ( ! empty( $params[ $key ] ) ) {
				$existing[ $key ] = $params[ $key ];
			}
		}

		return $existing;
	}

	/**
	 * Merge governed platform identifiers.
	 *
	 * @param array<string, string> $params   Current parameters.
	 * @param array<string, string> $existing Existing identifiers.
	 * @return array<string, string>
	 */
	private static function platform_ids( array $params, array $existing ): array {
		foreach ( array( 'google_adgroup_id', 'google_network', 'google_device', 'google_matchtype', 'meta_campaign_id', 'meta_adset_id', 'meta_ad_id' ) as $key ) {
			if ( ! empty( $params[ $key ] ) ) {
				$existing[ $key ] = $params[ $key ];
			}
		}

		return $existing;
	}

	/**
	 * Persist only the approved in-house experiment marker.
	 *
	 * @param array<string, string> $params   Current parameters.
	 * @param array<string, string> $existing Existing experiment.
	 * @return array<string, string>
	 */
	private static function experiment( array $params, array $existing ): array {
		$value = strtolower( (string) ( $params['cefa_agency_test'] ?? '' ) );

		if ( in_array( $value, array( 'in_house', 'fr_us_in_house' ), true ) ) {
			return array( 'agency_test' => 'fr_us_in_house' );
		}

		return $existing;
	}

	/**
	 * Reduce old history until the signed token can fit in a cookie.
	 *
	 * @param array<string, mixed> $envelope Envelope.
	 * @return array<string, mixed>
	 */
	private static function fit_cookie_budget( array $envelope ): array {
		$history_count = count( $envelope['touch_history'] );
		$encoded_size  = strlen( (string) wp_json_encode( $envelope ) );

		while ( 1 < $history_count && 2600 < $encoded_size ) {
			array_shift( $envelope['touch_history'] );
			$history_count = count( $envelope['touch_history'] );
			$encoded_size  = strlen( (string) wp_json_encode( $envelope ) );
		}

		$envelope['touch_count'] = count( $envelope['touch_history'] );

		return $envelope;
	}

	/**
	 * Return a stable signature for touch-history deduplication.
	 *
	 * @param array<string, mixed> $touch Touch.
	 * @return string
	 */
	private static function touch_signature( array $touch ): string {
		return implode( '|', array( $touch['source'] ?? '', $touch['medium'] ?? '', $touch['campaign_id'] ?? '', $touch['campaign'] ?? '', $touch['content'] ?? '', $touch['landing_host'] ?? '', $touch['landing_path'] ?? '', $touch['click_id_type'] ?? '' ) );
	}

	/**
	 * Normalize a bounded parameter and reject placeholders/control characters.
	 *
	 * @param string $value      Candidate value.
	 * @param int    $max_length Maximum length.
	 * @return string
	 */
	private static function normalize_value( string $value, int $max_length ): string {
		$value = trim( $value );

		if ( '' === $value || preg_match( '/[\x00-\x1F\x7F]/', $value ) || preg_match( '/^(undefined|null|\(not set\)|not set|\{\{[^}]+\}\})$/i', $value ) ) {
			return '';
		}

		return substr( preg_replace( '/\s+/', ' ', $value ), 0, $max_length );
	}

	/**
	 * Return normalized host/path only.
	 *
	 * @param string $url URL.
	 * @return array<string, string>
	 */
	private static function safe_url_parts( string $url ): array {
		$parts = wp_parse_url( $url );

		if ( ! is_array( $parts ) || empty( $parts['host'] ) ) {
			return array();
		}

		return array(
			'host' => strtolower( preg_replace( '/:\d+$/', '', (string) $parts['host'] ) ),
			'path' => self::normalize_path( (string) ( $parts['path'] ?? '/' ) ),
		);
	}

	/**
	 * Build normalized landing host/path from the current request.
	 *
	 * @param array<string, mixed> $server Server values.
	 * @return array<string, string>
	 */
	private static function landing_parts( array $server ): array {
		$host = strtolower( preg_replace( '/:\d+$/', '', (string) ( $server['HTTP_HOST'] ?? '' ) ) );
		$path = (string) wp_parse_url( (string) ( $server['REQUEST_URI'] ?? '/' ), PHP_URL_PATH );

		return array(
			'host' => self::normalize_value( $host, 180 ),
			'path' => self::normalize_path( $path ),
		);
	}

	/**
	 * Normalize a URL path without retaining query strings.
	 *
	 * @param string $path URL path.
	 * @return string
	 */
	private static function normalize_path( string $path ): string {
		$path = '/' . ltrim( $path, '/' );

		return substr( preg_replace( '#/+#', '/', $path ), 0, 500 );
	}

	/**
	 * Determine whether explicit campaign evidence exists.
	 *
	 * @param array<string, string> $params Parameters.
	 * @return bool
	 */
	private static function has_explicit_utm( array $params ): bool {
		foreach ( array( 'utm_source', 'utm_medium', 'utm_campaign', 'utm_id', 'utm_term', 'utm_content' ) as $key ) {
			if ( ! empty( $params[ $key ] ) ) {
				return true;
			}
		}

		return false;
	}

	/**
	 * Return the current request click-ID type by precedence.
	 *
	 * @param array<string, string> $params Parameters.
	 * @return string
	 */
	private static function current_click_id_type( array $params ): string {
		foreach ( array( 'gclid', 'gbraid', 'wbraid', 'msclkid', 'fbclid' ) as $key ) {
			if ( ! empty( $params[ $key ] ) ) {
				return $key;
			}
		}

		return '';
	}

	/**
	 * Classify governed source/medium pairs.
	 *
	 * @param string $source Source.
	 * @param string $medium Medium.
	 * @return string
	 */
	private static function channel_from_medium( string $source, string $medium ): string {
		if ( false !== strpos( $medium, 'social' ) && preg_match( '/facebook|instagram|meta|linkedin|tiktok/', $source ) ) {
			return 'paid_social';
		}

		if ( preg_match( '/^(cpc|ppc|paid_search|paid-search)$/', $medium ) ) {
			return 'paid_search';
		}

		if ( 'organic' === $medium ) {
			return 'organic_search';
		}

		if ( 'email' === $medium ) {
			return 'email';
		}

		return 'referral';
	}

	/**
	 * Exclude governed CEFA journey hosts by exact hostname.
	 *
	 * @param string $host Hostname.
	 * @return bool
	 */
	private static function is_own_host( string $host ): bool {
		return in_array( strtolower( $host ), self::OWN_HOSTS, true );
	}

	/**
	 * Map approved referrer hosts to sources.
	 *
	 * @param string $host Hostname.
	 * @return string
	 */
	private static function source_from_referrer( string $host ): string {
		$host = strtolower( preg_replace( '/^www\./', '', $host ) );

		if ( preg_match( '/(^|\.)google\.[a-z.]+$/', $host ) ) {
			return 'google';
		}

		$search_sources = array(
			'bing.com'         => 'bing',
			'search.yahoo.com' => 'yahoo',
			'duckduckgo.com'   => 'duckduckgo',
		);

		if ( isset( $search_sources[ $host ] ) ) {
			return $search_sources[ $host ];
		}

		if ( preg_match( '/(^|\.)(facebook|instagram)\.com$/', $host, $matches ) ) {
			return $matches[2];
		}

		return self::normalize_value( $host, 180 );
	}

	/**
	 * Classify approved search referrers.
	 *
	 * @param string $host Hostname.
	 * @return string
	 */
	private static function referrer_channel( string $host ): string {
		$source = self::source_from_referrer( $host );

		return in_array( $source, array( 'google', 'bing', 'yahoo', 'duckduckgo' ), true ) ? 'organic_search' : 'referral';
	}

	/**
	 * Base64url encode data.
	 *
	 * @param string $value Value.
	 * @return string
	 */
	private static function base64url_encode( string $value ): string {
		return rtrim( strtr( base64_encode( $value ), '+/', '-_' ), '=' ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_encode -- Required for a signed compact cookie token.
	}

	/**
	 * Base64url decode data.
	 *
	 * @param string $value Value.
	 * @return string|false
	 */
	private static function base64url_decode( string $value ) {
		$padding = strlen( $value ) % 4;

		if ( $padding ) {
			$value .= str_repeat( '=', 4 - $padding );
		}

		return base64_decode( strtr( $value, '-_', '+/' ), true ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_decode -- Decodes the signed compact cookie token.
	}
}
