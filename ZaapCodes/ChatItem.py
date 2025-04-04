
class ChatItem:
    text = None
    item_type = None
    
    def __init__(self, text : str="", item_type : str=""):
        self.text=text
        self.item_type=item_type