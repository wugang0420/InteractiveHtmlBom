"""Subclass of settings_dialog, which is generated by wxFormBuilder."""
import os
import re

import wx

import dialog_base


def pop_error(msg):
    wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)


class SettingsDialog(dialog_base.SettingsDialogBase):
    def __init__(self, parent, extra_data_func):
        dialog_base.SettingsDialogBase.__init__(self, parent)
        self.panel = SettingsDialogPanel(self, extra_data_func)
        best_size = self.panel.BestSize
        # hack for some gtk themes that incorrectly calculate best size
        best_size.IncBy(dx=0, dy=30)
        self.SetClientSize(best_size)

    # hack for new wxFormBuilder generating code incompatible with old wxPython
    # noinspection PyMethodOverriding
    def SetSizeHints(self, sz1, sz2):
        self.SetSizeHintsSz(sz1, sz2)

    def set_extra_data_path(self, extra_data_file):
        print extra_data_file
        self.panel.extra.netlistFilePicker.Path = extra_data_file
        wx.CallAfter(self.panel.extra.OnNetlistFileChanged, None)


# Implementing settings_dialog
class SettingsDialogPanel(dialog_base.SettingsDialogPanel):
    def __init__(self, parent, extra_data_func):
        dialog_base.SettingsDialogPanel.__init__(self, parent)
        self.general = GeneralSettingsPanel(self.notebook)
        self.html = HtmlSettingsPanel(self.notebook)
        self.extra = ExtraFieldsPanel(self.notebook, extra_data_func)
        self.notebook.AddPage(self.general, "General")
        self.notebook.AddPage(self.html, "Html defaults")
        self.notebook.AddPage(self.extra, "Extra fields")
        self.html.OnBoardRotationSlider(None)

    def OnExit(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnSaveSettings(self, event):
        # TODO: implement OnSaveSettings
        pass

    def OnGenerateBom(self, event):
        self.GetParent().EndModal(wx.ID_OK)


# Implementing HtmlSettingsPanelBase
class HtmlSettingsPanel(dialog_base.HtmlSettingsPanelBase):
    def __init__(self, parent):
        dialog_base.HtmlSettingsPanelBase.__init__(self, parent)

    # Handlers for HtmlSettingsPanelBase events.
    def OnBoardRotationSlider(self, event):
        degrees = self.boardRotationSlider.Value * 5
        self.rotationDegreeLabel.LabelText = u"{}\u00B0".format(degrees)


# Implementing GeneralSettingsPanelBase
class GeneralSettingsPanel(dialog_base.GeneralSettingsPanelBase):
    def __init__(self, parent):
        dialog_base.GeneralSettingsPanelBase.__init__(self, parent)

    # Handlers for GeneralSettingsPanelBase events.
    def OnComponentSortOrderUp(self, event):
        selection = self.componentSortOrderBox.Selection
        if selection != wx.NOT_FOUND and selection > 0:
            item = self.componentSortOrderBox.GetString(selection)
            self.componentSortOrderBox.Delete(selection)
            self.componentSortOrderBox.Insert(item, selection - 1)
            self.componentSortOrderBox.SetSelection(selection - 1)

    def OnComponentSortOrderDown(self, event):
        selection = self.componentSortOrderBox.Selection
        size = self.componentSortOrderBox.Count
        if selection != wx.NOT_FOUND and selection < size - 1:
            item = self.componentSortOrderBox.GetString(selection)
            self.componentSortOrderBox.Delete(selection)
            self.componentSortOrderBox.Insert(item, selection + 1)
            self.componentSortOrderBox.SetSelection(selection + 1)

    def OnComponentSortOrderAdd(self, event):
        item = wx.GetTextFromUser(
                "Characters except for A-Z will be ignored.",
                "Add sort order item")
        item = re.sub('[^A-Z]', '', item.upper())
        if item == '':
            return
        found = self.componentSortOrderBox.FindString(item)
        if found != wx.NOT_FOUND:
            self.componentSortOrderBox.SetSelection(found)
            return
        self.componentSortOrderBox.Append(item)
        self.componentSortOrderBox.SetSelection(
                self.componentSortOrderBox.Count - 1)

    def OnComponentSortOrderRemove(self, event):
        selection = self.componentSortOrderBox.Selection
        if selection != wx.NOT_FOUND:
            item = self.componentSortOrderBox.GetString(selection)
            if item == '~':
                pop_error("You can not delete '~' item")
                return
            self.componentSortOrderBox.Delete(selection)
            if self.componentSortOrderBox.Count > 0:
                self.componentSortOrderBox.SetSelection(max(selection - 1, 0))

    def OnComponentBlacklistAdd(self, event):
        item = wx.GetTextFromUser(
                "Characters except for A-Z 0-9 and * will be ignored.",
                "Add blacklist item")
        item = re.sub('[^A-Z0-9*]', '', item.upper())
        if item == '':
            return
        found = self.blacklistBox.FindString(item)
        if found != wx.NOT_FOUND:
            self.blacklistBox.SetSelection(found)
            return
        self.blacklistBox.Append(item)
        self.blacklistBox.SetSelection(
                self.blacklistBox.Count - 1)

    def OnComponentBlacklistRemove(self, event):
        selection = self.blacklistBox.Selection
        if selection != wx.NOT_FOUND:
            self.blacklistBox.Delete(selection)
            if self.blacklistBox.Count > 0:
                self.blacklistBox.SetSelection(max(selection - 1, 0))


# Implementing ExtraFieldsPanelBase
class ExtraFieldsPanel(dialog_base.ExtraFieldsPanelBase):
    NONE_STRING = '<none>'

    def __init__(self, parent, extra_data_func):
        dialog_base.ExtraFieldsPanelBase.__init__(self, parent)
        self.extra_data_func = extra_data_func
        self.extra_field_data = None

    # Handlers for ExtraFieldsPanelBase events.
    def OnExtraFieldsUp(self, event):
        selection = self.extraFieldsList.Selection
        if selection != wx.NOT_FOUND and selection > 0:
            item = self.extraFieldsList.GetString(selection)
            checked = self.extraFieldsList.IsChecked(selection)
            self.extraFieldsList.Delete(selection)
            self.extraFieldsList.Insert(item, selection - 1)
            if checked:
                self.extraFieldsList.Check(selection - 1)
            self.extraFieldsList.SetSelection(selection - 1)

    def OnExtraFieldsDown(self, event):
        selection = self.extraFieldsList.Selection
        size = self.extraFieldsList.Count
        if selection != wx.NOT_FOUND and selection < size - 1:
            item = self.extraFieldsList.GetString(selection)
            checked = self.extraFieldsList.IsChecked(selection)
            self.extraFieldsList.Delete(selection)
            self.extraFieldsList.Insert(item, selection + 1)
            if checked:
                self.extraFieldsList.Check(selection + 1)
            self.extraFieldsList.SetSelection(selection + 1)

    def OnNetlistFileChanged(self, event):
        netlist_file = self.netlistFilePicker.Path
        if not os.path.isfile(netlist_file):
            return
        self.extra_field_data = self.extra_data_func(netlist_file)
        if self.extra_field_data is not None:
            field_list = list(self.extra_field_data[0])
            self.extraFieldsList.SetItems(field_list)
            field_list.append(self.NONE_STRING)
            self.boardVariantFieldBox.SetItems(field_list)
            self.boardVariantFieldBox.SetStringSelection(self.NONE_STRING)
            self.boardVariantWhitelist.Clear()
            self.boardVariantBlacklist.Clear()
            self.dnpFieldBox.SetItems(field_list)
            self.dnpFieldBox.SetStringSelection(self.NONE_STRING)

    def OnBoardVariantFieldChange(self, event):
        selection = self.boardVariantFieldBox.Value
        if not selection or selection == self.NONE_STRING \
                or self.extra_field_data is None:
            self.boardVariantWhitelist.Clear()
            self.boardVariantBlacklist.Clear()
            return
        variant_set = set()
        for _, field_dict in self.extra_field_data[1].items():
            if selection in field_dict:
                variant_set.add(field_dict[selection])
        self.boardVariantWhitelist.SetItems(list(variant_set))
        self.boardVariantBlacklist.SetItems(list(variant_set))
