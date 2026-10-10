import unittest

from app.qualification import MAX_LOAN_AMOUNT, QualificationEngine


def eligible_facts(**overrides):
    facts = {
        "property_type": "residential",
        "ownership_status": "sole",
        "documents_available": True,
        "loan_amount": 5_000_000,
        "occupation": "salaried",
        "income_mode": "bank",
        "market_value": 10_000_000,
        "tenure_years": 10,
    }
    facts.update(overrides)
    return facts


class QualificationEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = QualificationEngine()
        self.engine.create_session("test-call")
        self.engine.process_turn("test-call", customer_verified=True)

    def turn(self, facts=None, **kwargs):
        return self.engine.process_turn("test-call", facts=facts or {}, **kwargs)

    def test_happy_path_qualifies_only_after_all_seven_items(self):
        state = self.turn(eligible_facts())
        self.assertEqual(state.terminal_outcome, "QUALIFIED_FOR_EXPERT_FOLLOWUP")
        self.assertTrue(state.qualified)

    def test_each_disqualifier_ends_immediately(self):
        cases = [
            ({"property_type": "agricultural"}, "AGRICULTURAL_PROPERTY"),
            ({"documents_available": False}, "ORIGINAL_DOCUMENTS_UNAVAILABLE"),
            ({"income_mode": "cash"}, "CASH_INCOME"),
            ({"tenure_years": 2}, "TENURE_OUT_OF_RANGE"),
            ({"tenure_years": 16}, "TENURE_OUT_OF_RANGE"),
        ]
        for override, expected_reason in cases:
            with self.subTest(override=override):
                engine = QualificationEngine()
                engine.create_session("call")
                engine.process_turn("call", customer_verified=True)
                state = engine.process_turn("call", facts=eligible_facts(**override))
                self.assertEqual(state.terminal_outcome, "DISQUALIFIED")
                self.assertEqual(state.events[-1]["reason"], expected_reason)

    def test_joint_ownership_is_eligible(self):
        state = self.turn(eligible_facts(ownership_status="joint"))
        self.assertEqual(state.terminal_outcome, "QUALIFIED_FOR_EXPERT_FOLLOWUP")

    def test_market_value_has_no_minimum_threshold(self):
        state = self.turn(eligible_facts(market_value=1))
        self.assertEqual(state.terminal_outcome, "QUALIFIED_FOR_EXPERT_FOLLOWUP")

    def test_over_cap_requires_explicit_acceptance(self):
        state = self.turn({"loan_amount": 9_000_000})
        self.assertTrue(state.awaiting_maximum_acceptance)
        self.assertIsNone(state.terminal_outcome)
        state = self.turn(accept_maximum=True)
        self.assertEqual(state.loan_amount, MAX_LOAN_AMOUNT)
        self.assertEqual(state.terminal_outcome, "QUALIFIED_FOR_EXPERT_FOLLOWUP")

    def test_over_cap_decline_ends_call(self):
        self.turn({"loan_amount": 9_000_000})
        state = self.turn(accept_maximum=False)
        self.assertEqual(state.terminal_outcome, "CUSTOMER_DECLINED_MAXIMUM")

    def test_out_of_order_facts_are_saved_and_not_reasked(self):
        state = self.turn({
            "property_type": "residential",
            "ownership_status": "joint",
            "market_value": 12_000_000,
        })
        self.assertEqual(state.last_action, "ASK_NEXT_QUESTION")
        self.assertIn("original property documents", state.last_message.lower())
        self.assertEqual(state.ownership_status, "joint")
        self.assertEqual(state.market_value, 12_000_000)

    def test_busy_customer_gets_callback_and_terminal_outcome(self):
        state = self.turn(customer_busy=True, callback_time="tomorrow at 10 AM")
        self.assertEqual(state.terminal_outcome, "CALLBACK_REQUESTED")
        self.assertEqual(state.callback_time, "tomorrow at 10 AM")

    def test_transfer_case_ends_without_qualification(self):
        state = self.turn(existing_property_loan=True)
        self.assertEqual(state.terminal_outcome, "TRANSFER_SPECIALIST_FOLLOWUP")
        self.assertFalse(state.qualified)

    def test_emi_reduction_case_ends_without_qualification(self):
        state = self.turn(emi_reduction_request=True)
        self.assertEqual(state.terminal_outcome, "TRANSFER_SPECIALIST_FOLLOWUP")

    def test_wrong_customer_is_terminal(self):
        engine = QualificationEngine()
        engine.create_session("call")
        state = engine.process_turn("call", customer_verified=False)
        self.assertEqual(state.terminal_outcome, "WRONG_CUSTOMER")

    def test_terminal_session_cannot_be_reopened(self):
        state = self.turn(eligible_facts(property_type="agricultural"))
        snapshot = state.to_dict()
        state2 = self.turn(eligible_facts())
        self.assertEqual(state2.to_dict(), snapshot)
        self.assertEqual(state2.terminal_outcome, "DISQUALIFIED")

    def test_unknown_facts_do_not_default_to_eligible(self):
        state = self.turn({"property_type": "residential"})
        self.assertIsNone(state.terminal_outcome)
        self.assertEqual(state.last_action, "ASK_NEXT_QUESTION")

    def test_invalid_fact_values_are_rejected(self):
        with self.assertRaises(ValueError):
            self.turn({"property_type": "farmhouse-but-unknown-category"})

    def test_exact_boundaries_are_eligible(self):
        for years in (3, 15):
            with self.subTest(years=years):
                engine = QualificationEngine()
                engine.create_session("call")
                engine.process_turn("call", customer_verified=True)
                state = engine.process_turn("call", facts=eligible_facts(tenure_years=years))
                self.assertEqual(state.terminal_outcome, "QUALIFIED_FOR_EXPERT_FOLLOWUP")

    def test_amount_at_cap_is_eligible(self):
        state = self.turn(eligible_facts(loan_amount=MAX_LOAN_AMOUNT))
        self.assertEqual(state.terminal_outcome, "QUALIFIED_FOR_EXPERT_FOLLOWUP")


if __name__ == "__main__":
    unittest.main()
