import subprocess
import json
import os
import wx

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Test FileChooser", size=(300, 200))
        panel = wx.Panel(self)
        button = wx.Button(panel, label="Choisir un fichier", pos=(50, 50))
        button.Bind(wx.EVT_BUTTON, self.on_choose_file)

    def on_choose_file(self, event):
        worker_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "filechooser_worker.py")
        result = subprocess.check_output(["python", worker_path, "openfile"], text=True)
        path = json.loads(result).get("path", "")
        wx.MessageBox(f"Fichier choisi : {path}", "Résultat")

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
