from __future__ import annotations

import unittest

from parent_activation.greenrope_adapter import (
    GreenRopeClient,
    evaluate_required_fields,
    parse_field_dictionary,
    parse_phase_dictionary,
    parse_phase_paths,
)


class GreenRopeDictionaryTests(unittest.TestCase):
    def test_required_identity_fields_block_readiness_when_absent(self) -> None:
        readiness = evaluate_required_fields({"UTM Source", "gclid"})
        self.assertEqual("blocked", readiness.status)
        self.assertEqual(frozenset({"cefaeventid", "cefaformentryid"}), readiness.missing)

    def test_field_dictionary_normalizes_labels_and_unblocks_exact_contract(self) -> None:
        payload = {
            "GetOpportunityFieldsResponse": {
                "fields": {
                    "field": [
                        {"field_id": "1", "fieldname": "CEFA Event ID", "fieldtype": "text"},
                        {"field_id": "2", "fieldname": "CEFA_Form Entry ID", "fieldtype": "text"},
                    ]
                }
            }
        }
        fields = parse_field_dictionary(payload)
        self.assertEqual(["cefaeventid", "cefaformentryid"], [field.normalized_label for field in fields])
        self.assertEqual("ready", evaluate_required_fields(field.normalized_label for field in fields).status)

    def test_phase_and_path_dictionaries_extract_metadata_only(self) -> None:
        phases = parse_phase_dictionary(
            {"GetPhasesResponse": {"phases": {"phase": {"phase_id": "10", "phasename": "Tour Scheduled"}}}}
        )
        paths = parse_phase_paths(
            {
                "GetPhasePathsResponse": {
                    "paths": {"path": {"phase_path_id": "20", "from_phase_id": "9", "to_phase_id": "10"}}
                }
            }
        )
        self.assertEqual("tourscheduled", phases[0].normalized_label)
        self.assertEqual("9", paths[0].from_phase_id)
        self.assertEqual("10", paths[0].to_phase_id)

    def test_client_uses_only_dictionary_requests(self) -> None:
        requests: list[str] = []

        def transport(request: object, _: int) -> dict[str, object]:
            body = request.data.decode("utf-8")  # type: ignore[attr-defined]
            requests.append(body)
            if "GetOpportunityFieldsRequest" in body:
                return {"GetOpportunityFieldsResponse": {"fields": {"field": []}}}
            if "GetPhasesRequest" in body:
                return {"GetPhasesResponse": {"phases": {"phase": []}}}
            return {"GetPhasePathsResponse": {"paths": {"path": []}}}

        client = GreenRopeClient("https://example.invalid", "email", "token", "account", transport=transport)
        client.opportunity_fields()
        client.phases()
        client.phase_paths()
        self.assertEqual(3, len(requests))
        self.assertTrue(all("Request" in request for request in requests))
        self.assertFalse(any("Create" in request or "Update" in request or "Delete" in request for request in requests))


if __name__ == "__main__":
    unittest.main()
