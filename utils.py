
class CheckEntryData:

    integers = '0123456789'
    floats = integers + '.'

    def check_integer(self, inp_str):
        if not inp_str:
            return True

        if all(x in self.integers for x  in inp_str):
            try:
                int(inp_str)
                return True
            except ValueError:
                return True
        else:
            return False

    def check_float(self, inp_str):
        if not inp_str:
            return True

        if all(x in self.floats for x  in inp_str) and inp_str.count(".") <= 1:
            try:
                float(inp_str)
                return True
            except ValueError:
                return True
        else:
            return False
