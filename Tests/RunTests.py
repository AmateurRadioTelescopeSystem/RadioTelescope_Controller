import unittest
import Tests.test_astronomy


if __name__ == "__main__":
    run = unittest.TextTestRunner()
    run.run(Tests.test_astronomy.TestConversions())
