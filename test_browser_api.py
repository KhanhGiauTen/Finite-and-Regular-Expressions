import itertools
import json
import re
import unittest
from browser_api import run_public


class BrowserTests(unittest.TestCase):
    def run_engine(self, expression, text):
        return json.loads(run_public(json.dumps({"regex": expression, "text": text})))

    def test_acceptance_matches_reference(self):
        for expression in ["(a+b)*abb", "a*b*", "a+E", "(ab)*", "a.(a+b)"]:
            reference = expression.replace("+", "|").replace("E", "").replace(".", "\\.")
            for length in range(5):
                for symbols in itertools.product("ab.", repeat=length):
                    text = "".join(symbols)
                    self.assertEqual(self.run_engine(expression, text)["accepted"],
                                     re.fullmatch(reference, text) is not None)

    def test_trace_and_empty_string(self):
        result = self.run_engine("(a+b)*abb", "aabb")
        self.assertTrue(result["accepted"])
        self.assertEqual(len(result["trace"]), 5)
        self.assertTrue(self.run_engine("E", "")["accepted"])

    def test_invalid_syntax(self):
        for expression in ["", "a+", "(a", "a)", "()", "*a", "a++b", "a|b", "abcde"]:
            with self.assertRaises(ValueError):
                self.run_engine(expression, "a")

    def test_unknown_symbol_is_rejected(self):
        result = self.run_engine("a*", "z")
        self.assertFalse(result["accepted"])
        self.assertIsNone(result["trace"][-1]["state"])

    def test_input_bounds(self):
        with self.assertRaises(ValueError):
            self.run_engine("a*", "a" * 129)
        with self.assertRaises(ValueError):
            run_public('{"regex":"a","text":"a","code":"x"}')


if __name__ == "__main__":
    unittest.main()
