"""Check the VME encodings shared with LLVM's RISCVInstrFormatsV.td."""

import importlib.machinery
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
parser = importlib.machinery.SourceFileLoader(
    "parse_opcodes", str(ROOT / "parse_opcodes")
).load_module()
_, _, masks, matches, arguments = parser.parse_inputs([str(ROOT / "opcodes-vme")])


class VMEEncodingTest(unittest.TestCase):
    def test_msetmtypei(self):
        name = "msetmtypei"
        self.assertEqual(matches[name], 0x88407057)
        self.assertEqual(masks[name], 0xEE7E7FFF)
        self.assertEqual(arguments[name], ["altfmt", "vsew", "mtwiden"])
        self.assertEqual(parser.arglut["altfmt"], (28, 28))
        self.assertEqual(parser.arglut["vsew"], (24, 23))
        self.assertEqual(parser.arglut["mtwiden"], (16, 15))
        for altfmt in range(2):
            for vsew in range(4):
                for mtwiden in range(4):
                    word = (matches[name] | (altfmt << 28) |
                            (vsew << 23) | (mtwiden << 15))
                    self.assertEqual(word & masks[name], matches[name])
                    self.assertEqual((word >> 28) & 1, altfmt)
                    self.assertEqual((word >> 23) & 3, vsew)
                    self.assertEqual((word >> 15) & 3, mtwiden)

    def test_matrix_arithmetic(self):
        expected = {
            "vtfmm.tvv": 0xF2001077,
            "vtfmm.alt.tvv": 0xF20010F7,
            "vtmmu.tvv": 0xF2000077,
            "vtmms.tvv": 0xF20000F7,
        }
        for name, match in expected.items():
            with self.subTest(instruction=name):
                self.assertEqual(matches[name], match)
                self.assertEqual(masks[name], 0xFE0071FF)
                self.assertEqual(arguments[name], ["vs2", "vs1", "rdhi3"])
                for tile in range(0, 16, 2):
                    word = match | (31 << 20) | (17 << 15) | ((tile >> 1) << 9)
                    self.assertEqual(word & masks[name], match)
                    self.assertEqual((word >> 11) & 1, (tile >> 3) & 1)
                    self.assertEqual((word >> 8) & 0xF, tile)
                    self.assertNotEqual((word | (1 << 8)) & masks[name], match)


if __name__ == "__main__":
    unittest.main()
