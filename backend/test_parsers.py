import os
import sys
import unittest


sys.path.insert(0, os.path.dirname(__file__))

from main import parse_line_chat, parse_whatsapp_chat


class ChatParserTests(unittest.TestCase):
    def test_line_chat_parses_dated_tab_format(self):
        chat_content = "\n".join([
            "分析対象: Bob",
            "2026/06/16 09:12\tAlice\tAre you free this weekend?",
            "2026/06/16 09:13\tBob\tI want to visit a coffee roaster.",
            "Maybe buy some beans too.",
        ])

        target_person, analysis_text = parse_line_chat(chat_content)

        self.assertEqual(target_person, "Bob")
        self.assertIn("I want to visit a coffee roaster. Maybe buy some beans too.", analysis_text)
        self.assertNotIn("Are you free this weekend?", analysis_text)

    def test_whatsapp_chat_parses_mobile_export_format(self):
        chat_content = "\n".join([
            "分析対象: Bob",
            "6/16/26, 9:12 AM - Alice: Are you free this weekend?",
            "6/16/26, 9:13 AM - Bob: I need a new sketchbook.",
        ])

        target_person, analysis_text = parse_whatsapp_chat(chat_content)

        self.assertEqual(target_person, "Bob")
        self.assertIn("I need a new sketchbook.", analysis_text)
        self.assertNotIn("Are you free this weekend?", analysis_text)

    def test_line_debug_logs_do_not_include_message_content(self):
        chat_content = "\n".join([
            "09:10\tAlice\tsecret alice message",
            "09:11\tBob\tsecret bob message",
            "09:12\tCarol\tsecret carol message",
        ])

        with self.assertLogs("main", level="DEBUG") as logs:
            with self.assertRaises(ValueError):
                parse_line_chat(chat_content)

        log_output = "\n".join(logs.output)
        self.assertNotIn("secret alice message", log_output)
        self.assertNotIn("secret bob message", log_output)
        self.assertNotIn("secret carol message", log_output)


if __name__ == "__main__":
    unittest.main()
