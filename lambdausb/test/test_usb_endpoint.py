import unittest

from ..usb.endpoint import *


class InputEndpointTestCase(unittest.TestCase):
    def test_simple(self):
        ep = InputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        self.assertEqual(ep.xfer, Transfer.CONTROL)
        self.assertEqual(ep.max_size, 64)

    def test_wrong_xfer(self):
        with self.assertRaisesRegex(TypeError,
                r"Transfer type must be an instance of Transfer, not 'foo'"):
            ep = InputEndpoint(xfer="foo", max_size=64)

    def test_wrong_size(self):
        with self.assertRaisesRegex(ValueError,
                r"Maximum packet size must be a positive integer, not 'foo'"):
            ep = InputEndpoint(xfer=Transfer.CONTROL, max_size="foo")
        with self.assertRaisesRegex(ValueError,
                r"Maximum packet size must be a positive integer, not -1"):
            ep = InputEndpoint(xfer=Transfer.CONTROL, max_size=-1)

    def test_wrong_size_isochronous(self):
        with self.assertRaisesRegex(ValueError,
                r"Invalid maximum packet size 1025; must be lesser than or equal to 1024 for an "
                r"isochronous endpoint"):
            ep = InputEndpoint(xfer=Transfer.ISOCHRONOUS, max_size=1025)

    def test_wrong_size_control(self):
        with self.assertRaisesRegex(ValueError,
                r"Invalid maximum packet size 65; must be lesser than or equal to 64 for a "
                r"control endpoint"):
            ep = InputEndpoint(xfer=Transfer.CONTROL, max_size=65)

    def test_wrong_size_bulk(self):
        with self.assertRaisesRegex(ValueError,
                r"Invalid maximum packet size 513; must be lesser than or equal to 512 for a "
                r"bulk endpoint"):
            ep = InputEndpoint(xfer=Transfer.BULK, max_size=513)

    def test_wrong_size_interrupt(self):
        with self.assertRaisesRegex(ValueError,
                r"Invalid maximum packet size 1025; must be lesser than or equal to 1024 for an "
                r"interrupt endpoint"):
            ep = InputEndpoint(xfer=Transfer.INTERRUPT, max_size=1025)


class OutputEndpointTestCase(unittest.TestCase):
    def test_simple(self):
        ep = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        self.assertEqual(ep.xfer, Transfer.CONTROL)
        self.assertEqual(ep.max_size, 64)

    def test_wrong_xfer(self):
        with self.assertRaisesRegex(TypeError,
                r"Transfer type must be an instance of Transfer, not 'foo'"):
            ep = OutputEndpoint(xfer="foo", max_size=64)

    def test_wrong_size(self):
        with self.assertRaisesRegex(ValueError,
                r"Maximum packet size must be a positive integer, not 'foo'"):
            ep = OutputEndpoint(xfer=Transfer.CONTROL, max_size="foo")
        with self.assertRaisesRegex(ValueError,
                r"Maximum packet size must be a positive integer, not -1"):
            ep = OutputEndpoint(xfer=Transfer.CONTROL, max_size=-1)

    def test_wrong_size_isochronous(self):
        with self.assertRaisesRegex(ValueError,
                r"Invalid maximum packet size 1025; must be lesser than or equal to 1024 for an "
                r"isochronous endpoint"):
            ep = OutputEndpoint(xfer=Transfer.ISOCHRONOUS, max_size=1025)

    def test_wrong_size_control(self):
        with self.assertRaisesRegex(ValueError,
                r"Invalid maximum packet size 65; must be lesser than or equal to 64 for a "
                r"control endpoint"):
            ep = OutputEndpoint(xfer=Transfer.CONTROL, max_size=65)

    def test_wrong_size_bulk(self):
        with self.assertRaisesRegex(ValueError,
                r"Invalid maximum packet size 513; must be lesser than or equal to 512 for a "
                r"bulk endpoint"):
            ep = OutputEndpoint(xfer=Transfer.BULK, max_size=513)

    def test_wrong_size_interrupt(self):
        with self.assertRaisesRegex(ValueError,
                r"Invalid maximum packet size 1025; must be lesser than or equal to 1024 for an "
                r"interrupt endpoint"):
            ep = OutputEndpoint(xfer=Transfer.INTERRUPT, max_size=1025)

    def test_setup(self):
        ep_0 = OutputEndpoint(xfer=Transfer.CONTROL, max_size=64)
        ep_1 = OutputEndpoint(xfer=Transfer.BULK,    max_size=64)
        self.assertEqual(ep_0.setup.width, 1)
        self.assertEqual(ep_1.setup.width, 0)
