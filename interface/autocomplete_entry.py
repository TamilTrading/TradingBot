
import tkinter as tk

class AutoComplete(tk.Entry):

    def __init__(self, symbols, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._symbols = symbols

        self._lb = tk.Listbox
        self._lb_open = False

        # Binding command when pressed arrow keys
        self.bind('<Up>', self._up_down_arrow_event)
        self.bind('<Down>', self._up_down_arrow_event)
        self.bind('<Right>', self._right_arrow_event)

        self._var = tk.StringVar()
        self.configure(textvariable=self._var)
        self._var.trace('w', self._changed)

    def _changed(self, var_name, index, mode):
        entry_val = self._var.get().upper()
        self._var.set(entry_val)

        if self._var.get() == '':
            if self._lb_open:
                self._lb.destroy()
                self._lb_open = False
        else:
            if not self._lb_open:
                self._lb = tk.Listbox(height=8)
                self._lb.place(x=self.winfo_x() + self.winfo_width(), 
                                y=self.winfo_y() + self.winfo_height())
                self._lb_open = True
            
            # Inserting the matched symbol in listbox
            match_symbol = [symbol for symbol in self._symbols if symbol.startswith(entry_val)]
            if match_symbol:
                
                # Deleting the listbox variable before filling
                try:
                    self._lb.delete(0, tk.END)
                except tk.TclError:
                    pass

                for symbol in match_symbol[:8]:
                    self._lb.insert(tk.END, symbol)
            
            else:
                if self._lb_open:
                    self._lb.destroy()
                    self._lb_open = False 
    
    def _up_down_arrow_event(self, event):
        if self._lb_open:
            if self._lb.curselection() == ():
                index = -1
            else:
                index = self._lb.curselection()[0]

            lb_size = self._lb.size()
            if event.keysym == 'Up' and index > 0:
                self._lb.select_clear(first=index)
                index -= 1
                self._lb.selection_set(first=str(index))
                self._lb.activate(index)
            elif event.keysym == 'Down' and index < (lb_size - 1):
                self._lb.select_clear(first=index)
                index += 1
                self._lb.selection_set(first=str(index))
                self._lb.activate(index)

    def _right_arrow_event(self, event):

        if self._lb_open:
            self._var.set(self._lb.get(tk.ACTIVE))
            self._lb.destroy()
            self._lb_open = False
            self.icursor(tk.END)


