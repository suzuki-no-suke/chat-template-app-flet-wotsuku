import flet as ft

from datetime import datetime, timedelta

import src.data.chat_history as chat_hist

class SingleChatMessageView(ft.UserControl):
    """単一チャット送信・受信メッセージの表示
    """
    def __init__(self, role, message, is_right=True, msg_time=datetime.now()):
        self.role = role
        self.message = message
        self.is_right = is_right
        self.msg_time = msg_time

        self.gui_row = ft.Row()
        self.gui_icon = None
        self.gui_text = None

        super().__init__()

    def _decide_icon(self, role):
        icondata = ft.Icon(name=ft.icons.QUESTION_MARK)
        if role == "user":
            icondata = ft.Icon(name=ft.icons.PERSON)
        elif role == "assistant":
            icondata = ft.Icon(name=ft.icons.CHAT_ROUNDED)
        elif role == "system":
            icondata = ft.Icon(name=ft.icons.HANDYMAN)
            
        return icondata

    def _decide_time_message(self, time):
        nowtime = datetime.now()
        timestr = "-/-/- -:-:-"

        # time differ than 24 hours -> date and time
        if time - nowtime > timedelta(hours=24):
            timestr = time.strftime("%Y-%m-%d %H:%M")
        # time differ less than 24 hours -> time only
        elif time - nowtime < timedelta(hours=24):
            timestr = time.strftime("%H:%M:%S")
        return timestr

    def _decide_is_right(self, role):
        is_right = False
        if role == "user":
            is_right = True
        return is_right

    def build(self):
        time_text = self._decide_time_message(self.msg_time)
        role_text = self.role
        self.gui_icon = self._decide_icon(self.role)

        self.gui_text = ft.TextField(
            label=f"{role_text} - {time_text}",
            value=self.message,
            read_only=True,
            multiline=True)

        if self.is_right:
            self.gui_row.controls.append(self.gui_text)
            self.gui_row.controls.append(self.gui_icon)
        else:
            self.gui_row.controls.append(self.gui_icon)
            self.gui_row.controls.append(self.gui_text)

        return self.gui_row

    def apply_chat_data(self, chatdata : chat_hist.ChatSingleMessage):
        self.role = chatdata.role
        self.message = chatdata.message
        self.is_right = self._decide_is_right(self.role)
        self.msg_time = chatdata.time

        # rebuild GUIs
        time_text = self._decide_time_message(self.msg_time)
        role_text = self.role

        self.gui_icon = self._decide_icon(self.role)
        self.gui_text.label = f"{role_text} - {time_text}"
        self.gui_text.value = self.message

        self.gui_row.controls.clear()
        if self.is_right:
            self.gui_row.controls.append(self.gui_text)
            self.gui_row.controls.append(self.gui_icon)
        else:
            self.gui_row.controls.append(self.gui_icon)
            self.gui_row.controls.append(self.gui_text)

    def gether_chat_data(self):
        data = chat_hist.ChatSingleMessage()

        data.role = self.role
        data.message = self.message
        data.time = self.msg_time

        return data


class ChatHistoryView(ft.UserControl):
    """
    チャット履歴の表示と保存
    """
    def __init__(self):
        self.history_id = None
        self.chatdisp = ft.Column([])

        self.rightside = ["user"]
        super().__init__()

    def build(self):
        return self.chatdisp

    def clear(self):
        self.history_id = None
        self.chatdisp.control.clear()

    def _is_right_check(self, role):
        return  (role in self.rightside)

    def add_chat(self, role, message):
        addtime = datetime.now()

        single_msg = SingleChatMessageView(role, message, self._is_right_check(role), addtime)
        self.chatdisp.controls.append(single_msg)

        # NOTE : need each view update - update message does not distribute
        self.chatdisp.update()

        return single_msg

    def gether_chat_history(self) -> list[chat_hist.ChatSingleMessage]:
        """chat history returns by list of  ChatSingleMessage"""
        datalist = []
        for c in self.chatdisp.controls:
            if isinstance(c, SingleChatMessageView):
                datalist.append(c.gether_chat_data())
        return datalist
    
    def _gen_chatmessage(self, chatdata : chat_hist.ChatSingleMessage):
        return SingleChatMessageView(
            chatdata.role,
            chatdata.message,
            self._is_right_check(chatdata.role),
            chatdata.time)

    def apply_chat_history(self, chat_list : list, history_id : str | None = None) -> None:
        self.clear()
        self.history_id = history_id

        for c in chat_list:
            chat_view = self._gen_chatmessage(c)
            self.chatdisp.controls.append(chat_view)
