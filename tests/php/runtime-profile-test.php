<?php
/**
 * Runtime-profile coexistence contract tests.
 *
 * @package CEFA_Conversion_Tracking
 */

define( 'ABSPATH', __DIR__ . '/' );

$GLOBALS['cefa_test_actions'] = array();
$GLOBALS['cefa_test_filters'] = array();

function add_action( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
	$GLOBALS['cefa_test_actions'][] = compact( 'hook', 'callback', 'priority', 'accepted_args' );
}

function add_filter( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
	$GLOBALS['cefa_test_filters'][] = compact( 'hook', 'callback', 'priority', 'accepted_args' );
}

function rgar( $array, $key ) {
	return is_array( $array ) && array_key_exists( $key, $array ) ? $array[ $key ] : null;
}

final class CEFA_Conversion_Tracking_Config {
	public static $profile = 'attribution_only';

	public static function runtime_profile() {
		return self::$profile;
	}

	public static function active_form_ids() {
		return array( 1, 2 );
	}

	public static function form_config( $form_id ) {
		return in_array( $form_id, array( 1, 2 ), true ) ? array( 'id' => $form_id ) : array();
	}
}

final class CEFA_Conversion_Tracking_Entry_Attribution {
	public static $calls = 0;

	public static function persist_after_submission( $entry, $form_config ) {
		unset( $form_config );
		++self::$calls;
		$entry['canonical_saved'] = true;
		return $entry;
	}
}

final class CEFA_Conversion_Tracking_Attribution_Parity {
	public static $calls               = 0;
	public static $received_canonical  = false;

	public static function persist_after_submission( $entry, $form_config ) {
		unset( $form_config );
		++self::$calls;
		self::$received_canonical = ! empty( $entry['canonical_saved'] );
		return $entry;
	}
}

require_once dirname( __DIR__, 2 ) . '/includes/class-cefa-conversion-tracking.php';

function cefa_runtime_assert( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message );
	}
}

CEFA_Conversion_Tracking::init();

$action_hooks = array_column( $GLOBALS['cefa_test_actions'], 'hook' );
$filter_hooks = array_column( $GLOBALS['cefa_test_filters'], 'hook' );

cefa_runtime_assert( in_array( 'gform_after_submission_1', $action_hooks, true ), 'Form 1 attribution-only persistence hook is missing.' );
cefa_runtime_assert( in_array( 'gform_after_submission_2', $action_hooks, true ), 'Form 2 attribution-only persistence hook is missing.' );
cefa_runtime_assert( ! in_array( 'gform_pre_submission_1', $action_hooks, true ), 'Attribution-only mode registered a pre-submission event hook.' );
cefa_runtime_assert( ! in_array( 'gform_confirmation_1', $filter_hooks, true ), 'Attribution-only mode registered a confirmation event hook.' );

foreach ( $GLOBALS['cefa_test_actions'] as $action ) {
	if ( 0 === strpos( $action['hook'], 'gform_after_submission_' ) ) {
		cefa_runtime_assert(
			array( 'CEFA_Conversion_Tracking', 'persist_attribution_only' ) === $action['callback'],
			'Attribution-only mode registered the full conversion callback.'
		);
	}
	cefa_runtime_assert(
		array( 'CEFA_Conversion_Tracking_Event_ID_Registry', 'maybe_install' ) !== $action['callback'],
		'Attribution-only mode registered the event-ID registry.'
	);
}

CEFA_Conversion_Tracking::persist_attribution_only(
	array( 'id' => 10, 'status' => 'active' ),
	array( 'id' => 1 )
);
cefa_runtime_assert( 1 === CEFA_Conversion_Tracking_Entry_Attribution::$calls, 'Canonical attribution was not persisted.' );
cefa_runtime_assert( 1 === CEFA_Conversion_Tracking_Attribution_Parity::$calls, 'Parity evidence was not persisted.' );
cefa_runtime_assert( CEFA_Conversion_Tracking_Attribution_Parity::$received_canonical, 'Parity did not receive canonical entry metadata.' );

CEFA_Conversion_Tracking::persist_attribution_only(
	array( 'id' => 11, 'status' => 'spam' ),
	array( 'id' => 1 )
);
cefa_runtime_assert( 1 === CEFA_Conversion_Tracking_Entry_Attribution::$calls, 'Spam entry was persisted in attribution-only mode.' );

$GLOBALS['cefa_test_actions'] = array();
$GLOBALS['cefa_test_filters'] = array();
CEFA_Conversion_Tracking_Config::$profile = 'full';
CEFA_Conversion_Tracking::init();

$action_hooks = array_column( $GLOBALS['cefa_test_actions'], 'hook' );
$filter_hooks = array_column( $GLOBALS['cefa_test_filters'], 'hook' );

cefa_runtime_assert( in_array( 'gform_pre_submission_1', $action_hooks, true ), 'Full mode lost its pre-submission hook.' );
cefa_runtime_assert( in_array( 'gform_after_submission_1', $action_hooks, true ), 'Full mode lost its confirmed-submit hook.' );
cefa_runtime_assert( in_array( 'gform_confirmation_1', $filter_hooks, true ), 'Full mode lost its confirmation filter.' );

echo "Runtime profile tests passed.\n";
