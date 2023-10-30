from tests.QtTestCase import QtTestCase
from urh.controller.dialogs.FilterBandwidthDialog import FilterBandwidthDialog
from urh.signalprocessing.Filter import Filter


class TestFilterBandwidthDialog(QtTestCase):
    def setUp(self):
        super().setUp()
        self.dialog = FilterBandwidthDialog()

    def test_change_custom_bw(self):
        bw = 0.3
        N = Filter.get_filter_length_from_bandwidth(bw)
        self.dialog.ui.doubleSpinBoxCustomBandwidth.setValue(bw)
        self.assertEqual(N, self.dialog.ui.spinBoxCustomKernelLength.value())

        N = 401
        bw = Filter.get_bandwidth_from_filter_length(N)
        self.dialog.ui.spinBoxCustomKernelLength.setValue(N)
        self.assertAlmostEqual(
            bw,
            self.dialog.ui.doubleSpinBoxCustomBandwidth.value(),
            places=self.dialog.ui.doubleSpinBoxCustomBandwidth.decimals(),
        )
