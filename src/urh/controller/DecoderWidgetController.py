import copy
import os

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QDropEvent, QDragEnterEvent
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QGraphicsScene, QApplication

from urh import constants
from urh.SignalSceneManager import SignalSceneManager
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.signalprocessing.encoding import encoding
from urh.ui.CustomDialog import CustomDialog
from urh.ui.ui_decoding import Ui_Decoder
from urh.util.ProjectManager import ProjectManager


class DecoderWidgetController(QDialog):
    def __init__(self, decodings, signals, project_manager: ProjectManager,
                 parent=None):
        """
        :type decodings: list of encoding
        :type signals: list of Signal
        """
        # Init
        super().__init__(parent)
        self.ui = Ui_Decoder()
        self.ui.setupUi(self)

        # Variables
        self.old_inpt_txt = ""
        self.old_carrier_txt = ""
        self.old_decoderchain = []
        self.active_block = ""

        self.project_manager = project_manager

        # Initialize encoder
        self.decodings = decodings
        self.ui.combobox_decodings.clear()
        for decoding in self.decodings:
            self.ui.combobox_decodings.addItem(decoding.name)
        self.chainstr = []
        self.chainoptions = {}
        self.set_e()

        # Signals
        self.signals = signals if signals is not None else []
        for i in signals:
            self.ui.combobox_signals.addItem(i.name)

        # Function lists
        self.ui.basefunctions.addItem(constants.DECODING_EDGE)
        self.ui.basefunctions.addItem(constants.DECODING_SUBSTITUTION)
        self.ui.basefunctions.addItem(constants.DECODING_EXTERNAL)
        self.ui.additionalfunctions.addItem(constants.DECODING_INVERT)
        self.ui.additionalfunctions.addItem(constants.DECODING_DIFFERENTIAL)
        self.ui.additionalfunctions.addItem(constants.DECODING_BITORDER)
        self.ui.additionalfunctions.addItem(constants.DECODING_REDUNDANCY)
        self.ui.additionalfunctions.addItem(constants.DECODING_CARRIER)
        self.ui.additionalfunctions.addItem(constants.DECODING_DATAWHITENING)

        # Presets
        self.setWindowTitle("Decoding")
        self.setAcceptDrops(True)
        self.inpt_text = "10010110"
        self.ui.inpt.setText(self.inpt_text)
        self.ui.optionWidget.setCurrentIndex(0)
        self.decoder_update()

        self.ui.substitution.setColumnCount(2)
        self.ui.substitution.setRowCount(self.ui.substitution_rows.value())
        self.ui.substitution.setHorizontalHeaderLabels(['From', 'To'])
        self.ui.substitution.setColumnWidth(0, 190)
        self.ui.substitution.setColumnWidth(1, 190)

        self.ui.saveas.setVisible(False)

        # Connects
        self.create_connects()


    def create_connects(self):
        self.ui.inpt.textChanged.connect(self.decoder_update)
        self.ui.multiple.valueChanged.connect(self.handle_multiple_changed)
        self.ui.carrier.textChanged.connect(self.handle_carrier_changed)
        self.ui.substitution_rows.valueChanged.connect(self.handle_substitution_rows_changed)
        self.ui.substitution.itemChanged.connect(self.handle_substitution_changed)
        self.ui.external_decoder.textEdited.connect(self.handle_external)
        self.ui.external_encoder.textEdited.connect(self.handle_external)
        self.ui.datawhitening_sync.textEdited.connect(self.handle_datawhitening)
        self.ui.datawhitening_polynomial.textEdited.connect(self.handle_datawhitening)
        self.ui.datawhitening_applycrc.clicked.connect(self.handle_datawhitening)
        self.ui.datawhitening_preamble_rm.clicked.connect(self.handle_datawhitening)
        self.ui.datawhitening_sync_rm.clicked.connect(self.handle_datawhitening)
        self.ui.datawhitening_crc_rm.clicked.connect(self.handle_datawhitening)

        self.ui.decoderchain.itemChanged.connect(self.decoderchainUpdate)
        self.ui.decoderchain.internalMove.connect(self.decoderchainUpdate)
        self.ui.decoderchain.itemActivated.connect(self.setInformation)
        self.ui.decoderchain.deleteElement.connect(self.deleteElement)
        self.ui.basefunctions.itemActivated.connect(self.setInformation)
        self.ui.additionalfunctions.itemActivated.connect(self.setInformation)
        self.ui.combobox_decodings.currentIndexChanged.connect(self.set_e)
        self.ui.combobox_signals.currentIndexChanged.connect(self.set_signal)
        self.ui.saveas.clicked.connect(self.saveas)
        self.ui.delete_decoding.clicked.connect(self.delete_decoding)


    def save_to_file(self):
        if self.project_manager.project_file:
            prefix = os.path.realpath(os.path.dirname(
                self.project_manager.project_file))
        else:
            prefix = os.path.realpath(os.path.join(constants.SETTINGS.fileName(), ".."))

        f = open(os.path.join(prefix, constants.DECODINGS_FILE), "w")
        if not f:
            return

        for i in range(0, self.ui.combobox_decodings.count()):
            str = ""
            for j in self.decodings[i].get_chain():
                str += repr(j) + ", "
            str += "\n"
            f.write(str)

        f.close()

    def saveas(self):
        # Ask for a name
        txt = ["Please enter a name:", self.e.chain[0]]
        ok , name = CustomDialog.dialog(self, txt, "input")

        if ok and name != "":
            self.e.chain[0] = name
            self.decoderchainUpdate()

            # If name is already there, overwrite existing
            for i in range (0, len(self.decodings)):
                if name == self.decodings[i].name:
                    self.ui.combobox_decodings.setCurrentIndex(i)
                    self.decodings[i] = encoding(self.chainstr)
                    self.set_e()
                    self.ui.saveas.setVisible(False)
                    self.save_to_file()
                    return

            self.decodings.append(encoding(self.chainstr))
            self.ui.combobox_decodings.addItem(self.chainstr[0])
            self.ui.combobox_decodings.setCurrentIndex(self.ui.combobox_decodings.count()-1)
            self.set_e()
            self.save_to_file()


    def delete_decoding(self):
        num = self.ui.combobox_decodings.currentIndex()
        if num >= 0:
            # Ask for acknowledgement
            txt = "Do you really want to delete '" + self.decodings[num].name + "'?"
            ok , _ = CustomDialog.dialog(self, txt, "yesno")

            if ok:
                self.decodings.pop(num)
                self.ui.combobox_decodings.removeItem(num)
                self.save_to_file()


    def set_e(self):
        if self.ui.combobox_decodings.count() < 1: # Empty list
            return

        self.e = copy.deepcopy(self.decodings[self.ui.combobox_decodings.currentIndex()])
        """:type: encoding """
        chain = self.e.get_chain()
        self.ui.decoderchain.clear()
        self.chainoptions.clear()
        last_i = ""
        for i in chain:
            if i in [constants.DECODING_INVERT, constants.DECODING_DIFFERENTIAL, constants.DECODING_REDUNDANCY,
                     constants.DECODING_CARRIER, constants.DECODING_BITORDER, constants.DECODING_EDGE, constants.DECODING_DATAWHITENING,
                     constants.DECODING_SUBSTITUTION, constants.DECODING_EXTERNAL, constants.DECODING_DISABLED_PREFIX]:
                self.ui.decoderchain.addItem(i)
                self.decoderchainUpdate()
                last_i = self.ui.decoderchain.item(self.ui.decoderchain.count()-1).text()
            else:
                if any(x in last_i for x in [constants.DECODING_REDUNDANCY, constants.DECODING_CARRIER,
                                             constants.DECODING_SUBSTITUTION, constants.DECODING_EXTERNAL,
                                             constants.DECODING_DATAWHITENING]):
                    self.chainoptions[last_i] = i

        self.decoderchainUpdate()
        self.decoder_update()
        self.ui.saveas.setVisible(False)


    def decoderchainUpdate(self):
        # for i in range (0, self.ui.decoderchain.count()):
        #     print(i, "->", self.ui.decoderchain.item(i).text())
        # print()
        self.ui.saveas.setVisible(True)
        self.eliminateDuplicates()
        self.chainstr = [self.e.name]
        for i in range (0, self.ui.decoderchain.count()):
            op = self.ui.decoderchain.item(i).text()

            # Is this function disabled?
            if constants.DECODING_DISABLED_PREFIX in op:
                continue

            self.chainstr.append(op)

            # Add parameters to chainstr
            if constants.DECODING_REDUNDANCY in op:
                # Read Multiple Value
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = 2
                    self.chainstr.append(2) # Default
            elif constants.DECODING_CARRIER in op:
                # Read Carrier Field and add string to chainstr
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("") # Default
            elif constants.DECODING_SUBSTITUTION in op:
                # Add substitution string to chainstr: Format = src0:dst0;src1:dst1;...
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("") # Default
            elif constants.DECODING_EXTERNAL in op:
                # Add program path's string to chainstr: Format = decoder;encoder
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("") # Default
            elif constants.DECODING_DATAWHITENING in op:
                # Add Data Whitening Parameters
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("0xe9cae9ca;0x21;0x8") # Default

        self.e.set_chain(self.chainstr)
        self.decoder_update()


    def deleteElement(self):
        if self.ui.decoderchain.count() == 0:   # Clear all
            self.chainoptions.clear()
        else:
            self.chainoptions.pop(self.ui.decoderchain.active_element_text, None)
        self.decoderchainUpdate()


    def eliminateDuplicates(self):
        decoderchain_count = self.ui.decoderchain.count()
        olddecoderchain_count = len(self.old_decoderchain)

        # Special case for 1 element (add " ")
        if decoderchain_count == 1:
            tmp = self.ui.decoderchain.item(0).text()
            if tmp[-1] != " " and not tmp[-1].isnumeric():
                self.ui.decoderchain.takeItem(0)
                self.ui.decoderchain.insertItem(0, tmp + " ")

        # Ignore internal move (same count()) and removed elements and lists < 2 // len(self.old_decoderchain)+1 == self.ui.decoderchain.count()
        if decoderchain_count > 1 and decoderchain_count > olddecoderchain_count:
            elem = 0
            while elem < olddecoderchain_count:
                if self.ui.decoderchain.item(elem).text() == self.old_decoderchain[elem]:
                    elem += 1
                else:
                    break

            # Count number of current elements and append string "#<num>" to current text, if num > 1
            txt = self.ui.decoderchain.item(elem).text()
            num = 0
            for i in range (0, decoderchain_count):
                if txt in self.ui.decoderchain.item(i).text():
                    num += 1
            if num > 1:
                tmp_txt = txt + " #" + str(num)
            else:
                tmp_txt = txt + " "

            # Check duplicate names
            dup = False
            for i in range (0, decoderchain_count):
                if self.ui.decoderchain.item(i).text() == tmp_txt:
                    dup = True
                    break

            if dup:
                for i in range (1, num):
                    if i > 1:
                        tmp_txt = txt + " #" + str(i)
                    else:
                        tmp_txt = txt + " "

                    dup = False
                    for j in range (0, decoderchain_count):
                        if self.ui.decoderchain.item(j).text() == tmp_txt:
                            dup = True
                            break
                    if not dup:
                        break

            # Replace current element with new "text #<num>"
            if not dup:
                self.ui.decoderchain.takeItem(elem)
                self.ui.decoderchain.insertItem(elem, tmp_txt)

        # Save current decoderchain to old_decoderchain
        self.old_decoderchain = []
        for i in range (0, decoderchain_count):
            self.old_decoderchain.append(self.ui.decoderchain.item(i).text())


    def decoder_update(self):
        # Only allow {0, 1}
        signaltype = self.ui.combobox_signals.currentIndex()
        inpt_txt = self.ui.inpt.text()
        if signaltype == 0:
            if inpt_txt.count("0") + inpt_txt.count("1") < len(inpt_txt):
                self.ui.inpt.setText(self.old_inpt_txt)
            else:
                self.old_inpt_txt = inpt_txt

        # Write decoded bits
        bit = self.e.str2bit(self.ui.inpt.text())
        decoded = self.e.bit2str(self.e.decode(bit))
        errors = "[Decoding Errors = " + str(self.e.analyze(bit)) + "]"
        self.ui.decoding_errors_label.setText(errors)
        self.ui.output.setText(decoded)

        if len(decoded) > 0:
            if signaltype == 0:
                temp_signal = SignalSceneManager.create_rectangle(inpt_txt)[0]
                self.ui.graphicsView_signal.setScene(temp_signal)
                self.ui.graphicsView_signal.update()

            temp_decoded = SignalSceneManager.create_rectangle(decoded)[0]
            self.ui.graphicsView_decoded.setScene(temp_decoded)
            self.ui.graphicsView_decoded.update()


    def setInformation(self):
        # Presets
        decoderEdit = False
        self.ui.optionWidget.setCurrentIndex(0)
        txt = ""

        # Determine selected element
        if self.ui.basefunctions.hasFocus():
            element = self.ui.basefunctions.currentItem().text()
            txt += element + ":\n"
        elif self.ui.additionalfunctions.hasFocus():
            element = self.ui.additionalfunctions.currentItem().text()
            txt += element + ":\n"
        elif self.ui.decoderchain.hasFocus():
            decoderEdit = True
            txt = "## DECODING PROCESS ##\n\n"
            element = self.ui.decoderchain.currentItem().text()
            if element[-1] == " ":
                elementname = element[0:-1]
            else:
                elementname = element
            txt += elementname + ":\n"
            self.active_block = element

        # Remove "[Disabled] " for further tasks
        if constants.DECODING_DISABLED_PREFIX in element:
            element = element[len(constants.DECODING_DISABLED_PREFIX):]

        # Write info text and show options
        if constants.DECODING_EDGE in element:
            txt += "Trigger on signal edge, i.e. the transition between low and high.\n" \
                   "- Low to High (01) is 1\n" \
                   "- High to Low (10) is 0"
        elif constants.DECODING_SUBSTITUTION in element:
            txt += "A set of manual defined signal sequences FROM (e.g. 10, 01) is replaced by another set of " \
                   "sequences TO (e.g. 01, 10)."
            self.ui.optionWidget.setCurrentIndex(3)
            # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.substitution_rows.setValue(4)
                self.ui.substitution.setRowCount(0)
                self.ui.substitution.setRowCount(4)
            else:
                if element in self.chainoptions:
                    values = self.chainoptions[element]
                    if values == "":
                        self.ui.substitution_rows.setValue(4)
                        self.ui.substitution.setRowCount(0)
                        self.ui.substitution.setRowCount(4)
                    else:
                        arrs = self.e.get_subst_array(values)
                        if len(arrs[0]) == len(arrs[1]):
                            self.ui.substitution_rows.setValue(len(arrs[0]))
                            self.ui.substitution.setRowCount(len(arrs[0]))
                            for i in range(0, len(arrs[0])):
                                self.ui.substitution.setItem(i, 0, QTableWidgetItem(self.e.bit2str(arrs[0][i])))
                                self.ui.substitution.setItem(i, 1, QTableWidgetItem(self.e.bit2str(arrs[1][i])))
                else:
                    self.ui.substitution_rows.setValue(4)
                    self.ui.substitution.setRowCount(0)
                    self.ui.substitution.setRowCount(4)
            self.ui.substitution.setEnabled(decoderEdit)
            self.ui.substitution_rows.setEnabled(decoderEdit)

        elif constants.DECODING_EXTERNAL in element:
            txt += "The decoding (and encoding) process is delegated to external programs or scripts via parameter.\n" \
                   "Example: Given the signal 10010110, your program is called as './decoder 10010110'. Your program " \
                   "computes and prints a corresponding set of 0s and 1s which is fed back into the decoding process. "
            self.ui.optionWidget.setCurrentIndex(4)
            # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.external_decoder.setText("")
                self.ui.external_encoder.setText("")
            else:
                if element in self.chainoptions:
                    value = self.chainoptions[element]
                    if value == "":
                        self.ui.external_decoder.setText("")
                        self.ui.external_encoder.setText("")
                    else:
                        decstr, encstr = value.split(";")
                        self.ui.external_decoder.setText(decstr)
                        self.ui.external_encoder.setText(encstr)
                else:
                    self.ui.external_decoder.setText("")
                    self.ui.external_encoder.setText("")
            self.ui.external_decoder.setEnabled(decoderEdit)
            self.ui.external_encoder.setEnabled(decoderEdit)

        elif constants.DECODING_INVERT in element:
            txt += "All bits are inverted, i.e. 0->1 and 1->0."
        elif constants.DECODING_DIFFERENTIAL in element:
            txt += "Every transition between low and high (0->1 or 1->0) becomes 1, no transition (0->0 or 1->1) remains 0.\n" \
                   "The first signal bit is regarded as start value and directly copied.\n" \
                   "Example: 0011 becomes 0010 [0|(0->0)|(0->1)|(1->1)]."
        elif constants.DECODING_BITORDER in element:
            txt += "Every byte (8 bit) is reversed, i.e. the order of the bits 01234567 (e.g. least significant bit first) " \
                   "is changed to 76543210 (e.g. most significant bit first)."
        elif constants.DECODING_REDUNDANCY in element:
            txt += "If the source signal always has multiple redundant bits for one bit (e.g. 1111=1, 0000=0), the " \
                   "redundancy is removed here. You have to define the number of redundant bits."
            self.ui.optionWidget.setCurrentIndex(1)
            # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.multiple.setValue(2)
            else:
                if element in self.chainoptions:
                    value = self.chainoptions[element]
                    if value == "":
                        self.ui.multiple.setValue(2)
                    else:
                        self.ui.multiple.setValue(int(value))
                else:
                    self.ui.multiple.setValue(2)
            self.ui.multiple.setEnabled(decoderEdit)

        elif constants.DECODING_CARRIER in element:
            txt += "A carrier is a fixed pattern like 1_1_1_1 where the actual data lies in between, e.g. 1a1a1b1. This " \
                   "function extracts the actual bit information (here: aab) from the signal.\n" \
                   "Examples:\n" \
                   "- Carrier = '1' means 1_1_1_1...\n" \
                   "- Carrier = '01' means 01_01_01_01..."
            self.ui.optionWidget.setCurrentIndex(2)
            # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.carrier.setText("1")
            else:
                if element in self.chainoptions:
                    value = self.chainoptions[element]
                    if value == "":
                        self.ui.carrier.setText("1")
                    else:
                        self.ui.carrier.setText(value)
                else:
                    self.ui.carrier.setText("1")
            self.ui.carrier.setEnabled(decoderEdit)

        elif constants.DECODING_DATAWHITENING in element:
            txt += "Texas Instruments CC110x chips allow a data whitening that is applied before sending the signals to HF. " \
                   "After a preamble (1010...) there is a fixed 16/32 bit sync word. The following data (incl. 16 bit CRC) " \
                   "is masked (XOR) with the output of a LFSR.\n" \
                   "This function removes the sync word, zeroes the crc (if valid) and unmasks the data."
            self.ui.optionWidget.setCurrentIndex(5)
            # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.datawhitening_sync.setText("0xe9cae9ca")
                self.ui.datawhitening_polynomial.setText("0x21")
                self.ui.datawhitening_applycrc.setChecked(True)
                self.ui.datawhitening_preamble_rm.setChecked(False)
                self.ui.datawhitening_sync_rm.setChecked(False)
                self.ui.datawhitening_crc_rm.setChecked(False)
            else:
                if element in self.chainoptions:
                    value = self.chainoptions[element]
                    if value == "":
                        self.ui.datawhitening_sync.setText("0xe9cae9ca")
                        self.ui.datawhitening_polynomial.setText("0x21")
                        self.ui.datawhitening_applycrc.setChecked(True)
                        self.ui.datawhitening_preamble_rm.setChecked(False)
                        self.ui.datawhitening_sync_rm.setChecked(False)
                        self.ui.datawhitening_crc_rm.setChecked(False)
                    else:
                        try:
                            whitening_sync, whitening_polynomial, opt = value.split(";")
                            self.ui.datawhitening_sync.setText(whitening_sync)
                            self.ui.datawhitening_polynomial.setText(whitening_polynomial)
                            opt = self.e.hex2bit(opt)
                            if len(opt)>= 4:
                                self.ui.datawhitening_applycrc.setChecked(opt[0])
                                self.ui.datawhitening_preamble_rm.setChecked(opt[1])
                                self.ui.datawhitening_sync_rm.setChecked(opt[2])
                                self.ui.datawhitening_crc_rm.setChecked(opt[3])

                        except ValueError:
                            self.ui.datawhitening_sync.setText("0xe9cae9ca")
                            self.ui.datawhitening_polynomial.setText("0x21")
                            self.ui.datawhitening_applycrc.setChecked(True)
                            self.ui.datawhitening_preamble_rm.setChecked(False)
                            self.ui.datawhitening_sync_rm.setChecked(False)
                            self.ui.datawhitening_crc_rm.setChecked(False)

            self.ui.datawhitening_sync.setEnabled(decoderEdit)
            self.ui.datawhitening_polynomial.setEnabled(decoderEdit)
            self.ui.datawhitening_applycrc.setEnabled(decoderEdit)
            self.ui.datawhitening_preamble_rm.setEnabled(decoderEdit)
            self.ui.datawhitening_sync_rm.setEnabled(decoderEdit)
            self.ui.datawhitening_crc_rm.setEnabled(decoderEdit)

        self.ui.info.setText(txt)

    @pyqtSlot()
    def handle_datawhitening(self):
        opt = 0
        if self.ui.datawhitening_applycrc.isChecked():
            opt = opt | 0x8

        if self.ui.datawhitening_preamble_rm.isChecked():
            opt = opt | 0x4

        if self.ui.datawhitening_sync_rm.isChecked():
            opt = opt | 0x2

        if self.ui.datawhitening_crc_rm.isChecked():
            opt = opt | 0x1

        datawhiteningstr = self.ui.datawhitening_sync.text() + ";" + self.ui.datawhitening_polynomial.text() + ";" + hex(opt)
        self.chainoptions[self.active_block] = datawhiteningstr
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_external(self):
        externalstr = self.ui.external_decoder.text() + ";" + self.ui.external_encoder.text()
        self.chainoptions[self.active_block] = externalstr
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_substitution_changed(self):
        subststr = ""
        for i in range(0, self.ui.substitution_rows.value()):
            if self.ui.substitution.item(i, 0) and self.ui.substitution.item(i, 1):
                subststr += self.ui.substitution.item(i, 0).text() + ":" + self.ui.substitution.item(i, 1).text() + ";"
        self.chainoptions[self.active_block] = subststr
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_substitution_rows_changed(self):
        # Substitution Row Spinbox
        self.ui.substitution.setRowCount(self.ui.substitution_rows.value())
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_multiple_changed(self):
        # Multiple Spinbox
        val = self.ui.multiple.value()
        self.chainoptions[self.active_block] = val
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_carrier_changed(self):
        # Only allow {0, 1}
        carrier_txt = self.ui.carrier.text()
        if carrier_txt.count("0") + carrier_txt.count("1") < len(carrier_txt):
            self.ui.carrier.setText(self.old_carrier_txt)
        else:
            self.old_carrier_txt = carrier_txt
        # Carrier Textbox
        #self.e.carrier = self.e.str2bit(self.ui.carrier.text())
        self.chainoptions[self.active_block] = carrier_txt
        self.decoderchainUpdate()


    def dragEnterEvent(self, event: QDragEnterEvent):
        event.accept()


    def dropEvent(self, event: QDropEvent):
        #if not self.ui.decoderchain.geometry().contains(self.mapToGlobal(event.pos())):
        if self.ui.decoderchain.active_element >= 0:
            self.chainoptions.pop(self.ui.decoderchain.item(self.ui.decoderchain.active_element).text(), None)
        self.ui.decoderchain.takeItem(self.ui.decoderchain.active_element)
        self.decoderchainUpdate()


    def set_signal(self):
        indx = self.ui.combobox_signals.currentIndex()
        if indx != 0:
            self.ui.inpt.setReadOnly(True)
        else:
            self.ui.inpt.setReadOnly(False)
            self.ui.inpt.setText("10010110")
            self.decoder_update()
            return

        signal = self.signals[indx-1]
        pa = ProtocolAnalyzer(signal)
        pa.get_protocol_from_signal()
        self.ui.inpt.setText("".join(pa.decoded_proto_bits_str))

        tmp_scene = QGraphicsScene()
        tmp_scene.addText(self.tr("Loading Signal..."))
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.ui.graphicsView_signal.setScene(tmp_scene)
        QApplication.processEvents()

        if signal is not None:
            last_block = pa.blocks[-1]
            lookup = {i: block.bit_sample_pos for i, block in enumerate(pa.blocks)}

            plot_data = signal.qad[lookup[0][0]:lookup[pa.num_blocks - 1][len(last_block) - 1]]
            self.ui.graphicsView_signal.plot_data(plot_data)

        self.ui.graphicsView_signal.centerOn(0, 0)
        QApplication.restoreOverrideCursor()

