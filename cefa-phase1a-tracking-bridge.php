<?php
/**
 * Plugin Name: CEFA Phase 1A Tracking Bridge
 * Plugin URI: https://github.com/mert-atalay/conversion_tracking
 * Description: Emits one clean school_inquiry_submit dataLayer event after confirmed Gravity Form 4 success.
 * Version: 0.1.0
 * Requires at least: 6.3
 * Requires PHP: 7.4
 * Author: CEFA
 * License: GPL-2.0-or-later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Update URI: https://github.com/mert-atalay/conversion_tracking
 * Text Domain: cefa-phase1a-tracking-bridge
 *
 * @package CEFA_Phase1A_Tracking_Bridge
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'CEFA_PHASE1A_TRACKING_BRIDGE_VERSION', '0.1.0' );
define( 'CEFA_PHASE1A_TRACKING_BRIDGE_FILE', __FILE__ );
define( 'CEFA_PHASE1A_TRACKING_BRIDGE_DIR', plugin_dir_path( __FILE__ ) );
define( 'CEFA_PHASE1A_TRACKING_BRIDGE_URL', plugin_dir_url( __FILE__ ) );
define( 'CEFA_PHASE1A_TRACKING_BRIDGE_FORM_ID', 4 );

require_once CEFA_PHASE1A_TRACKING_BRIDGE_DIR . 'includes/class-cefa-phase1a-tracking-bridge-event-id.php';
require_once CEFA_PHASE1A_TRACKING_BRIDGE_DIR . 'includes/class-cefa-phase1a-tracking-bridge-datalayer-payload.php';
require_once CEFA_PHASE1A_TRACKING_BRIDGE_DIR . 'includes/class-cefa-phase1a-tracking-bridge-duplicate-guard.php';
require_once CEFA_PHASE1A_TRACKING_BRIDGE_DIR . 'includes/class-cefa-phase1a-tracking-bridge-confirmation-payload.php';
require_once CEFA_PHASE1A_TRACKING_BRIDGE_DIR . 'includes/class-cefa-phase1a-tracking-bridge-rest-controller.php';
require_once CEFA_PHASE1A_TRACKING_BRIDGE_DIR . 'includes/class-cefa-phase1a-tracking-bridge.php';

CEFA_Phase1A_Tracking_Bridge::init();
