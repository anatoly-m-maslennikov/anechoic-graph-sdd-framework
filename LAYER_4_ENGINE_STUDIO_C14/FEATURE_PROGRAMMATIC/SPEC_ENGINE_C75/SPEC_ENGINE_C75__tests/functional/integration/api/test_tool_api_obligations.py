import unittest


class ToolApiObligationTests(unittest.TestCase):
    def test_inconsistent_branches_return_source_linked_report(self):
        from ._tool_api_response_cases import check_source_linked_conflict

        check_source_linked_conflict(self)

    def test_inconsistent_error_fields_remain_visible_without_other_outcome(
        self,
    ):
        from ._tool_api_response_cases import check_inconsistent_error_fields

        check_inconsistent_error_fields(self)

    def test_partial_outcomes_keep_conflicts_and_incomplete_evidence(self):
        from ._tool_api_response_cases import check_partial_outcome_evidence

        check_partial_outcome_evidence(self)

    def test_partial_outcome_compares_known_fields_against_contract(self):
        from ._tool_api_terminal_cases import check_partial_contract_outcome

        check_partial_contract_outcome(self)

    def test_public_comparison_covers_each_terminal_branch(self):
        from ._tool_api_terminal_cases import check_terminal_branches

        check_terminal_branches(self)

    def test_unclassified_failure_keeps_format_disagreement(self):
        from ._tool_api_terminal_cases import check_unclassified_failure

        check_unclassified_failure(self)

    def test_public_delivery_and_internal_message_require_each_branch(self):
        from ._tool_api_delivery_cases import check_public_delivery

        check_public_delivery(self)

    def test_unclassified_terminal_in_public_formal_chain(self):
        from ._tool_api_delivery_cases import check_unclassified_terminal

        check_unclassified_terminal(self)

    def test_selects_profile_with_inconsistent_operation(self):
        from ._tool_api_query_cases import check_inconsistent_operation

        check_inconsistent_operation(self)

    def test_query_evidence_covers_each_reachable_success_path(self):
        from ._tool_api_query_cases import check_query_evidence

        check_query_evidence(self)

    def test_explicit_facts_and_missing_or_contradictory_evidence(self):
        from ._tool_api_query_cases import check_explicit_facts

        check_explicit_facts(self)
