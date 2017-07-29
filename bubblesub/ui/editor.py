import bubblesub.util
from PyQt5 import QtWidgets


class Editor(QtWidgets.QWidget):
    # TODO: allow editing layer, margins and comment
    def __init__(self, api, parent=None):
        super().__init__(parent)

        self._index = None
        self._api = api

        self.style_edit = QtWidgets.QComboBox(
            self,
            editable=True,
            minimumWidth=200,
            insertPolicy=QtWidgets.QComboBox.NoInsert)
        self.actor_edit = QtWidgets.QComboBox(
            self,
            editable=True,
            minimumWidth=200,
            insertPolicy=QtWidgets.QComboBox.NoInsert)
        self.start_time_edit = bubblesub.ui.util.TimeEdit(self)
        self.end_time_edit = bubblesub.ui.util.TimeEdit(self)
        self.duration_edit = bubblesub.ui.util.TimeEdit(self)
        self.text_edit = QtWidgets.QPlainTextEdit(self, tabChangesFocus=True)

        top_bar = QtWidgets.QWidget(self)
        top_bar.setLayout(QtWidgets.QHBoxLayout(self))
        top_bar.layout().setContentsMargins(0, 0, 0, 0)
        top_bar.layout().addWidget(QtWidgets.QLabel('Style:', self))
        top_bar.layout().addWidget(self.style_edit)
        top_bar.layout().addWidget(QtWidgets.QLabel('Actor:', self))
        top_bar.layout().addWidget(self.actor_edit)
        top_bar.layout().addWidget(QtWidgets.QLabel('Start time:', self))
        top_bar.layout().addWidget(self.start_time_edit)
        top_bar.layout().addWidget(QtWidgets.QLabel('End time:', self))
        top_bar.layout().addWidget(self.end_time_edit)
        top_bar.layout().addWidget(QtWidgets.QLabel('Duration:', self))
        top_bar.layout().addWidget(self.duration_edit)

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addWidget(top_bar)
        self.layout().addWidget(self.text_edit)
        self.setEnabled(False)

        api.subs.lines.item_changed.connect(self._item_changed)
        api.subs.selection_changed.connect(self._grid_selection_changed)
        self._connect_slots()

    def _fetch_selection(self, index):
        self._index = index
        subtitle = self._api.subs.lines[index]
        self.start_time_edit.setText(bubblesub.util.ms_to_str(subtitle.start))
        self.end_time_edit.setText(bubblesub.util.ms_to_str(subtitle.end))
        self.duration_edit.setText(bubblesub.util.ms_to_str(subtitle.duration))

        self.actor_edit.clear()
        self.actor_edit.addItems(
            sorted(list(set(sub.actor for sub in self._api.subs.lines))))
        self.actor_edit.lineEdit().setText(subtitle.actor)

        self.style_edit.clear()
        self.style_edit.addItems(
            sorted(list(set(sub.style for sub in self._api.subs.lines))))
        self.style_edit.lineEdit().setText(subtitle.style)

        text = subtitle.text
        if self._api.opt.general['convert_newlines']:
            text = text.replace('\\N', '\n')
        self.text_edit.document().setPlainText(text)
        self.setEnabled(True)

    def _clear_selection(self):
        self._index = None
        self.start_time_edit.reset_text()
        self.end_time_edit.reset_text()
        self.duration_edit.reset_text()
        self.style_edit.lineEdit().setText('')
        self.actor_edit.lineEdit().setText('')
        self.text_edit.document().setPlainText('')
        self.setEnabled(False)

    def _push_selection(self):
        if not self.isEnabled():
            return

        new_start = bubblesub.util.str_to_ms(self.start_time_edit.text())
        new_end = bubblesub.util.str_to_ms(self.end_time_edit.text())
        new_style = self.style_edit.lineEdit().text()
        new_actor = self.actor_edit.lineEdit().text()
        new_text = self.text_edit.toPlainText().replace('\n', '\\N')

        subtitle = self._api.subs.lines[self._index]
        subtitle.begin_update()
        subtitle.start = new_start
        subtitle.end = new_end
        subtitle.style = new_style
        subtitle.actor = new_actor
        subtitle.text = new_text
        subtitle.end_update()

    def _grid_selection_changed(self, rows):
        self._disconnect_slots()
        if len(rows) == 1:
            self._fetch_selection(rows[0])
        else:
            self._clear_selection()
        self._connect_slots()

    def _item_changed(self, idx):
        if idx == self._index or idx is None:
            self._disconnect_slots()
            self._fetch_selection(self._index)
            self._connect_slots()

    def _time_end_edited(self):
        start = bubblesub.util.str_to_ms(self.start_time_edit.text())
        end = bubblesub.util.str_to_ms(self.end_time_edit.text())
        duration = end - start
        self.duration_edit.setText(bubblesub.util.ms_to_str(duration))
        self._push_selection()

    def _duration_edited(self):
        start = bubblesub.util.str_to_ms(self.start_time_edit.text())
        duration = bubblesub.util.str_to_ms(self.duration_edit.text())
        end = start + duration
        self.end_time_edit.setText(bubblesub.util.ms_to_str(end))
        self._push_selection()

    def _generic_edited(self):
        self._push_selection()

    def _connect_slots(self):
        self.start_time_edit.textEdited.connect(self._generic_edited)
        self.end_time_edit.textEdited.connect(self._time_end_edited)
        self.duration_edit.textEdited.connect(self._duration_edited)
        self.actor_edit.editTextChanged.connect(self._generic_edited)
        self.style_edit.editTextChanged.connect(self._generic_edited)
        self.text_edit.textChanged.connect(self._generic_edited)

    def _disconnect_slots(self):
        self.start_time_edit.textEdited.disconnect(self._generic_edited)
        self.end_time_edit.textEdited.disconnect(self._time_end_edited)
        self.duration_edit.textEdited.disconnect(self._duration_edited)
        self.actor_edit.editTextChanged.disconnect(self._generic_edited)
        self.style_edit.editTextChanged.disconnect(self._generic_edited)
        self.text_edit.textChanged.disconnect(self._generic_edited)
