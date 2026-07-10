<?php
/**
 * Read-only CEFA attribution shadow report for WP-CLI eval-file.
 *
 * Usage:
 * wp eval-file tools/wp-shadow-parity-report.php 4 '2026-07-10 00:00:00' 500
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Normalize one attribution value for parity comparison.
 *
 * @param string $semantic_key Attribution semantic key.
 * @param mixed  $value        Candidate value.
 * @return string
 */
function cefa_ct_shadow_normalize_value( string $semantic_key, $value ): string {
	$value = trim( sanitize_text_field( (string) $value ) );

	if ( preg_match( '/(?:source|medium|channel)/', $semantic_key ) ) {
		return strtolower( $value );
	}

	return $value;
}

/**
 * Classify one core paid-attribution comparison without returning raw values.
 *
 * Context URLs are excluded because the canonical shadow starts on deployment,
 * while old browser fields can predate it. A legacy click-family value is also
 * excluded when canonical attribution selected a different current click ID.
 *
 * @param string $semantic_key Attribution semantic key.
 * @param mixed  $legacy       Existing form value.
 * @param mixed  $canonical    Canonical value.
 * @return string `skip`, `match`, or `mismatch`.
 */
function cefa_ct_shadow_core_comparison( string $semantic_key, $legacy, $canonical ): string {
	if ( preg_match( '/(?:landing|referrer)/', $semantic_key ) ) {
		return 'skip';
	}

	$legacy    = cefa_ct_shadow_normalize_value( $semantic_key, $legacy );
	$canonical = cefa_ct_shadow_normalize_value( $semantic_key, $canonical );
	$click_ids = array( 'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid' );

	if ( in_array( $semantic_key, $click_ids, true ) && '' === $canonical ) {
		return 'skip';
	}

	if ( '' === $legacy && '' === $canonical ) {
		return 'skip';
	}

	return hash_equals( $canonical, $legacy ) ? 'match' : 'mismatch';
}

if ( ! defined( 'WP_CLI' ) || ! WP_CLI ) {
	return;
}

if ( ! class_exists( 'GFAPI' ) || ! class_exists( 'CEFA_Conversion_Tracking_Config' ) ) {
	WP_CLI::error( 'Gravity Forms and CEFA Conversion Tracking must be active.' );
}

$report_args = isset( $args ) && is_array( $args ) ? $args : array();
$form_id     = isset( $report_args[0] ) ? max( 1, (int) $report_args[0] ) : 4;
$start_date  = isset( $report_args[1] ) ? sanitize_text_field( (string) $report_args[1] ) : gmdate( 'Y-m-d 00:00:00' );
$page_size   = isset( $report_args[2] ) ? min( 1000, max( 1, (int) $report_args[2] ) ) : 500;
$form_config = CEFA_Conversion_Tracking_Config::form_config( $form_id );

if ( empty( $form_config ) ) {
	WP_CLI::error( 'The requested form is not configured for the current hostname.' );
}

$entries = GFAPI::get_entries(
	$form_id,
	array(
		'status'     => 'active',
		'start_date' => $start_date,
	),
	array(
		'key'        => 'date_created',
		'direction'  => 'ASC',
		'is_numeric' => false,
	),
	array(
		'offset'    => 0,
		'page_size' => $page_size,
	)
);

if ( is_wp_error( $entries ) ) {
	WP_CLI::error( $entries->get_error_message() );
}

$field_map  = is_array( $form_config['attribution_fields'] ?? null ) ? $form_config['attribution_fields'] : array();
$summary    = array(
	'generated_at_utc'               => gmdate( 'c' ),
	'form_id'                        => $form_id,
	'start_date_utc'                 => $start_date,
	'entry_count'                    => count( $entries ),
	'attribution_present'            => 0,
	'expected_direct_without_attr'   => 0,
	'unexpected_attribution_missing' => 0,
	'server_id_count'                => 0,
	'unique_server_id_count'         => 0,
	'identity_statuses'              => array(),
	'ledger_capture_count'           => 0,
	'ledger_statuses'                => array(),
	'writeback_statuses'             => array(),
	'channels'                       => array(),
	'paid_entry_count'               => 0,
	'paid_raw_checked'               => 0,
	'paid_raw_matched'               => 0,
	'paid_raw_parity'                => null,
	'paid_core_checked'              => 0,
	'paid_core_matched'              => 0,
	'paid_core_parity'               => null,
	'paid_core_issue_keys'           => array(),
	'delivery_note_types'            => array(),
);
$server_ids = array();
$entry_ids  = array();

foreach ( $entries as $entry ) {
	$entry_id    = (int) rgar( $entry, 'id' );
	$entry_ids[] = $entry_id;
	$server_id   = (string) gform_get_meta( $entry_id, 'cefa_conversion_tracking_server_event_id' );
	$identity    = (string) gform_get_meta( $entry_id, 'cefa_conversion_tracking_identity_status' );
	$capture_id  = (string) gform_get_meta( $entry_id, 'cefa_conversion_tracking_capture_id' );
	$ledger      = sanitize_key( (string) gform_get_meta( $entry_id, 'cefa_conversion_tracking_ledger_status' ) );
	$writeback   = sanitize_key( (string) gform_get_meta( $entry_id, 'cefa_conversion_tracking_writeback_status' ) );

	if ( '' !== $server_id ) {
		++$summary['server_id_count'];
		$server_ids[ $server_id ] = true;
	}

	if ( '' !== $identity ) {
		$summary['identity_statuses'][ $identity ] = ( $summary['identity_statuses'][ $identity ] ?? 0 ) + 1;
	}

	if ( '' !== $capture_id ) {
		++$summary['ledger_capture_count'];
	}

	if ( '' !== $ledger ) {
		$summary['ledger_statuses'][ $ledger ] = ( $summary['ledger_statuses'][ $ledger ] ?? 0 ) + 1;
	}

	if ( '' !== $writeback ) {
		$summary['writeback_statuses'][ $writeback ] = ( $summary['writeback_statuses'][ $writeback ] ?? 0 ) + 1;
	}

	$encoded  = (string) gform_get_meta( $entry_id, 'cefa_conversion_tracking_attribution_v1' );
	$envelope = '' !== $encoded ? json_decode( $encoded, true ) : null;

	if ( ! is_array( $envelope ) ) {
		$acquisition_fields = 0;

		foreach ( $field_map as $semantic_key => $field_id ) {
			if ( preg_match( '/(?:landing|referrer)/', (string) $semantic_key ) ) {
				continue;
			}

			if ( '' !== trim( (string) rgar( $entry, (string) $field_id ) ) ) {
				++$acquisition_fields;
			}
		}

		if ( 0 === $acquisition_fields ) {
			++$summary['expected_direct_without_attr'];
		} else {
			++$summary['unexpected_attribution_missing'];
		}

		continue;
	}

	++$summary['attribution_present'];
	$last_touch = is_array( $envelope['last_non_direct_touch'] ?? null ) ? $envelope['last_non_direct_touch'] : array();
	$click_ids  = is_array( $envelope['click_ids'] ?? null ) ? $envelope['click_ids'] : array();
	$channel    = sanitize_key( (string) ( $last_touch['channel'] ?? 'unknown' ) );
	$is_paid    = 0 === strpos( $channel, 'paid_' ) || ! empty( $click_ids );

	$summary['channels'][ $channel ] = ( $summary['channels'][ $channel ] ?? 0 ) + 1;

	if ( ! $is_paid ) {
		continue;
	}

	++$summary['paid_entry_count'];
	$parity = json_decode( (string) gform_get_meta( $entry_id, 'cefa_conversion_tracking_attribution_parity_v1' ), true );

	if ( is_array( $parity ) ) {
		$summary['paid_raw_checked'] += (int) ( $parity['checked_count'] ?? 0 );
		$summary['paid_raw_matched'] += (int) ( $parity['matched_count'] ?? 0 );
	}

	$canonical = CEFA_Conversion_Tracking_Attribution::canonical_compatibility_values( $envelope, $form_config );

	foreach ( $field_map as $semantic_key => $field_id ) {
		$result = cefa_ct_shadow_core_comparison(
			(string) $semantic_key,
			rgar( $entry, (string) $field_id ),
			$canonical[ $semantic_key ] ?? ''
		);

		if ( 'skip' === $result ) {
			continue;
		}

		++$summary['paid_core_checked'];

		if ( 'match' === $result ) {
			++$summary['paid_core_matched'];
		} else {
			$summary['paid_core_issue_keys'][ $semantic_key ] = ( $summary['paid_core_issue_keys'][ $semantic_key ] ?? 0 ) + 1;
		}
	}
}

$summary['unique_server_id_count'] = count( $server_ids );

if ( $summary['paid_raw_checked'] > 0 ) {
	$summary['paid_raw_parity'] = round( $summary['paid_raw_matched'] / $summary['paid_raw_checked'], 4 );
}

if ( $summary['paid_core_checked'] > 0 ) {
	$summary['paid_core_parity'] = round( $summary['paid_core_matched'] / $summary['paid_core_checked'], 4 );
}

if ( ! empty( $entry_ids ) ) {
	$notes = GFAPI::get_notes( array( 'entry_id' => $entry_ids ) );

	foreach ( is_array( $notes ) ? $notes : array() as $note ) {
		$note_type = sanitize_key( (string) ( $note->note_type ?? '' ) );
		$sub       = sanitize_key( (string) ( $note->sub_type ?? '' ) );
		$key       = $note_type . ( '' !== $sub ? '|' . $sub : '' );

		if ( '' !== $key ) {
			$summary['delivery_note_types'][ $key ] = ( $summary['delivery_note_types'][ $key ] ?? 0 ) + 1;
		}
	}
}

foreach ( array( 'identity_statuses', 'ledger_statuses', 'writeback_statuses', 'channels', 'paid_core_issue_keys', 'delivery_note_types' ) as $key ) {
	ksort( $summary[ $key ] );
}

WP_CLI::line( wp_json_encode( $summary, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) );
