import copy
import os

from PyQt5.QtCore import QDir, Qt, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QDropEvent, QDragEnterEvent, QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QTableWidgetItem,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QMessageBox,
)

from urh import settings
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.ui.painting.SignalSceneManager import SignalSceneManager
from urh.ui.ui_decoding import Ui_Decoder
from urh.util.ProjectManager import ProjectManager


class DecoderDialog(QDialog):
    def __init__(
        self, decodings, signals, project_manager: ProjectManager, parent=None
    ):
        """
        :type decodings: list of Encoding
        :type signals: list of Signal
        """
        # Init
        super().__init__(parent)
        self.ui = Ui_Decoder()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)

        # Variables
        self.old_inpt_txt = ""
        self.old_carrier_txt = ""
        self.old_decoderchain = []
        self.active_message = ""
        self.old_cutmark = ""
        self.old_morse = (1, 3)

        self.project_manager = project_manager

        # Initialize encoder
        self.decodings = decodings
        self.ui.combobox_decodings.clear()
        for decoding in self.decodings:
            self.ui.combobox_decodings.addItem(decoding.name)
        self.chainstr = []
        self.chainoptions = {}
        self.set_e()

        self.last_selected_item = ""

        # Signals
        self.signals = signals if signals is not None else []
        for signal in signals:
            if signal:
                self.ui.combobox_signals.addItem(signal.name)

        # Function lists
        self.ui.basefunctions.addItem(settings.DECODING_EDGE)
        self.ui.basefunctions.addItem(settings.DECODING_MORSE)
        self.ui.basefunctions.addItem(settings.DECODING_SUBSTITUTION)
        self.ui.basefunctions.addItem(settings.DECODING_EXTERNAL)
        self.ui.additionalfunctions.addItem(settings.DECODING_INVERT)
        self.ui.additionalfunctions.addItem(settings.DECODING_DIFFERENTIAL)
        self.ui.additionalfunctions.addItem(settings.DECODING_BITORDER)
        self.ui.additionalfunctions.addItem(settings.DECODING_REDUNDANCY)
        self.ui.additionalfunctions.addItem(settings.DECODING_CARRIER)
        self.ui.additionalfunctions.addItem(settings.DECODING_DATAWHITENING)
        self.ui.additionalfunctions.addItem(settings.DECODING_ENOCEAN)
        self.ui.additionalfunctions.addItem(settings.DECODING_CUT)

        # Presets
        self.setWindowTitle("Decoding")
        self.setWindowIcon(QIcon(":/icons/icons/decoding.svg"))
        self.setAcceptDrops(True)
        self.inpt_text = "10010110"
        self.ui.inpt.setText(self.inpt_text)
        self.ui.optionWidget.setCurrentIndex(0)
        self.decoder_update()

        self.ui.substitution.setColumnCount(2)
        self.ui.substitution.setRowCount(self.ui.substitution_rows.value())
        self.ui.substitution.setHorizontalHeaderLabels(["From", "To"])
        self.ui.substitution.setColumnWidth(0, 190)
        self.ui.substitution.setColumnWidth(1, 190)

        self.ui.btnAddtoYourDecoding.hide()
        self.ui.saveas.setVisible(False)

        # Connects
        self.create_connects()
        self.restoreGeometry(
            settings.read("{}/geometry".format(self.__class__.__name__), type=bytes)
        )

    def create_connects(self):
        self.ui.inpt.textChanged.connect(self.decoder_update)
        self.ui.multiple.valueChanged.connect(self.handle_multiple_changed)
        self.ui.carrier.textChanged.connect(self.handle_carrier_changed)
        self.ui.substitution_rows.valueChanged.connect(
            self.handle_substitution_rows_changed
        )
        self.ui.substitution.itemChanged.connect(self.handle_substitution_changed)

        self.ui.btnChooseDecoder.clicked.connect(self.choose_decoder)
        self.ui.btnChooseEncoder.clicked.connect(self.choose_encoder)

        self.ui.external_decoder.textEdited.connect(self.handle_external)
        self.ui.external_encoder.textEdited.connect(self.handle_external)
        self.ui.datawhitening_sync.textEdited.connect(self.handle_datawhitening)
        self.ui.datawhitening_polynomial.textEdited.connect(self.handle_datawhitening)
        self.ui.datawhitening_overwrite_crc.clicked.connect(self.handle_datawhitening)

        self.ui.decoderchain.itemChanged.connect(self.decoderchainUpdate)
        self.ui.decoderchain.internalMove.connect(self.decoderchainUpdate)
        self.ui.decoderchain.deleteElement.connect(self.deleteElement)
        self.ui.decoderchain.currentRowChanged.connect(
            self.on_decoder_chain_current_row_changed
        )
        self.ui.basefunctions.currentRowChanged.connect(
            self.on_base_functions_current_row_changed
        )
        self.ui.additionalfunctions.currentRowChanged.connect(
            self.on_additional_functions_current_row_changed
        )
        self.ui.btnAddtoYourDecoding.clicked.connect(
            self.on_btn_add_to_your_decoding_clicked
        )

        self.ui.combobox_decodings.currentIndexChanged.connect(self.set_e)
        self.ui.combobox_signals.currentIndexChanged.connect(self.set_signal)
        self.ui.saveas.clicked.connect(self.saveas)
        self.ui.delete_decoding.clicked.connect(self.delete_decoding)

        self.ui.rB_delbefore.clicked.connect(self.handle_cut)
        self.ui.rB_delafter.clicked.connect(self.handle_cut)
        self.ui.rB_delbeforepos.clicked.connect(self.handle_cut)
        self.ui.rB_delafterpos.clicked.connect(self.handle_cut)
        self.ui.cutmark.textEdited.connect(self.handle_cut)
        self.ui.cutmark2.valueChanged.connect(self.handle_cut)

        self.ui.morse_low.valueChanged.connect(self.handle_morse_changed)
        self.ui.morse_high.valueChanged.connect(self.handle_morse_changed)
        self.ui.morse_wait.valueChanged.connect(self.handle_morse_changed)

    def closeEvent(self, event: QCloseEvent):
        settings.write(
            "{}/geometry".format(self.__class__.__name__), self.saveGeometry()
        )
        super().closeEvent(event)

    def choose_decoder(self):
        f, ok = QFileDialog.getOpenFileName(
            self, self.tr("Choose decoder program"), QDir.homePath()
        )
        if f and ok:
            self.ui.external_decoder.setText(f)
            self.handle_external()

    def choose_encoder(self):
        f, ok = QFileDialog.getOpenFileName(
            self, self.tr("Choose encoder program"), QDir.homePath()
        )
        if f and ok:
            self.ui.external_encoder.setText(f)
            self.handle_external()

    def save_to_file(self):
        if self.project_manager.project_file:
            self.project_manager.decodings = self.decodings
        else:
            prefix = os.path.realpath(
                os.path.join(settings.get_qt_settings_filename(), "..")
            )
            with open(os.path.join(prefix, settings.DECODINGS_FILE), "w") as f:
                for i in range(0, self.ui.combobox_decodings.count()):
                    str = ""
                    for j in self.decodings[i].get_chain():
                        str += repr(j) + ", "
                    str += "\n"
                    f.write(str)

    def saveas(self):
        # Ask for a name
        name, ok = QInputDialog.getText(
            self,
            self.tr("Save decoding"),
            self.tr("Please enter a name:"),
            QLineEdit.Normal,
            self.e.chain[0],
        )

        if ok and name != "":
            self.e.chain[0] = name
            self.decoderchainUpdate()

            # If name is already there, overwrite existing
            for i in range(0, len(self.decodings)):
                if name == self.decodings[i].name:
                    self.ui.combobox_decodings.setCurrentIndex(i)
                    self.decodings[i] = Encoding(self.chainstr)
                    self.set_e()
                    self.ui.saveas.setVisible(False)
                    self.save_to_file()
                    return

            self.decodings.append(Encoding(self.chainstr))
            self.ui.combobox_decodings.addItem(self.chainstr[0])
            self.ui.combobox_decodings.setCurrentIndex(
                self.ui.combobox_decodings.count() - 1
            )
            self.set_e()
            self.save_to_file()

    def delete_decoding(self):
        num = self.ui.combobox_decodings.currentIndex()
        if num >= 0:
            reply = QMessageBox.question(
                self,
                self.tr("Delete Decoding?"),
                self.tr(
                    "Do you really want to delete "
                    + "'{}'?".format(self.decodings[num].name)
                ),
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.decodings.pop(num)
                self.ui.combobox_decodings.removeItem(num)
                self.save_to_file()

    def set_e(self):
        if self.ui.combobox_decodings.count() < 1:  # Empty list
            return

        self.e = copy.deepcopy(
            self.decodings[self.ui.combobox_decodings.currentIndex()]
        )
        """:type: encoding """
        chain = self.e.get_chain()
        self.ui.decoderchain.clear()
        self.chainoptions.clear()
        last_i = ""
        for i in chain:
            if i in [
                settings.DECODING_INVERT,
                settings.DECODING_ENOCEAN,
                settings.DECODING_DIFFERENTIAL,
                settings.DECODING_REDUNDANCY,
                settings.DECODING_CARRIER,
                settings.DECODING_BITORDER,
                settings.DECODING_EDGE,
                settings.DECODING_DATAWHITENING,
                settings.DECODING_SUBSTITUTION,
                settings.DECODING_EXTERNAL,
                settings.DECODING_CUT,
                settings.DECODING_MORSE,
                settings.DECODING_DISABLED_PREFIX,
            ]:
                self.ui.decoderchain.addItem(i)
                self.decoderchainUpdate()
                last_i = self.ui.decoderchain.item(
                    self.ui.decoderchain.count() - 1
                ).text()
            else:
                if any(
                    x in last_i
                    for x in [
                        settings.DECODING_REDUNDANCY,
                        settings.DECODING_CARRIER,
                        settings.DECODING_SUBSTITUTION,
                        settings.DECODING_EXTERNAL,
                        settings.DECODING_DATAWHITENING,
                        settings.DECODING_CUT,
                        settings.DECODING_MORSE,
                    ]
                ):
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
        for i in range(0, self.ui.decoderchain.count()):
            op = self.ui.decoderchain.item(i).text()

            # Is this function disabled?
            if settings.DECODING_DISABLED_PREFIX in op:
                continue

            self.chainstr.append(op)

            # Add parameters to chainstr
            if settings.DECODING_REDUNDANCY in op:
                # Read Multiple Value
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = 2
                    self.chainstr.append(2)  # Default
            elif settings.DECODING_CARRIER in op:
                # Read Carrier Field and add string to chainstr
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("")  # Default
            elif settings.DECODING_SUBSTITUTION in op:
                # Add substitution string to chainstr: Format = src0:dst0;src1:dst1;...
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("")  # Default
            elif settings.DECODING_EXTERNAL in op:
                # Add program path's string to chainstr: Format = decoder;encoder
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("")  # Default
            elif settings.DECODING_DATAWHITENING in op:
                # Add Data Whitening Parameters
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("0xe9cae9ca;0x21;0")  # Default
            elif settings.DECODING_CUT in op:
                # Add cut parameters
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("0;1010")  # Default
            elif settings.DECODING_MORSE in op:
                # Add morse parameters
                if op in self.chainoptions:
                    self.chainstr.append(self.chainoptions[op])
                else:
                    self.chainoptions[op] = ""
                    self.chainstr.append("1;3;1")  # Default

        self.e.set_chain(self.chainstr)
        self.decoder_update()

    def deleteElement(self):
        if self.ui.decoderchain.count() == 0:  # Clear all
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
                if (
                    self.ui.decoderchain.item(elem).text()
                    == self.old_decoderchain[elem]
                ):
                    elem += 1
                else:
                    break

            # Count number of current elements and append string "#<num>" to current text, if num > 1
            txt = self.ui.decoderchain.item(elem).text()
            num = 0
            for i in range(0, decoderchain_count):
                if txt in self.ui.decoderchain.item(i).text():
                    num += 1
            if num > 1:
                tmp_txt = txt + " #" + str(num)
            else:
                tmp_txt = txt + " "

            # Check duplicate names
            dup = False
            for i in range(0, decoderchain_count):
                if self.ui.decoderchain.item(i).text() == tmp_txt:
                    dup = True
                    break

            if dup:
                for i in range(1, num):
                    if i > 1:
                        tmp_txt = txt + " #" + str(i)
                    else:
                        tmp_txt = txt + " "

                    dup = False
                    for j in range(0, decoderchain_count):
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
        for i in range(0, decoderchain_count):
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
        errors = "[Decoding Errors = " + str(self.e.analyze(bit)[0]) + "]"
        self.ui.decoding_errors_label.setText(errors)
        self.ui.output.setText(decoded)
        self.ui.output.setCursorPosition(0)

        if len(decoded) > 0:
            if signaltype == 0:
                temp_signal = SignalSceneManager.create_rectangle(inpt_txt)[0]
                self.ui.graphicsView_signal.setScene(temp_signal)
                self.ui.graphicsView_signal.update()

            temp_decoded = SignalSceneManager.create_rectangle(decoded)[0]
            self.ui.graphicsView_decoded.setScene(temp_decoded)
            self.ui.graphicsView_decoded.update()

    @pyqtSlot(int)
    def on_base_functions_current_row_changed(self, index: int):
        if self.ui.basefunctions.currentItem().text() is not None:
            self.ui.decoderchain.setCurrentRow(-1)
            self.set_information(0)
        else:
            self.ui.optionWidget.setCurrentIndex(0)
            self.ui.info.clear()

    @pyqtSlot(int)
    def on_additional_functions_current_row_changed(self, index: int):
        if self.ui.additionalfunctions.currentItem() is not None:
            self.ui.decoderchain.setCurrentRow(-1)
            self.set_information(1)
        else:
            self.ui.optionWidget.setCurrentIndex(0)
            self.ui.info.clear()

    @pyqtSlot(int)
    def on_decoder_chain_current_row_changed(self, index: int):
        if self.ui.decoderchain.currentItem() is not None:
            self.set_information(2)
        else:
            self.ui.optionWidget.setCurrentIndex(0)
            self.ui.info.clear()

    def set_information(self, mode: int):
        # Presets
        decoderEdit = False
        self.ui.optionWidget.setCurrentIndex(0)
        txt = ""

        # Determine selected element
        if mode == 0:
            element = self.ui.basefunctions.currentItem().text()
            txt += element + ":\n"
            self.last_selected_item = element
            self.ui.btnAddtoYourDecoding.show()
        elif mode == 1:
            element = self.ui.additionalfunctions.currentItem().text()
            txt += element + ":\n"
            self.last_selected_item = element
            self.ui.btnAddtoYourDecoding.show()
        elif mode == 2:
            decoderEdit = True
            txt = "## In Your Decoding ##\n\n"
            element = self.ui.decoderchain.currentItem().text()
            if element[-1] == " ":
                elementname = element[0:-1]
            else:
                elementname = element
            txt += elementname + ":\n"
            self.active_message = element
            self.ui.btnAddtoYourDecoding.hide()

        # Remove "[Disabled] " for further tasks
        if settings.DECODING_DISABLED_PREFIX in element:
            element = element[len(settings.DECODING_DISABLED_PREFIX) :]

        # Write info text and show options
        if settings.DECODING_EDGE in element:
            txt += (
                "Trigger on signal edge, i.e. the transition between low and high.\n"
                "- Low to High (01) is 1\n"
                "- High to Low (10) is 0"
            )
        elif settings.DECODING_SUBSTITUTION in element:
            txt += (
                "A set of manual defined signal sequences FROM (e.g. 110, 100) is replaced by another set of "
                "sequences TO (e.g. 01, 10). Note that all FROM entries must have the same length, otherwise "
                "the result is unpredictable! (For TX: all TO entries must have the same length)"
            )
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
                                self.ui.substitution.setItem(
                                    i, 0, QTableWidgetItem(self.e.bit2str(arrs[0][i]))
                                )
                                self.ui.substitution.setItem(
                                    i, 1, QTableWidgetItem(self.e.bit2str(arrs[1][i]))
                                )
                else:
                    self.ui.substitution_rows.setValue(4)
                    self.ui.substitution.setRowCount(0)
                    self.ui.substitution.setRowCount(4)
            self.ui.substitution.setEnabled(decoderEdit)
            self.ui.substitution_rows.setEnabled(decoderEdit)

        elif settings.DECODING_EXTERNAL in element:
            txt += (
                "The decoding (and encoding) process is delegated to external programs or scripts via parameter.\n"
                "Example: Given the signal 10010110, your program is called as './decoder 10010110'. Your program "
                "computes and prints a corresponding set of 0s and 1s which is fed back into the decoding process. "
            )
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
            self.ui.btnChooseDecoder.setEnabled(decoderEdit)
            self.ui.btnChooseEncoder.setEnabled(decoderEdit)

        elif settings.DECODING_INVERT in element:
            txt += "All bits are inverted, i.e. 0->1 and 1->0."
        elif settings.DECODING_ENOCEAN in element:
            txt += "Remove Wireless Short-Packet (WSP) encoding that is used by EnOcean standard."
        elif settings.DECODING_DIFFERENTIAL in element:
            txt += (
                "Every transition between low and high (0->1 or 1->0) becomes 1, no transition (0->0 or 1->1) remains 0.\n"
                "The first signal bit is regarded as start value and directly copied.\n"
                "Example: 0011 becomes 0010 [0|(0->0)|(0->1)|(1->1)]."
            )
        elif settings.DECODING_BITORDER in element:
            txt += (
                "Every byte (8 bit) is reversed, i.e. the order of the bits 01234567 (e.g. least significant bit first) "
                "is changed to 76543210 (e.g. most significant bit first)."
            )
        elif settings.DECODING_REDUNDANCY in element:
            txt += (
                "If the source signal always has multiple redundant bits for one bit (e.g. 1111=1, 0000=0), the "
                "redundancy is removed here. You have to define the number of redundant bits."
            )
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
        elif settings.DECODING_MORSE in element:
            txt += (
                "If the signal is a morse code, e.g. 00111001001110011100, where information are "
                "transported with long and short sequences of 1 (0 just for padding), then this "
                "decoding evaluates those sequences (Example output: 1011)."
            )
            self.ui.optionWidget.setCurrentIndex(7)
            # # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.morse_low.setValue(1)
                self.ui.morse_high.setValue(3)
                self.ui.morse_wait.setValue(1)
            else:
                if element in self.chainoptions:
                    value = self.chainoptions[element]
                    if value == "":
                        self.ui.morse_low.setValue(1)
                        self.ui.morse_high.setValue(3)
                        self.ui.morse_wait.setValue(1)
                    else:
                        try:
                            l, h, w = value.split(";")
                            self.ui.morse_low.setValue(int(l))
                            self.ui.morse_high.setValue(int(h))
                            self.ui.morse_wait.setValue(int(w))
                        except ValueError:
                            self.ui.morse_low.setValue(1)
                            self.ui.morse_high.setValue(3)
                            self.ui.morse_wait.setValue(1)
                else:
                    self.ui.morse_low.setValue(1)
                    self.ui.morse_high.setValue(3)
                    self.ui.morse_wait.setValue(1)
            self.ui.morse_low.setEnabled(decoderEdit)
            self.ui.morse_high.setEnabled(decoderEdit)
            self.ui.morse_wait.setEnabled(decoderEdit)
        elif settings.DECODING_CARRIER in element:
            txt += (
                "A carrier is a fixed pattern like 1_1_1_1 where the actual data lies in between, e.g. 1a1a1b1. This "
                "function extracts the actual bit information (here: aab) from the signal at '_'/'.' positions.\n"
                "Examples:\n"
                "- Carrier = '1_' means 1_1_1_...\n"
                "- Carrier = '01_' means 01_01_01_01..."
            )
            self.ui.optionWidget.setCurrentIndex(2)
            # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.carrier.setText("1_")
            else:
                if element in self.chainoptions:
                    value = self.chainoptions[element]
                    if value == "":
                        self.ui.carrier.setText("1_")
                    else:
                        self.ui.carrier.setText(value)
                else:
                    self.ui.carrier.setText("1_")
            self.ui.carrier.setEnabled(decoderEdit)
        elif settings.DECODING_DATAWHITENING in element:
            txt += (
                "Texas Instruments CC110x chips allow a data whitening that is applied before sending the signals to HF. "
                "After a preamble (1010...) there is a fixed 16/32 bit sync word. The following data (incl. 16 bit CRC) "
                "is masked (XOR) with the output of a LFSR.\n"
                "This unmasks the data."
            )
            self.ui.optionWidget.setCurrentIndex(5)
            # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.datawhitening_sync.setText("0xe9cae9ca")
                self.ui.datawhitening_polynomial.setText("0x21")
                self.ui.datawhitening_overwrite_crc.setChecked(False)
            else:
                if element in self.chainoptions:
                    value = self.chainoptions[element]
                    if value == "":
                        self.ui.datawhitening_sync.setText("0xe9cae9ca")
                        self.ui.datawhitening_polynomial.setText("0x21")
                        self.ui.datawhitening_overwrite_crc.setChecked(False)
                    else:
                        try:
                            (
                                whitening_sync,
                                whitening_polynomial,
                                whitening_overwrite_crc,
                            ) = value.split(";")
                            self.ui.datawhitening_sync.setText(whitening_sync)
                            self.ui.datawhitening_polynomial.setText(
                                whitening_polynomial
                            )
                            self.ui.datawhitening_overwrite_crc.setChecked(
                                True if whitening_overwrite_crc == "1" else False
                            )

                        except ValueError:
                            self.ui.datawhitening_sync.setText("0xe9cae9ca")
                            self.ui.datawhitening_polynomial.setText("0x21")
                            self.ui.datawhitening_overwrite_crc.setChecked(False)

            self.ui.datawhitening_sync.setEnabled(decoderEdit)
            self.ui.datawhitening_polynomial.setEnabled(decoderEdit)
            self.ui.datawhitening_overwrite_crc.setEnabled(decoderEdit)

        elif settings.DECODING_CUT in element:
            txt += (
                "This function enables you to cut data from your messages, in order to shorten or align them for a "
                "better view. Note that this decoding does NOT support encoding, because cut data is gone!\n"
                "Example:\n"
                "- Cut before '1010' would delete everything before first '1010' bits.\n"
                "- Cut before Position = 3 (in bit) would delete the first three bits.\n"
            )
            self.ui.optionWidget.setCurrentIndex(6)
            # Values can only be changed when editing decoder, otherwise default value
            if not decoderEdit:
                self.ui.cutmark.setText("1010")
                self.old_cutmark = self.ui.cutmark.text()
                self.ui.cutmark2.setValue(1)
                self.ui.rB_delbefore.setChecked(False)
                self.ui.rB_delafter.setChecked(False)
                self.ui.rB_delbeforepos.setChecked(False)
                self.ui.rB_delafterpos.setChecked(False)
                self.ui.cutmark.setEnabled(False)
                self.ui.cutmark2.setEnabled(False)
            else:
                if element in self.chainoptions:
                    value = self.chainoptions[element]
                    if value == "":
                        self.ui.cutmark.setText("1010")
                        self.ui.cutmark.setEnabled(True)
                        self.old_cutmark = self.ui.cutmark.text()
                        self.ui.cutmark2.setValue(1)
                        self.ui.cutmark2.setEnabled(False)
                        self.ui.rB_delbefore.setChecked(True)
                        self.ui.rB_delafter.setChecked(False)
                        self.ui.rB_delbeforepos.setChecked(False)
                        self.ui.rB_delafterpos.setChecked(False)
                    else:
                        try:
                            cmode, cmark = value.split(";")
                            cmode = int(cmode)
                            if cmode == 0:
                                self.ui.rB_delbefore.setChecked(True)
                                self.ui.cutmark.setEnabled(True)
                                self.ui.cutmark2.setEnabled(False)
                                self.ui.cutmark.setText(cmark)
                            elif cmode == 1:
                                self.ui.rB_delafter.setChecked(True)
                                self.ui.cutmark.setEnabled(True)
                                self.ui.cutmark2.setEnabled(False)
                                self.ui.cutmark.setText(cmark)
                            elif cmode == 2:
                                self.ui.rB_delbeforepos.setChecked(True)
                                self.ui.cutmark.setEnabled(False)
                                self.ui.cutmark2.setEnabled(True)
                                self.ui.cutmark2.setValue(int(cmark))
                            elif cmode == 3:
                                self.ui.rB_delafterpos.setChecked(True)
                                self.ui.cutmark.setEnabled(False)
                                self.ui.cutmark2.setEnabled(True)
                                self.ui.cutmark2.setValue(int(cmark))

                        except ValueError:
                            self.ui.cutmark.setText("1010")
                            self.old_cutmark = self.ui.cutmark.text()
                            self.ui.cutmark2.setValue(1)
                            self.ui.rB_delbefore.setChecked(True)
                            self.ui.rB_delafter.setChecked(False)
                            self.ui.rB_delbeforepos.setChecked(False)
                            self.ui.rB_delafterpos.setChecked(False)
                            self.ui.cutmark.setEnabled(True)
                            self.ui.cutmark2.setEnabled(False)
                else:
                    self.ui.cutmark.setText("1010")
                    self.old_cutmark = self.ui.cutmark.text()
                    self.ui.cutmark2.setValue(1)
                    self.ui.rB_delbefore.setChecked(True)
                    self.ui.rB_delafter.setChecked(False)
                    self.ui.rB_delbeforepos.setChecked(False)
                    self.ui.rB_delafterpos.setChecked(False)
                    self.ui.cutmark.setEnabled(True)
                    self.ui.cutmark2.setEnabled(False)
            self.ui.rB_delbefore.setEnabled(decoderEdit)
            self.ui.rB_delafter.setEnabled(decoderEdit)
            self.ui.rB_delbeforepos.setEnabled(decoderEdit)
            self.ui.rB_delafterpos.setEnabled(decoderEdit)

        self.ui.info.setText(txt)

    @pyqtSlot()
    def handle_datawhitening(self):
        datawhiteningstr = (
            self.ui.datawhitening_sync.text()
            + ";"
            + self.ui.datawhitening_polynomial.text()
            + ";"
            + ("1" if self.ui.datawhitening_overwrite_crc.isChecked() else "0")
        )
        if settings.DECODING_DATAWHITENING in self.active_message:
            self.chainoptions[self.active_message] = datawhiteningstr
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_external(self):
        externalstr = (
            self.ui.external_decoder.text() + ";" + self.ui.external_encoder.text()
        )
        if settings.DECODING_EXTERNAL in self.active_message:
            self.chainoptions[self.active_message] = externalstr
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_substitution_changed(self):
        subststr = ""
        for i in range(0, self.ui.substitution_rows.value()):
            if self.ui.substitution.item(i, 0) and self.ui.substitution.item(i, 1):
                subststr += (
                    self.ui.substitution.item(i, 0).text()
                    + ":"
                    + self.ui.substitution.item(i, 1).text()
                    + ";"
                )
        if settings.DECODING_SUBSTITUTION in self.active_message:
            self.chainoptions[self.active_message] = subststr
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
        if settings.DECODING_REDUNDANCY in self.active_message:
            self.chainoptions[self.active_message] = val
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_morse_changed(self):
        # Multiple Spinbox
        val_low = self.ui.morse_low.value()
        val_high = self.ui.morse_high.value()
        val_wait = self.ui.morse_wait.value()

        if val_low >= val_high:
            self.ui.morse_low.setValue(self.old_morse[0])
            self.ui.morse_high.setValue(self.old_morse[1])
            (val_low, val_high) = self.old_morse
        else:
            self.old_morse = (val_low, val_high)

        if settings.DECODING_MORSE in self.active_message:
            self.chainoptions[self.active_message] = "{};{};{}".format(
                val_low, val_high, val_wait
            )
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_carrier_changed(self):
        # Only allow {0, 1}
        carrier_txt = self.ui.carrier.text()
        if carrier_txt.count("0") + carrier_txt.count("1") + carrier_txt.count(
            "_"
        ) + carrier_txt.count(".") + carrier_txt.count("*") < len(carrier_txt):
            self.ui.carrier.setText(self.old_carrier_txt)
        else:
            self.old_carrier_txt = carrier_txt
        # Carrier Textbox
        # self.e.carrier = self.e.str2bit(self.ui.carrier.text())
        if settings.DECODING_CARRIER in self.active_message:
            self.chainoptions[self.active_message] = carrier_txt
        self.decoderchainUpdate()

    @pyqtSlot()
    def handle_cut(self):
        cmode = 0
        cmark = ""
        if self.ui.rB_delbefore.isChecked() or self.ui.rB_delafter.isChecked():
            # Activate right cutmark field
            self.ui.cutmark.setEnabled(True)
            self.ui.cutmark2.setEnabled(False)
            # set cmode
            if self.ui.rB_delafter.isChecked():
                cmode = 1
            # check values in cutmark
            cmark = self.ui.cutmark.text()
            if cmark.count("0") + cmark.count("1") < len(cmark):
                self.ui.cutmark.setText(self.old_cutmark)
            else:
                self.old_cutmark = cmark
        else:
            # Activate right cutmark field
            self.ui.cutmark.setEnabled(False)
            self.ui.cutmark2.setEnabled(True)
            # set cmode
            if self.ui.rB_delbeforepos.isChecked():
                cmode = 2
            else:
                cmode = 3
            cmark = str(self.ui.cutmark2.value())

        cut_text = str(cmode) + ";" + cmark

        if settings.DECODING_CUT in self.active_message:
            self.chainoptions[self.active_message] = cut_text
        self.decoderchainUpdate()

    @pyqtSlot()
    def on_btn_add_to_your_decoding_clicked(self):
        if self.last_selected_item != "":
            self.ui.decoderchain.addItem(self.last_selected_item)
            self.decoderchainUpdate()
            self.ui.decoderchain.setCurrentRow(self.ui.decoderchain.count() - 1)

    def dragEnterEvent(self, event: QDragEnterEvent):
        event.accept()

    def dropEvent(self, event: QDropEvent):
        # if not self.ui.decoderchain.geometry().contains(self.mapToGlobal(event.pos())):
        if self.ui.decoderchain.currentItem() is not None:
            self.chainoptions.pop(self.ui.decoderchain.currentItem().text(), None)
            self.ui.decoderchain.takeItem(self.ui.decoderchain.currentRow())
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

        self.setCursor(Qt.WaitCursor)

        signal = self.signals[indx - 1]
        pa = ProtocolAnalyzer(signal)
        pa.get_protocol_from_signal()
        self.ui.inpt.setText("".join(pa.plain_bits_str))
        self.ui.inpt.setCursorPosition(0)

        if signal is not None and pa.messages:
            last_message = pa.messages[-1]
            lookup = {i: msg.bit_sample_pos for i, msg in enumerate(pa.messages)}

            plot_data = signal.qad[
                lookup[0][0] : lookup[pa.num_messages - 1][len(last_message) - 1]
            ]
            self.ui.graphicsView_signal.plot_data(plot_data)

        self.ui.graphicsView_signal.centerOn(0, 0)
        self.unsetCursor()
