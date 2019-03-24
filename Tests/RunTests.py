import unittest
import Tests.Astronomy


if __name__ == "__main__":
    run = unittest.TextTestRunner()
    run.run(Tests.Astronomy.TestConversions())
