import nougat


class TestConfig:

    def test_load_from_object(self):

        app = nougat.Nougat()

        class BasicConfig:

            UPPER_VAR = 'hello'
            lower_var = 'world'

        app.config.load_from_object(BasicConfig)

        assert app.config.UPPER_VAR == 'hello'
        assert app.config.lower_var is None

    def test_patch_config(self):

        app = nougat.Nougat()

        app.config.HELLO = 'world'

        assert app.config.HELLO == 'world'
