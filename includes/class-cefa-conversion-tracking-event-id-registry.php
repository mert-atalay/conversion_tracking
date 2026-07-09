<?php
/**
 * Plugin-owned server event-ID reservation table.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Reserves immutable server event IDs before destination dispatch.
 */
final class CEFA_Conversion_Tracking_Event_ID_Registry {
	private const DB_VERSION        = '1';
	private const DB_VERSION_OPTION = 'cefa_ct_event_id_db_version';
	private const GENERATION_TRIES  = 10;

	/**
	 * Install the registry during plugin activation.
	 *
	 * @return void
	 */
	public static function activate(): void {
		self::install();
	}

	/**
	 * Install lazily only when the guarded bridge is enabled.
	 *
	 * @return void
	 */
	public static function maybe_install(): void {
		if ( 'off' === CEFA_Conversion_Tracking_Config::attribution_v2_mode() ) {
			return;
		}

		if ( self::DB_VERSION !== (string) get_option( self::DB_VERSION_OPTION, '' ) ) {
			self::install();
		}
	}

	/**
	 * Generate and atomically reserve a unique UUID.
	 *
	 * @param string $site_context Site context.
	 * @param int    $form_id      Form ID.
	 * @param int    $entry_id     Entry ID, or zero before save.
	 * @return string
	 */
	public static function generate_and_reserve( string $site_context, int $form_id, int $entry_id = 0 ): string {
		for ( $attempt = 0; $attempt < self::GENERATION_TRIES; ++$attempt ) {
			$event_id = wp_generate_uuid4();

			if ( self::reserve( $event_id, $site_context, $form_id, $entry_id ) ) {
				return $event_id;
			}
		}

		return '';
	}

	/**
	 * Reserve an existing UUID when a primary request resumes after save.
	 *
	 * @param string $event_id     Event ID.
	 * @param string $site_context Site context.
	 * @param int    $form_id      Form ID.
	 * @param int    $entry_id     Entry ID.
	 * @return bool
	 */
	public static function reserve( string $event_id, string $site_context, int $form_id, int $entry_id = 0 ): bool {
		global $wpdb;

		if ( ! isset( $wpdb ) || ! is_object( $wpdb ) || '' === CEFA_Conversion_Tracking_Event_ID::normalize_event_id( $event_id ) ) {
			return false;
		}

		$result = $wpdb->insert( // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery -- Atomic insert enforces the unique event-ID primary key.
			self::table_name(),
			array(
				'event_id'     => $event_id,
				'site_context' => sanitize_key( $site_context ),
				'form_id'      => $form_id,
				'entry_id'     => $entry_id,
				'created_at'   => current_time( 'mysql', true ),
			),
			array( '%s', '%s', '%d', '%d', '%s' )
		);

		return 1 === $result;
	}

	/**
	 * Attach the saved Gravity Forms entry to a pre-reserved ID.
	 *
	 * @param string $event_id Event ID.
	 * @param int    $entry_id Entry ID.
	 * @return bool
	 */
	public static function attach_entry( string $event_id, int $entry_id ): bool {
		global $wpdb;

		if ( ! isset( $wpdb ) || ! is_object( $wpdb ) || $entry_id < 1 ) {
			return false;
		}

		$result = $wpdb->update( // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery,WordPress.DB.DirectDatabaseQuery.NoCaching -- Registry identity updates must be durable and uncached.
			self::table_name(),
			array( 'entry_id' => $entry_id ),
			array( 'event_id' => $event_id ),
			array( '%d' ),
			array( '%s' )
		);

		return false !== $result;
	}

	/**
	 * Create or upgrade the reservation table.
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
			event_id char(36) NOT NULL,
			site_context varchar(32) NOT NULL,
			form_id bigint(20) unsigned NOT NULL,
			entry_id bigint(20) unsigned NOT NULL DEFAULT 0,
			created_at datetime NOT NULL,
			PRIMARY KEY  (event_id),
			KEY entry_id (entry_id),
			KEY form_entry (form_id, entry_id)
		) {$charset_collate};";

		dbDelta( $sql );
		update_option( self::DB_VERSION_OPTION, self::DB_VERSION, false );
	}

	/**
	 * Return the prefixed registry table name.
	 *
	 * @return string
	 */
	private static function table_name(): string {
		global $wpdb;

		return $wpdb->prefix . 'cefa_ct_event_ids';
	}
}
