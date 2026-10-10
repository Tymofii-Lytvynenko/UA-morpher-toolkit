import unittest

from batch import InflectionRow, inflect_rows, parse_clipboard, results_to_clipboard


class ClipboardTests(unittest.TestCase):
    def test_one_column_names_and_blank_rows(self):
        self.assertEqual(
            parse_clipboard("Коваль Іван Іванович\r\n\r\nШевченко Анна Петрівна\r\n"),
            ["Коваль Іван Іванович", "", "Шевченко Анна Петрівна"],
        )

    def test_three_columns(self):
        self.assertEqual(
            parse_clipboard("Коваль\tІван\tІванович\nШевченко\tОлена\tПетрівна\tignored\n"),
            ["Коваль Іван Іванович", "Шевченко Олена Петрівна"],
        )

    def test_empty_clipboard(self):
        self.assertEqual(parse_clipboard(""), [])

    def test_retains_trailing_blank_data_row(self):
        self.assertEqual(parse_clipboard("Іваненко Петро Петрович\n\n"), ["Іваненко Петро Петрович", ""])


class BulkInflectionTests(unittest.TestCase):
    def test_inflection_preserves_position_and_blanks(self):
        seen = []

        def mock_morph(value, case, *, uppercase_surname):
            seen.append((value, case, uppercase_surname))
            return f"{case}/{value}"

        rows = inflect_rows(["А", "", "Б"], "gent", mock_morph, uppercase_surname=True)
        self.assertEqual(results_to_clipboard(rows), "gent/А\n\ngent/Б")
        self.assertEqual(seen, [("А", "gent", True), ("Б", "gent", True)])

    def test_failure_never_drops_entry(self):
        def fail(value, case, *, uppercase_surname):
            if value == "BAD":
                raise RuntimeError("Malformed row")
            return "OK"

        rows = inflect_rows(["GOOD", "BAD", "GOOD"], "datv", fail)
        self.assertEqual(len(rows), 3)
        self.assertEqual(results_to_clipboard(rows), "OK\nBAD\nOK")
        self.assertEqual(rows[1].error, "Malformed row")

    def test_invalid_case(self):
        with self.assertRaises(ValueError):
            inflect_rows(["А"], "invalid", lambda *args, **kwargs: "x")


if __name__ == "__main__":
    unittest.main()
