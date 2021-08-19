
class MyDummy:

    def first(self, input_arg):
        return input_arg


class TestMyDummy():

    def setUp(self):
        self.obj = MyDummy()

    def test_first(self):
        assert (self.obj.first(5), 5)
        assert (self.obj.first(6), 6)


